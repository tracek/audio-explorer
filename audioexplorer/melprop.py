import numpy as np
import pandas as pd
import librosa

def mel_frequency_cepstral_coefficients(y: np.ndarray, fs: int, n_mfcc=13, block_size=512, step_size=128, fmin=300, fmax=6000):
    """
    Compute mel-frequency cepstral coefficients https://en.wikipedia.org/wiki/Mel-frequency_cepstrum and its first
    and second derivatives. First coefficient will be ignored.

    :param y: 1-d signsl
    :param fs: sampling frequency [Hz]
    :param n_mfcc: number of coefficients to extract
    :param block_size: length of the FFT window
    :param step_size: number of samples between successive frames
    :param fmin: lowest frequency [Hz]
    :param fmax: highest frequency [Hz]. If None, use fmax = sr / 2.0
    :return: MFCCs
    """
    mfcc = librosa.feature.mfcc(y=y, sr=fs, n_mfcc=n_mfcc + 1, fmin=fmin, fmax=fmax, n_fft=block_size, hop_length=step_size)[1:]
    delta_mfcc = librosa.feature.delta(mfcc, mode='nearest')
    delta2_mfcc = librosa.feature.delta(mfcc, order=2, mode='nearest')
    feature_vector = np.concatenate((np.mean(mfcc, 1), np.mean(delta_mfcc, 1), np.mean(delta2_mfcc, 1)))

    mfcc_names = [f'mfcc_d0.{idx}' for idx in range(1, n_mfcc + 1)]
    mfcc_delta_names = [f'mfcc_d1.{idx}' for idx in range(1, n_mfcc + 1)]
    mfcc_delta2_names = [f'mfcc_d2.{idx}' for idx in range(1, n_mfcc + 1)]

    # feature_vector = (feature_vector-np.mean(feature_vector)) / np.std(feature_vector)
    feature_vector = pd.Series(data=feature_vector, index=mfcc_names+mfcc_delta_names+mfcc_delta2_names)
    return feature_vector