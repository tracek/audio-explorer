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
