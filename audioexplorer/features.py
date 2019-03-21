import numpy as np
import pandas as pd
from joblib import Parallel, delayed
from audioexplorer import specprop
from audioexplorer.onsets import OnsetDetector
from audioexplorer.filters import frequency_filter
from audioexplorer.yaafe_wrapper import YaafeWrapper


class FeatureExtractor(object):

    def __init__(self, fs: int, block_size: int=512, step_size: int=None):

        self.fs = fs
        self.block_size = block_size
        self.yaafe = YaafeWrapper(fs, block_size, step_size)
        if not step_size:
            self.step_size = block_size // 2

    def get_features(self, sample: np.ndarray) -> pd.DataFrame:
        spectral_props = specprop.spectral_statistics_series(sample, self.fs, 700)
        mfccs = specprop.mel_frequency_cepstral_coefficients(sample, self.fs, block_size=self.block_size, step_size=self.step_size)
        yaafe = self.yaafe.get_mean_features_as_series(sample)
        r = pd.concat([spectral_props, mfccs, yaafe])
        return r


def _extract_features(samples: np.ndarray, fs: int):
    extractor = FeatureExtractor(fs)
    features = []
    for sample in samples:
        f = extractor.get_features(sample)
        features.append(f)
    return pd.DataFrame(features)


def _split_audio_into_chunks_by_onsets(X: np.ndarray, fs: int, onsets: np.ndarray, sample_len: float, split: int) -> np.ndarray:
    samples = []
    for onset in onsets:
        start = int(onset * fs)
        end = int((onset + sample_len) * fs)
        samples.append(X[start: end])
    samples = np.array(samples)
    if split > 1:
        samples = np.array_split(samples, split)
    return samples


def get(X, fs, n_jobs=1, **kwargs) -> pd.DataFrame:
    lowcut = int(kwargs.get('lowcut', 500))
    highcut = int(kwargs.get('highcut', 6000))
    block_size = int(kwargs.get('block_size', 512))
    step_size = int(kwargs.get('step_size', block_size // 2))
    onset_detector_type = kwargs.get('onset_detector_type', 'hfc')
    onset_threshold = float(kwargs.get('onset_threshold', 0.01))
    onset_silence_threshold = float(kwargs.get('onset_silence_threshold', -90))
    min_duration_s = float(kwargs.get('min_duration_s', 0.15))
    sample_len = float(kwargs.get('sample_len', 0.2))

    X = frequency_filter(X, fs, lowcut=lowcut, highcut=highcut)
    onset_detector = OnsetDetector(fs, nfft=block_size, hop=step_size,
                                   onset_detector_type=onset_detector_type,
                                   onset_threshold=onset_threshold, onset_silence_threshold=onset_silence_threshold,
                                   min_duration_s=min_duration_s)

    onsets = onset_detector.get_all(X)
    chunks = _split_audio_into_chunks_by_onsets(X, fs, onsets, sample_len, n_jobs)
    if n_jobs == 1:
        features = _extract_features(chunks, fs)
    else:
        features = Parallel(n_jobs=n_jobs, backend='multiprocessing')(
            delayed(_extract_features)(samples=chunk, fs=fs) for chunk in chunks)
        features = pd.concat(features)

    features.insert(0, column='offset', value=onsets + sample_len)
    features.insert(0, column='onset', value=onsets)
    features = features.reset_index(drop=True)
    return features

