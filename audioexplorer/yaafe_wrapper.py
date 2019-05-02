#      Copyright (c) 2019  Lukasz Tracewski
#
#      This file is part of Audio Explorer.
#
#      Audio Explorer is free software: you can redistribute it and/or modify
#      it under the terms of the GNU General Public License as published by
#      the Free Software Foundation, either version 3 of the License, or
#      (at your option) any later version.
#
#      Foobar is distributed in the hope that it will be useful,
#      but WITHOUT ANY WARRANTY; without even the implied warranty of
#      MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#      GNU General Public License for more details.
#
#      You should have received a copy of the GNU General Public License
#      along with Audio Explorer.  If not, see <https://www.gnu.org/licenses/>.

import numpy as np
import pandas as pd
import yaafelib


YAAFE_FEATURES = \
    {'Chroma': 'Chroma',
     'LPC': 'LPC',
     'LSF': 'LSF',
     'MFCC': 'MFCC',
     'OBSI': 'OBSI',
     'SpectralCrestFactorPerBand': 'Crest factors',
     'SpectralFlatness': 'Flatness',
     'SpectralFlux': 'Flux',
     'SpectralRolloff': 'Rolloff',
     'SpectralVariation': 'Variation'}

class YaafeWrapper(object):

    def __init__(self, fs: int, block_size=1024, step_size=None, selected_features='all'):
        if not step_size:
            step_size = block_size // 2

        features_config = {
            'Chroma': f'Chroma2 CQTAlign=c  CQTBinsPerOctave=48  CQTMinFreq=27.5  CQTNbOctaves=7  CZBinsPerSemitone=1  CZNbCQTBinsAggregatedToPCPBin=-1  CZTuning=440  stepSize={step_size}',
            'LPC': f'LPC LPCNbCoeffs=1  blockSize={block_size}  stepSize={step_size}',
            'LSF': f'LSF blockSize={block_size}  stepSize={step_size}',
            'MFCC': f'MFCC CepsIgnoreFirstCoeff=1  CepsNbCoeffs=13  FFTWindow=Hanning  MelMaxFreq=6000.0  MelMinFreq=400.0  MelNbFilters=40  blockSize={block_size}  stepSize={step_size}',
            'OBSI': f'OBSI FFTLength=0  FFTWindow=Hanning  OBSIMinFreq=27.5  blockSize={block_size}  stepSize={step_size}',
            'SpectralCrestFactorPerBand': f'SpectralCrestFactorPerBand FFTLength=0  FFTWindow=Hanning  blockSize={block_size}  stepSize={step_size}',
            'SpectralDecrease': f'SpectralDecrease FFTLength=0  FFTWindow=Hanning  blockSize={block_size}  stepSize={step_size}',
            'SpectralFlatness': f'SpectralFlatness FFTLength=0  FFTWindow=Hanning  blockSize={block_size}  stepSize={step_size}',
            'SpectralFlux': f'SpectralFlux FFTLength=0  FFTWindow=Hanning  FluxSupport=All  blockSize={block_size}  stepSize={step_size}',
            'SpectralRolloff': f'SpectralRolloff FFTLength=0  FFTWindow=Hanning  blockSize={block_size}  stepSize={step_size}',
            'SpectralVariation': f'SpectralVariation FFTLength=0  FFTWindow=Hanning  blockSize={block_size}  stepSize={step_size}',
            'ZCR': f'ZCR blockSize={block_size}  stepSize={step_size}'
        }

        self.fs = fs
        if selected_features == 'all':
            selected_features = features_config.keys()
        feature_plan = yaafelib.FeaturePlan(sample_rate=fs, normalize=True)
        for feature_name, setting in features_config.items():
            if feature_name in selected_features:
                feature_plan.addFeature(feature_name + ': ' + setting)
        data_flow = feature_plan.getDataFlow()
        self.engine = yaafelib.Engine()
        self.engine.load(data_flow)

    def get_features(self, audio_data: np.ndarray) -> dict:
        features = self.engine.processAudio(audio_data.reshape(1, -1).astype('float64'))
        return features

    def get_mean_features(self, audio_data: np.ndarray) -> dict:
        features = self.engine.processAudio(audio_data.reshape(1, -1).astype('float64'))

        flat_dict = {}
        prefix = 'yaafe'
        for name, values in features.items():
            if values.shape[1] == 1:
                flat_dict[f'{prefix}_{name}'] = values.mean()
            else:
                d = {f'{prefix}_{name}.{idx}': value for idx, value in enumerate(list(values.mean(axis=0)))}
                flat_dict.update(d)
        return flat_dict

    def get_mean_features_as_series(self, audio_data: np.ndarray) -> pd.Series:
        flat_dict = self.get_mean_features(audio_data)
        return pd.Series(flat_dict)




