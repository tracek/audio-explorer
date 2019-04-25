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

import numpy as np
import pandas as pd
from scipy import signal


def spectral_statistics(y: np.ndarray, fs: int, lowcut: int = 0) -> dict:
    """
    Compute selected statistical properties of spectrum

    :param y: 1-d signsl
    :param fs: sampling frequency [Hz]
    :param lowcut: lowest frequency [Hz]
    :return: spectral features (dict)
    """
    spec = np.abs(np.fft.rfft(y))
    freq = np.fft.rfftfreq(len(y), d=1 / fs)
    idx = int(lowcut / fs * len(freq) * 2)
    spec = np.abs(spec[idx:])
    freq = freq[idx:]

    amp = spec / spec.sum()
    mean = (freq * amp).sum()
    amp_cumsum = np.cumsum(amp)
    median = freq[len(amp_cumsum[amp_cumsum <= 0.5]) + 1]
    mode = freq[amp.argmax()]
    Q25 = freq[len(amp_cumsum[amp_cumsum <= 0.25]) + 1]
    Q75 = freq[len(amp_cumsum[amp_cumsum <= 0.75]) + 1]
    IQR = Q75 - Q25

    prefix = 'freq'
    top_peaks_ordered_by_power = {f'{prefix}_peak.1': 0, f'{prefix}_peak.2': 0, f'{prefix}_peak.3': 0}
    amp_smooth = signal.medfilt(amp, kernel_size=15)
    peaks, height_d = signal.find_peaks(amp_smooth, distance=100, height=0.002)
    if peaks.size != 0:
        peak_f = freq[peaks]
        idx_three_top_peaks = height_d['peak_heights'].argsort()[-3:][::-1]
        top_3_freq = peak_f[idx_three_top_peaks]
        for peak, peak_name in zip(top_3_freq, top_peaks_ordered_by_power.keys()):
            top_peaks_ordered_by_power[peak_name] = peak

    specprops = {
        f'{prefix}_mean': mean,
        f'{prefix}_median': median,
        f'{prefix}_mode': mode,
        f'{prefix}_Q25': Q25,
        f'{prefix}_Q75': Q75,
        f'{prefix}_IQR': IQR
    }
    specprops.update(top_peaks_ordered_by_power)
    return specprops


def spectral_statistics_series(y: np.ndarray, fs: int, lowcut: int = 0) -> pd.Series:
    """
    Compute selected statistical properties of spectrum

    :param y: 1-d signsl
    :param fs: sampling frequency [Hz]
    :param lowcut: lowest frequency [Hz]
    :return: spectral features (pandas Series)
    """
    spec = spectral_statistics(y, fs, lowcut)
    return pd.Series(spec)



