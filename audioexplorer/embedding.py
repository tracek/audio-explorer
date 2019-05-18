#      Copyright (c) 2019  Lukasz Tracewski
#
#      This file is part of Audio Explorer.
#
#      Audio Explorer is free software: you can redistribute it and/or modify
#      it under the terms of the GNU General Public License as published by
#      the Free Software Foundation, either version 3 of the License, or
#      (at your option) any later version.
#
#      Audio Explorer is distributed in the hope that it will be useful,
#      but WITHOUT ANY WARRANTY; without even the implied warranty of
#      MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#      GNU General Public License for more details.
#
#      You should have received a copy of the GNU General Public License
#      along with Audio Explorer.  If not, see <https://www.gnu.org/licenses/>.

import os
import json
import logging
import numpy as np
import pandas as pd
import joblib
from typing import Union
from joblib import Parallel, delayed, cpu_count
from sklearn.model_selection import ParameterGrid
from sklearn.preprocessing import StandardScaler
from sklearn.manifold import TSNE, Isomap, SpectralEmbedding, LocallyLinearEmbedding
from sklearn.decomposition import PCA, FactorAnalysis, KernelPCA, FastICA


class EmbeddingException(Exception):
    pass


EMBEDDINGS = {'umap': 'Uniform Manifold Approximation and Projection',
              'tsne': 't-Distributed Stochastic Neighbor Embedding',
              'isomap': 'Isometric Mapping',
              'spectral': 'Spectral embedding',
              'loclin': 'Locally Linear Embedding',
              'pca': 'Principal Component Analysis',
              'kpca': 'Kernel Principal Component Analysis',
              'fa': 'Factor Analysis',
              'ica': 'Independent Component Analysis'}


def fit_and_save_with_grid(data: Union[np.ndarray, pd.DataFrame], grid_path: str, type: str='umap', output_dir: str='.', n_jobs: int=-1):
    type = type.lower()
    scaler = StandardScaler()
    data = scaler.fit_transform(data)
    os.makedirs(output_dir, exist_ok=True)
    joblib.dump(scaler, filename=os.path.join(output_dir, 'scaler.joblib'))

    if grid_path:
        with open(grid_path) as config_file:
            grid_dict = json.load(config_file)
        param_grid = ParameterGrid(grid_dict)
        if (n_jobs == -1) and (len(param_grid) > cpu_count()):
            n_jobs = len(param_grid)
        if n_jobs == 1:
            for params in param_grid:
                fit_and_save(data=data, output_dir=output_dir, n_jobs=1, **params)
        else:
            Parallel(n_jobs=n_jobs, backend='multiprocessing')(delayed(fit_and_save)(
                data=data, output_dir=output_dir, type=type, n_jobs=1, **params) for params in param_grid)
    else:
        fit_and_save(data=data, output_dir=output_dir, n_jobs=n_jobs)


def fit_and_save(data: Union[np.ndarray, pd.DataFrame], output_dir: str, type: str='umap', n_jobs=1, **kwargs):
    params_string = '-'.join(['{}_{}'.format(k, v) for k, v in kwargs.items()])
    logging.info(f'Running {type} with {params_string}')
    embedding = get_embeddings(data=data, type=type, n_jobs=n_jobs, **kwargs)
    output_path = os.path.join(output_dir, type + '_' + params_string + '.joblib')
    logging.info(f'Model built successfully. Saving model to {output_path}...')
    joblib.dump(embedding, filename=output_path)


def load_and_transform(data: np.ndarray, name: str) -> np.ndarray:
    d = joblib.load(name)
    scaler = d['scaler']
    model = d['model']
    data = scaler.transform(data)
    embedding = model.transform(data)
    return embedding


def get_embeddings(data: Union[np.ndarray, pd.DataFrame] , type: str='umap', n_jobs: int=1, **kwargs) -> (np.ndarray, str):
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
    if data.shape[0] < 10:
        raise EmbeddingException(f'The input data consisted of {data.shape[0]} points, which is too few for meaningful '
                              f'embedding. Consider reducing onset detection threshold.')
    data = StandardScaler().fit_transform(data)
    type = type.lower()
    random_state = 42
    warning_msg = None
    if type == 'umap':
        # somehow pydev debugger gets very slow upon loading of UMAP
        # moving umap here for the time being
        import umap
        n_neighbors = kwargs.get('n_neighbors')
        if n_neighbors and data.shape[0] < n_neighbors:
            raise EmbeddingException(f'The input data consisted of {data.shape[0]} points. Reduce n_neighbors to '
                                     f'at most {data.shape[0] - 1}, preferably less than {data.shape[0] // 4}.')
        if n_neighbors and data.shape[0] < (4 * n_neighbors):
            warning_msg = f'Number of neighbours to consider ({n_neighbors}) is very large when compared to number of ' \
                f'data points ({data.shape[0]}). Consider lowering number of neighbours to less than 1/4th, e.g. ' \
                f'{data.shape[0] // 4 - 1}.'
            logging.warning(warning_msg)
        algo = umap.UMAP(n_components=2, transform_seed=random_state, **kwargs)
    elif type == 'tsne':
        kwargs['perplexity'] = kwargs.get('perplexity', 50)
        algo = TSNE(n_components=2, init='pca', random_state=random_state, **kwargs)
    elif type == 'isomap':
        algo = Isomap(n_components=2, n_jobs=n_jobs, **kwargs)
    elif type == 'spectral':
        algo = SpectralEmbedding(n_components=2, n_jobs=n_jobs, random_state=random_state, **kwargs)
    elif type == 'loclin':
        algo = LocallyLinearEmbedding(n_components=2, n_jobs=n_jobs, random_state=random_state)
    elif type == 'pca':
        algo = PCA(n_components=2, random_state=random_state, **kwargs)
    elif type == 'fa':
        algo = FactorAnalysis(n_components=2, svd_method='lapack', random_state=random_state, **kwargs)
    elif type == 'kpca':
        kwargs['kernel'] = kwargs.get('kernel', 'cosine')
        algo = KernelPCA(n_components=2, n_jobs=n_jobs, random_state=random_state, **kwargs)
    elif type == 'ica':
        algo = FastICA(n_components=2, random_state=random_state)
    else:
        raise NotImplemented(f'Requested type {type} is not implemented')

    embedding = algo.fit_transform(data)
    return embedding, warning_msg


