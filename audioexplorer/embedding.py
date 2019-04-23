import os
import json
import logging
import numpy as np
import pandas as pd
import joblib
from typing import Union
from joblib import Parallel, delayed
from sklearn.model_selection import ParameterGrid
from sklearn.preprocessing import StandardScaler
from sklearn.manifold import TSNE, Isomap, SpectralEmbedding, LocallyLinearEmbedding
from sklearn.decomposition import PCA, FactorAnalysis, KernelPCA, FastICA


EMBEDDINGS = {'umap': 'Uniform Manifold Approximation and Projection',
              'tsne': 't-Distributed Stochastic Neighbor Embedding',
              'isomap': 'Isometric Mapping',
              'spectral': 'Spectral embedding',
              'loclin': 'Locally Linear Embedding',
              'pca': 'Principal Component Analysis',
              'kpca': 'Kernel Principal Component Analysis',
              'fa': 'Factor Analysis',
              'ica': 'Independent Component Analysis'}


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
        Parallel(n_jobs=n_jobs, backend='loky')(delayed(fit_and_save)(
            data=data, output_dir=output_path, embedding_type=embedding_type, params=params) for params in param_grid)
    else:
        fit_and_save(data=data, output_dir=output_path, embedding_type=embedding_type, params={})


def fit_and_save(embedding_type, output_dir, data, params):
    params_string = '-'.join(['{}_{}'.format(k, v) for k, v in params.items()])
    logging.info(f'Running {embedding_type} with {params_string}')
    try:
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
    except Exception as ex:
        logging.exception(ex)
        raise


def load_and_transform(data: np.ndarray, name: str) -> np.ndarray:
    d = joblib.load(name)
    scaler = d['scaler']
    model = d['model']
    data = scaler.transform(data)
    embedding = model.transform(data)
    return embedding


def get_embeddings(data: Union[np.ndarray, pd.DataFrame] , type: str='umap', **kwargs) -> np.ndarray:
    """
    Following embedding types are available
     'umap': 'Uniform Manifold Approximation and Projection',
     'tsne': 't-Distributed Stochastic Neighbor Embedding',
     'pca': 'Principal Component Analysis',
     'kpca': 'Kernel Principal Component Analysis',
     'fa': 'Factor Analysis',
     'ica': 'Independent Component Analysis'
     'isomap': 'Isomap'
     'spectral': 'Spectral embedding',
     'loclin': 'Locally Linear Embedding',
    :param data: numpy 2d array compatible
    :param type: One of the following: 'umap', 'tsne', 'pca', 'kpca', 'fa', 'ica'
    :param kwargs: params to pass to the embedding algorithm
    :return:
    """
    data = StandardScaler().fit_transform(data)
    type = type.lower()
    random_state = 42
    if type == 'umap':
        # somehow pydev debugger gets very slow upon loading of UMAP
        # moving umap here for the time being
        import umap
        kwargs['n_neighbors'] = kwargs.get('n_neighbors', 10)
        kwargs['min_dist'] = kwargs.get('min_dist', 0.1)
        kwargs['metric'] = kwargs.get('metric', 'euclidean')
        algo = umap.UMAP(n_components=2, transform_seed=random_state, **kwargs)
    elif type == 'tsne':
        kwargs['perplexity'] = kwargs.get('perplexity', 50)
        algo = TSNE(n_components=2, init='pca', random_state=random_state, **kwargs)
    elif type == 'isomap':
        algo = Isomap()
    elif type == 'spectral':
        algo = SpectralEmbedding(random_state=random_state)
    elif type == 'loclin':
        algo = LocallyLinearEmbedding(random_state=random_state)
    elif type == 'pca':
        algo = PCA(n_components=2, random_state=random_state, **kwargs)
    elif type == 'fa':
        algo = FactorAnalysis(n_components=2, svd_method='lapack', random_state=random_state, **kwargs)
    elif type == 'kpca':
        kwargs['kernel'] = kwargs.get('kernel', 'cosine')
        algo = KernelPCA(n_components=2, random_state=random_state, **kwargs)
    elif type == 'ica':
        algo = FastICA(n_components=2, random_state=random_state)
    else:
        raise NotImplemented(f'Requested type {type} is not implemented')

    embedding = algo.fit_transform(data)
    return embedding


