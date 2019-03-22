#!/usr/bin/env python3

import os
import sys
import shutil
import glob
import click
import librosa
import configparser
import logging
import pandas as pd
from audioexplorer import features, embedding


@click.group()
@click.option('--quiet', default=False, is_flag=True, help='Run in a silent mode')
def root(quiet):
    if quiet:
        logging.basicConfig(stream=sys.stdout, level=logging.ERROR)
    else:
        logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)


@root.command('a2f', help='Audio to HDF5 features')
@click.option("--path", "-i", type=click.STRING, required=True, help="Path to audio.")
@click.option("--output", "-o", type=click.STRING, default='.', help="Output file or directory.")
@click.option("--jobs", "-j", type=click.INT, default=1, help="Number of jobs to run", show_default=True)
@click.option("--config", "-c", type=click.Path(exists=True), default='audioexplorer/algo_config.ini', help="Feature extractor config.")
@click.option('--single', is_flag=True, help='Produce a single HDF5')
def process(path, output, jobs, config, single):
    if not os.path.exists(output):
        os.makedirs(output)
    shutil.copy(config, output)
    extractor_config = configparser.ConfigParser()
    extractor_config.read(config)
    audio_files = glob.glob(path + '/*.wav', recursive=True)
    for path in audio_files:
        logging.info(f'Processing {path}')
        y, sr = librosa.load(path, sr=16000)
        filename_noext = os.path.splitext(os.path.basename(path))[0]
        key = filename_noext.replace('-', '_')
        feats = features.get(y, sr, n_jobs=jobs, **extractor_config)

        if single:
            name = get_name_from_config(config)
            output_path = os.path.join(output, name + '.h5')
            feats.to_hdf(output_path, key=key, mode='a', format='fixed')
        else:
            output_path = os.path.join(output, filename_noext + '.h5')
            feats.to_hdf(output_path, key=key, mode='w', format='fixed')


def get_name_from_config(configpath):
    algo_config = configparser.ConfigParser()
    algo_config.read(configpath)
    c = algo_config['DEFAULT']
    s = f'block-{c["block_size"]}_step-{c["step_size"]}_len-{c["sample_len"]}_onsthr-{c["onset_threshold"]}' \
        f'_onssil-{c["onset_silence_threshold"][1:]}_onsmin-{c["min_duration_s"]}_low-{c["lowcut"]}_high-{c["highcut"]}'
    return s


@root.command('f2m', help='Features to embedding model')
@click.option("--features", "-i", type=click.STRING, help="Path to h5 features.")
@click.option("--config", "-c", type=click.Path(exists=False),
              default='algo_config.ini', help="Feature extractor config.")
@click.option("--embedding", "-e", type=click.Choice(['tsne', 'umap'], case_sensitive=False),
              default='tsne', help='Embedding to use')
def h5_to_embedding(features, config, embedding):
    h5_features = glob.glob(features + '/*.h5', recursive=True)
    dfs = [pd.read_hdf(path) for path in h5_features]
    dfs = pd.concat(dfs)
    if not os.path.exists(config):
        name = 'audio_embedding'
        logging.info(f'No feature config provided or found. The output will default to {name}')
    else:
        name = get_name_from_config(config)

    embedding.fit_and_dump(dfs.values, embedding=embedding, name=name)


@root.command('m2e', help='Model to embedddings')
@click.option("--features", "-i", type=click.Path(exists=True), help="Path to h5 features.")
@click.option("--model", "-m", type=click.Path(exists=True), help="Embedding model to use.")
def embed_features(features, model):
    df = pd.read_hdf(features)


if __name__ == '__main__':
    root()
