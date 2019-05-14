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

import os
import wave
import numpy as np
import boto3
import librosa
import sox
import logging
from scipy.io import wavfile


def is_conversion_required(filepath):
    sample_rate_16khz = int(sox.file_info.sample_rate(filepath)) == 16000
    mono = sox.file_info.channels(filepath) == 1
    wav = sox.file_info.file_type(filepath) == 'wav'
    convert = sample_rate_16khz and mono and wav
    return not convert


def convert_to_wav(input_path, output_path):
    logging.info(f'Entering convert_to_wav with input: {input_path} to {output_path}')
    if not os.path.isfile(input_path):
        raise Exception(f'Input path {input_path} is not there!')
    if is_conversion_required(input_path):
        tfm = sox.Transformer()
        tfm.set_globals(dither=True)
        tfm.rate(samplerate=16000)
        tfm.norm(db_level=-3)
        tfm.channels(1)
        tfm.build(input_filepath=input_path, output_filepath=output_path)
    else:
        os.rename(input_path, output_path)


def read_wave_local(path: str) -> (int, np.ndarray):
    # fs, signal = wavfile.read(path)
    fs, signal = wavfile.read(path)
    signal = signal / (2**15 - 1)
    return fs, signal


def seconds_to_wav_bytes(time, fs, dtype, wav_header_size: int=44):
    bytes = int(time * fs * np.dtype(dtype).itemsize) + wav_header_size
    if bytes % 2:  # odd byte, effect caused by rounding float
        bytes -= 1
    return bytes


def get_range_bytes(start, end, dtype, fs):
    start_bytes = seconds_to_wav_bytes(start, fs, dtype)
    end_bytes = seconds_to_wav_bytes(end, fs, dtype)
    if (end_bytes - start_bytes) % 2 == 0:
        end_bytes -= 1
    # Range set according to https://www.w3.org/Protocols/rfc2616/rfc2616-sec14.html#sec14.35
    range_bytes = f'bytes={start_bytes}-{end_bytes}'
    return range_bytes


def read_wave_part_from_s3(bucket: str, path: str, fs: int, start: int, end: int, dtype: np.dtype = np.int16) -> np.ndarray:
    """
    Read part of a wavefile from S3
    :param bucket: bucket name
    :param path: path in the bucket
    :param fs: frequency [Hz]
    :param start: start of audio of interest [s]
    :param end: end of audio of interest [s]
    :param dsize: data type size (e.g. int16 = 2 bytes)
    :return: wavefile of interest
    """
    client = boto3.client('s3')
    range_bytes = get_range_bytes(start, end, dtype, fs)
    o = client.get_object(Bucket=bucket, Key=path, Range=range_bytes)
    result = o['Body'].read()
    wav = np.frombuffer(result, dtype=dtype)
    return wav


def read_wav_parts_from_local(path: str, onsets: list, dtype = 'int16'):
    wavs = []
    with wave.open(path, mode='rb') as wavread:
        fs = wavread.getframerate()
        for start_s, end_s in onsets:
            start = int(start_s * fs)
            end = int(end_s * fs)
            sample_len = end - start
            wavread.setpos(start)
            wav_bytes = wavread.readframes(sample_len)
            wav_array = np.frombuffer(wav_bytes, dtype=dtype)
            wav_array = wav_array / (2 ** 15 - 1)
            wavs.append(wav_array)

    return wavs


def save_wav(y: np.ndarray, fs: int, path: str):
    y = y * (2 ** 15 - 1)
    wavfile.write(path, fs, y.astype('int16'))