import aubio
import numpy as np
import pandas as pd
import scipy.stats as stats


def get_pitch_stats(signal: np.ndarray, fs: int, block_size: int, hop: int, tolerance: float = 0.6) -> dict:
    """
    Get basic statistic on pitch in the given signal
    :param signal: 1-d signal
    :param fs: sampling frequency
    :param block_size: window size
    :param hop: size of a hop between frames
    :param tolerance:  tolerance for the pitch detection algorithm (for aubio)
    :return:
    """
    pitch_o = aubio.pitch("yin", block_size, hop, fs)
    pitch_o.set_unit('Hz')
    pitch_o.set_tolerance(tolerance)
    signal_win = np.array_split(signal, np.arange(hop, len(signal), hop))

    pitch = []
    for frame in signal_win:
        pitch = pitch_o(frame)[0]
        confidence = pitch_o.get_confidence()
        if confidence > tolerance:
            pitch.append(pitch)

    if pitch:
        pitch = np.array(pitch)
        Q25, Q50, Q75 = np.quantile(pitch, [0.25, 0.5, 0.75])
        IQR = Q75 - Q25
        skew = stats.skew(pitch)
        kurt = stats.kurtosis(pitch)
        median = np.median(pitch)
        mode = stats.mode(pitch)
        sd = np.std(pitch)
    else:
        Q25 = 0
        Q50 = 0
        Q75 = 0
        sd = 0
        median = 0
        mode = 0
        IQR = 0
        skew = 0
        kurt = 0

    pitchstats = {
        'pitch_mean': Q50,
        'pitch_sd': sd,
        'pitch_median': median,
        'pitch_mode': mode,
        'pitch_Q25': Q25,
        'pitch_Q75': Q75,
        'pitch_IQR': IQR,
        'pitch_skew': skew,
        'pitch_kurt': kurt
    }

    return pitchstats


def get_pitch_stats_series(signal: np.ndarray, fs: int, block_size: int, hop: int, tolerance: float = 0.6) -> pd.Series:
    """
    Get basic statistic on pitch in the given signal
    :param signal: 1-d signal
    :param fs: sampling frequency
    :param block_size: window size
    :param hop: size of a hop between frames
    :param tolerance:  tolerance for the pitch detection algorithm (for aubio)
    :return:
    """
    pitchstats = get_pitch_stats(signal, fs, block_size, hop, tolerance)
    return pd.Series(pitchstats)

