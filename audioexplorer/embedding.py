import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn import manifold
from sklearn import decomposition


def get_embeddings(data: np.ndarray, type='tsne', **kwargs) -> np.ndarray:
    data = StandardScaler().fit_transform(data)
    if type == 'tsne':
        perplexity = kwargs.get('perplexity', 80)
        algo = manifold.TSNE(n_components=2, perplexity=perplexity)
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

