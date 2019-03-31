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
def cli(quiet):
    if quiet:
        logging.basicConfig(stream=sys.stdout, level=logging.ERROR)
    else:
        logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)


@cli.command('a2f', help='Audio to HDF5 features')
@click.option("--input", "-in", type=click.STRING, required=True, help="Path to audio.")
@click.option("--output", "-out", type=click.STRING, default='.', help="Output file or directory.")
@click.option("--jobs", "-j", type=click.INT, default=1, help="Number of jobs to run", show_default=True)
@click.option("--config", "-c", type=click.Path(exists=True), default='audioexplorer/algo_config.ini', help="Feature extractor config.")
@click.option('--single', "-s", is_flag=True, help='Produce a single HDF5')
@click.option("--format", "-f", type=click.Choice(['fixed', 'table'], case_sensitive=False), default='fixed', help='HDF5 format')
def process(input, output, jobs, config, single, format):
    extractor_config = configparser.ConfigParser()
    extractor_config.read(config)
    audio_files = glob.glob(input + '/*.wav', recursive=False)
    config_signature = get_name_from_config(config)
    
    if single:
        os.makedirs(output, exist_ok=True)
        output_path = os.path.join(output, config_signature + '.h5')
        shutil.copy(config, output)
    else:
        output_path = os.path.join(output, config_signature)
        os.makedirs(output_path, exist_ok=True)
        shutil.copy(config, output_path)
    
    for wav in audio_files:
        logging.info(f'Processing {wav}')
        y, sr = librosa.load(wav, sr=16000)
        filename_noext = os.path.splitext(os.path.basename(wav))[0]
        key = filename_noext.replace('-', '_')
        feats = features.get(y, sr, n_jobs=jobs, **extractor_config)

        if not feats.empty:
            if single:
                feats.to_hdf(output_path, key=key, mode='a', format=format)
            else:
                output_path_file = os.path.join(output_path, filename_noext + '.h5')
                feats.to_hdf(output_path_file, key=key, mode='w', format=format)


def get_name_from_config(configpath):
    algo_config = configparser.ConfigParser()
    algo_config.read(configpath)
    c = algo_config['DEFAULT']
    s = f'block-{c["block_size"]}_step-{c["step_size"]}_len-{c["sample_len"]}_onsthr-{c["onset_threshold"]}' \
        f'_onssil-{c["onset_silence_threshold"][1:]}_onsmin-{c["min_duration_s"]}_low-{c["lowcut"]}_high-{c["highcut"]}'
    return s


@cli.command('f2m', help='Features to embedding model')
@click.option("--input", "-in", type=click.STRING, help="Path to h5 features.", required=True)
@click.option("--output", "-out", type=click.STRING, help="Output directory.")
@click.option("--jobs", "-j", type=click.INT, default=-1, help="Number of jobs to run", show_default=True)
@click.option("--algo", "-a", type=click.Choice(['tsne', 'umap'], case_sensitive=False), default='umap', help='Embedding to use')
@click.option("--params", "-p", type=click.Path(exists=True), help="JSON with grid search parameters for the embedding algo")
def h5_to_embedding(input, output, jobs, algo, params):
    if os.path.isfile(input):
        hdf_store = pd.HDFStore(input)
        hdf_keys = hdf_store.keys()
        hdf_store.close()
        dfs = [pd.read_hdf(input, key=key) for key in hdf_keys]
        dfs = pd.concat(dfs)
        if not output:
            output = os.path.splitext(input)[0]
    elif os.path.isdir(input):
        input = os.path.normpath(input)
        h5_features = glob.glob(input + '/*.h5', recursive=False)
        dfs = [pd.read_hdf(path) for path in h5_features]
        dfs = pd.concat(dfs)
        if not output:
            output = input
    else:
        raise Exception(f'Input {input} not recognised as file or directory.')
    embedding.fit_and_dump(dfs.values, embedding_type=algo, output_path=output, n_jobs=jobs, grid_path=params)


@cli.command('m2e', help='Model to embedddings')
@click.option("--input", "-i", type=click.Path(exists=True), help="Path to h5 features.", required=True)
@click.option("--model", "-m", type=click.Path(exists=True), help="Embedding model to use.", required=True)
@click.option("--output", "-out", help="Embedding output path.")
def embed_features(input, model, output):
    df = pd.read_hdf(input)
    res = embedding.load_and_transform(df.values, model)
    df_emb = pd.DataFrame(data=res, columns=['x', 'y'], index=False)
    if not output:
        output = os.path.splitext(input)[0] + '.csv'
    df_emb.to_csv(output, index=False)


if __name__ == '__main__':
    cli()
