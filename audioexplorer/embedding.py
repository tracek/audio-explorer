import os
import json
import logging
import numpy as np
import joblib
from joblib import Parallel, delayed
from sklearn.model_selection import ParameterGrid
from sklearn.preprocessing import StandardScaler
from sklearn.manifold import TSNE


def fit_and_dump(data: np.ndarray, embedding_type: str, output_path: str, n_jobs: int=-1, grid_path: str=None):
    embedding_type = embedding_type.lower()
    scaler = StandardScaler()
    data = scaler.fit_transform(data)
    os.makedirs(output_path, exist_ok=True)
    joblib.dump(scaler, filename=os.path.join(output_path, 'scaler.joblib'))

    if grid_path:
        with open(grid_path) as config_file:
            grid_dict = json.load(config_file)
        param_grid = ParameterGrid(grid_dict)
        if n_jobs == -1:
            n_jobs = len(param_grid)
        Parallel(n_jobs=n_jobs, backend='multiprocessing')(delayed(fit_and_save)(
            data=data, output_dir=output_path, embedding_type=embedding_type, params=params) for params in param_grid)
    else:
        fit_and_save(data=data, embedding_type=embedding_type, params={})


def fit_and_save(embedding_type, output_dir, data, params):
    params_string = '-'.join(['{}_{}'.format(k, v) for k, v in params.items()])
    logging.info(f'Running {embedding_type} with {params_string}')
    if embedding_type == 'tsne':
        algo = TSNE(**params)
    elif embedding_type == 'umap':
        import umap
        algo = umap.UMAP(**params)
    else:
        raise NotImplemented(f'Requested embedding type {embedding_type} is not implemented')

    fit = algo.fit(data)
    output_path = os.path.join(output_dir, embedding_type + '_' + params_string + '.joblib')
    joblib.dump(fit, filename=output_path)


def load_and_transform(data: np.ndarray, name: str) -> np.ndarray:
    d = joblib.load(name)
    scaler = d['scaler']
    model = d['model']
    data = scaler.transform(data)
    embedding = model.transform(data)
    return embedding


def get_embeddings(data, type='tsne', **kwargs) -> np.ndarray:
    data = StandardScaler().fit_transform(data)
    if type == 'tsne':
        perplexity = kwargs.get('perplexity', 80)
        algo = TSNE(n_components=2, perplexity=perplexity)
    elif type == 'umap':
        # somehow pydev debugger gets very slow upon loading of UMAP
        # moving umap here for the time being
        import umap
        n_neighbors = kwargs.get('n_neighbors', 10)
        min_dist = kwargs.get('min_dist', 0.1)
        metric = kwargs.get('metric', 'euclidean')
        algo = umap.UMAP(n_neighbors=n_neighbors, min_dist=min_dist, metric=metric, init='random')
    else:
        raise NotImplemented(f'Requested type {type} is not implemented')

    embedding = algo.fit_transform(data)
    return embedding


