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
from typing import Optional
from scipy.signal import butter, lfilter


def _butter_highpass(cutoff, fs, order=6):
    nyq = 0.5 * fs
    high = cutoff / nyq
    b, a = butter(order, high, btype='highpass')
    return b, a

def _butter_lowpass(cutoff, fs, order=6):
    nyq = 0.5 * fs
    low = cutoff / nyq
    b, a = butter(order, low, btype='lowpass')
    return b, a


def _butter_bandpass(lowcut, highcut, fs, order=6):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = butter(order, [low, high], btype='band')
    return b, a


def frequency_filter(signal: np.ndarray, fs: int, lowcut: Optional[int], highcut: Optional[int], order=6) -> np.ndarray:
    """
    Custom bandpass filter
    :param signal: single-channel signal
    :param fs: sampling rate [Hz]
    :param lowcut: cut everything below this frequency [Hz]
    :param highcut: cut everything above this frequency [Hz]
    :param order: order of the Butterworth filter
    :return:
    """
    if lowcut and highcut:
        b, a = _butter_bandpass(lowcut, highcut, fs, order)
    elif lowcut and not highcut:
        b, a = _butter_highpass(lowcut, fs, order)
    elif highcut and not lowcut:
        b, a = _butter_lowpass(highcut, fs, order)
    else:
        return signal
    y = lfilter(b, a, signal).astype('float32')
    return y
