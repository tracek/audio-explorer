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
from aubio import onset


class OnsetDetector(object):

    def __init__(self, fs,
                 nfft: int = 512,
                 hop: int = 256,
                 onset_detector_type: str = 'hfc',
                 onset_threshold: float = 0.01,
                 onset_silence_threshold: float = -90,
                 min_duration_s: float = 0.15):
        self.hop = hop
        self.onset_detector = onset(onset_detector_type, nfft, hop, fs)
        if onset_threshold:
            self.onset_detector.set_threshold(onset_threshold)
        if onset_silence_threshold:
            self.onset_detector.set_silence(onset_silence_threshold)
        if min_duration_s:
            self.onset_detector.set_minioi_s(min_duration_s)

    def get(self, frame):
        if self.onset_detector(frame):
            return self.onset_detector.get_last_s()

    def get_all(self, signal):
        signal_windowed = np.array_split(signal.astype('float32'), np.arange(self.hop, len(signal), self.hop))
        onsets = []
        for frame in signal_windowed[:-1]:
            if frame.any():
                if self.onset_detector(frame):
                    onsets.append(self.onset_detector.get_last_s())
        return np.array(onsets[1:])



def get_onsets(signal, fs, nfft, hop, onset_detector_type, onset_threshold=None,
               onset_silence_threshold=None, min_duration_s=None):
    onsets = []

    onset_detector = onset(onset_detector_type, nfft, hop, fs)
    if onset_threshold:
        onset_detector.set_threshold(onset_threshold)
    if onset_silence_threshold:
        onset_detector.set_silence(onset_silence_threshold)
    if min_duration_s:
        onset_detector.set_minioi_s(min_duration_s)

    signal_windowed = np.array_split(signal, np.arange(hop, len(signal), hop))

    for frame in signal_windowed[:-1]:
        if onset_detector(frame):
            onsets.append(onset_detector.get_last_s())

    return np.array(onsets[1:])
