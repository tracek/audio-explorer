import os
import glob
import click
import librosa
import configparser
from audioexplorer.feature_extractor import get_features_from_ndarray


@click.command()
@click.option("--input", "-i", type=click.STRING, help="Path to audio.")
@click.option("--output", "-o", type=click.STRING, default='.', help="Output directory.")
@click.option("--config", "-c", type=click.Path(exists=True), default='feature_extractor_config.ini', help="Feature extractor config.")
def process(input, output, config):
    extractor_config = configparser.ConfigParser()
    extractor_config.read(config)
    audio_files = glob.glob(input + '/*.wav', recursive=True)
    for path in audio_files:
        print('Processing', path)
        y, sr = librosa.load(path, sr=16000)
        filename_noext = os.path.splitext(os.path.basename(path))[0]
        output_path = os.path.join(output, filename_noext + '.h5')
        features = get_features_from_ndarray(y, sr, **extractor_config)
        features.to_hdf(output_path, key=filename_noext.replace('-', '_'), mode='w', format='fixed')


if __name__ == '__main__':
    process()
