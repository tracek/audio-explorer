import numpy as np
from aubio import onset


class OnsetDetector(object):

    def __init__(self, fs,
                 nfft: int = 512,
                 hop: int = 256,
                 onset_detector_type: str = 'hfc',
                 onset_threshold: float = 0.01,
                 onset_silence_threshold: int = -90,
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
        signal_windowed = np.array_split(signal, np.arange(self.hop, len(signal), self.hop))
        onsets = []
        for frame in signal_windowed[:-1]:
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
