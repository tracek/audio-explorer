#     Copyright 2019 Lukasz Tracewski
#
#     Licensed under the Apache License, Version 2.0 (the "License");
#     you may not use this file except in compliance with the License.
#     You may obtain a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#     Unless required by applicable law or agreed to in writing, software
#     distributed under the License is distributed on an "AS IS" BASIS,
#     WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#     See the License for the specific language governing permissions and
#     limitations under the License.

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


class EmbeddingFailed(Exception):
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
            Parallel(n_jobs=n_jobs, backend='loky')(delayed(fit_and_save)(
                data=data, output_dir=output_dir, type=type, n_jobs=1, kwargs=params) for params in param_grid)
    else:
        fit_and_save(data=data, output_dir=output_dir, n_jobs=n_jobs)


def fit_and_save(data: Union[np.ndarray, pd.DataFrame], output_dir: str, type: str='umap', n_jobs=1, **kwargs):
    params_string = '-'.join(['{}_{}'.format(k, v) for k, v in kwargs.items()])
    logging.info(f'Running {type} with {params_string}')
    embedding = get_embeddings(data=data, type=type, n_jobs=n_jobs, **kwargs)
    output_path = os.path.join(output_dir, type + '_' + params_string + '.joblib')
    joblib.dump(embedding, filename=output_path)


def load_and_transform(data: np.ndarray, name: str) -> np.ndarray:
    d = joblib.load(name)
    scaler = d['scaler']
    model = d['model']
    data = scaler.transform(data)
    embedding = model.transform(data)
    return embedding


def get_embeddings(data: Union[np.ndarray, pd.DataFrame] , type: str='umap', n_jobs: int=1, **kwargs) -> np.ndarray:
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
        raise EmbeddingFailed(f'The input data consisted of {data.shape[0]} points, which is too few for meaningful '
                              f'embedding.')
    data = StandardScaler().fit_transform(data)
    type = type.lower()
    random_state = 42
    if type == 'umap':
        # somehow pydev debugger gets very slow upon loading of UMAP
        # moving umap here for the time being
        import umap
        n_neighbors = 50
        if data.shape[0] < n_neighbors:
            raise EmbeddingFailed(f'The input data consisted of {data.shape[0]} points. Reduce clustering strength to '
                                  f'at most {data.shape[0] - 1}')
        algo = umap.UMAP(n_components=2, transform_seed=random_state, n_neighbors=n_neighbors, **kwargs)
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
    return embedding


