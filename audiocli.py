#!/usr/bin/env python3

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

import os
import sys
import shutil
import glob
import time
import click
import librosa
import configparser
import logging
import pandas as pd
from joblib import Parallel, delayed
from audioexplorer import features, embedding


@click.group()
@click.option('--quiet', default=False, is_flag=True, help='Run in a silent mode')
def cli(quiet):
    """audiocli is a command line program that helps in extracting """
    if quiet:
        logging.basicConfig(stream=sys.stdout, level=logging.ERROR)
    else:
        logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)


@cli.command('a2f', help='Audio to HDF5 features')
@click.option("--input", "-in", type=click.STRING, required=True, help="Path to audio in WAV format.")
@click.option("--output", "-out", type=click.STRING, default='.', help="Output file or directory. If directory does "
              "not exist it will be created. The output files will have the same base name as input.")
@click.option("--jobs", "-j", type=click.INT, default=-1, help="Number of jobs to run. Defaults to all cores",
              show_default=True)
@click.option("--config", "-c", type=click.Path(exists=True), default='audioexplorer/algo_config.ini',
              help="Feature extractor config.")
@click.option('--multi', "-m", is_flag=True, help='Process audio files in parallel. The setting will produce an HDF5 '
              'file per input, with the same base name. Large memory footprint. If not set, a single output file will '
              'be produced.')
@click.option("--format", "-f", type=click.Choice(['fixed', 'table'], case_sensitive=False), default='fixed',
              help='HDF5 format. Table is slightly slower and requires pytables (will not work outside Python), '
                   'but allows to read specific columns.')
def process(input, output, jobs, config, multi, format):
    start_time = time.time()
    extractor_config = configparser.ConfigParser()
    extractor_config.read(config)
    audio_files = glob.glob(input + '/*.wav', recursive=False)
    if not audio_files:
        logging.error(f'No wave files on {input}')

    outdir = os.path.dirname(output)
    if outdir:
        os.makedirs(os.path.dirname(output), exist_ok=True)
        shutil.copy(config, outdir)
    else:
        shutil.copy(config, '.')

    if multi:
        Parallel(n_jobs=jobs, backend='multiprocessing')(delayed(process_path)(
            input_path=wav_path,
            extractor_config=extractor_config['DEFAULT'],
            output_path=output,
            hdf_format=format,
            multi=multi,
            jobs=1) for wav_path in audio_files)
    else:
        if os.path.isdir(output):
            logging.error(f'Supplied path {output} is a directory. Please supply a file name.')
            sys.exit(1)
        for wav_path in audio_files:
            process_path(input_path=wav_path,
                         extractor_config=extractor_config['DEFAULT'],
                         output_path=output,
                         hdf_format=format,
                         multi=multi,
                         jobs=jobs)
    logging.info(f'Completed processing in {time.time() - start_time:.2f}s')


def process_path(input_path, extractor_config, output_path, hdf_format, multi, jobs):
    logging.info(f'Processing {input_path}')
    y, sr = librosa.load(input_path, sr=16000)
    filename_noext = os.path.splitext(os.path.basename(input_path))[0]
    key = filename_noext.replace('-', '_')

    if multi:
        mode = 'w'
        feats = features.get(y, sr, n_jobs=1, **extractor_config)
        output_file = os.path.join(output_path, filename_noext + '.h5')
    else:
        mode = 'a'
        feats = features.get(y, sr, n_jobs=jobs, **extractor_config)
        output_file = output_path

    if not feats.empty:
        feats.to_hdf(output_file, key=key, mode=mode, format=hdf_format)
    else:
        logging.warning(f'No onsets found in {input_path}')
        outdir = os.path.dirname(output_path)
        with open(os.path.join(outdir, 'empty.log'), 'a') as f:
            f.write(input_path + '\n')


@cli.command('f2m', help='Features to embedding model')
@click.option("--input", "-in", type=click.STRING, help="Path to h5 features.", required=True)
@click.option("--output", "-out", type=click.STRING, help="Output directory.")
@click.option("--jobs", "-j", type=click.INT, default=-1, help="Number of jobs to run", show_default=True)
@click.option("--algo", "-a", type=click.Choice(list(embedding.EMBEDDINGS.keys()), case_sensitive=False), default='umap', help='Embedding to use')
@click.option("--grid", "-p", type=click.Path(exists=True), help="JSON with grid search parameters for the embedding algo")
def h5_to_embedding(input, output, jobs, algo, grid):
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
    embedding.fit_and_save_with_grid(dfs.values, type=algo, output_dir=output, n_jobs=jobs, grid_path=grid)


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


def get_name_from_config(configpath):
    algo_config = configparser.ConfigParser()
    algo_config.read(configpath)
    c = algo_config['DEFAULT']
    s = f'block-{c["block_size"]}_step-{c["step_size"]}_len-{c["sample_len"]}_onsthr-{c["onset_threshold"]}' \
        f'_onssil-{c["onset_silence_threshold"][1:]}_onsmin-{c["min_duration_s"]}_low-{c["lowcut"]}_high-{c["highcut"]}'
    return s


if __name__ == '__main__':
    cli()
