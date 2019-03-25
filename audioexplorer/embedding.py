import numpy as np
import joblib
from multiprocessing import cpu_count
from MulticoreTSNE import MulticoreTSNE
from sklearn.preprocessing import StandardScaler
from sklearn.manifold import TSNE


def fit_and_dump(data: np.ndarray, embedding: str, name: str, **kwargs):
    embedding = embedding.lower()
    scaler = StandardScaler()
    data = scaler.fit_transform(data)

    if embedding == 'tsne':
        perplexity = kwargs.get('perplexity', 60)
        n_iter_without_progress = kwargs.get('n_iter_without_progress', 50)
        algo = MulticoreTSNE(perplexity=perplexity,
                             n_iter_without_progress=n_iter_without_progress,
                             n_jobs=cpu_count())
    elif embedding == 'umap':
        import umap
        n_neighbors = kwargs.get('n_neighbors', 10)
        min_dist = kwargs.get('min_dist', 0.1)
        metric = kwargs.get('metric', 'euclidean')
        algo = umap.UMAP(n_neighbors=n_neighbors, min_dist=min_dist, metric=metric, init='random')
    else:
        raise NotImplemented(f'Requested embedding type {embedding} is not implemented')

    fit = algo.fit(data)
    joblib.dump({'scaler': scaler, 'model': fit}, filename=f'{name}.joblib')


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


