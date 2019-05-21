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

import base64
import numpy as np
import matplotlib
matplotlib.use('agg')
import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objs as go
import xarray as xr
import datashader as ds
import datashader.transfer_functions as tf
from io import BytesIO
from collections import OrderedDict
from scipy import signal
from numpy.lib.stride_tricks import as_strided
from audioexplorer import yaafe_wrapper


def scatter_plot(x, y, customdata=None, text=None, opacity=0.8) -> go.Figure:

    trace0 = go.Scatter(
        x=x,
        y=y,
        mode='markers',
        marker=dict(
            size=4,
            color='red',
            opacity=opacity),
        customdata=customdata,
        text=text,
        hoverinfo='text'
    )

    layout = go.Layout(
        autosize=True,
        hovermode='closest',
        xaxis=dict(
            title='x',
            ticklen=5,
            zeroline=False,
            gridwidth=2,
        ),
        yaxis=dict(
            title='y',
            ticklen=5,
            zeroline=False,
            gridwidth=2,
        ),
        showlegend=False
    )
    fig = go.Figure(data=[trace0], layout=layout)
    return fig


def specgram_base64(y: np.ndarray, fs: int, start: float, end: float, margin) -> str:
    f, ax = plt.subplots()
    plt.specgram(y, Fs=fs, xextent=[start - margin, end + margin])
    plt.xlabel('Time [s]')
    plt.ylabel('Frequency [Hz]')
    plt.title('Spectrogram')
    ax.axvline(x=start, color='red', alpha=0.3)
    ax.axvline(x=end, color='red', alpha=0.3)

    with BytesIO() as stream:
        plt.savefig(stream, format='png')
        stream.seek(0)
        base64_jpg = base64.b64encode(stream.read()).decode("utf-8")
    plt.close(f)
    return base64_jpg


def power_spectrum(y: np.ndarray, fs: int, block_size: int=512, scaling: str='spectrum', cutoff: int=-100) -> go.Figure:
    """
    Plot power spectrum for 1d signal in dB scale
    :param y: signal
    :param fs: sampling frequency
    :param block_size: size of fft and nperseg
    :param scaling: spectrum or density
    :param cutoff: cut all signal below this strength
    :return: plotly Figure
    """
    f, spec = signal.welch(y, fs, scaling=scaling, nperseg=block_size, nfft=block_size, noverlap=block_size // 2,
                           detrend=False)
    spec = 10 * np.log10(spec)
    trace = go.Scatter(x=f, y=spec, fill='tozerox')

    if cutoff:
        ymin = max(cutoff, spec.min())
        ymax = int(spec.max()) + 5
        yaxis_range = (ymin, ymax)
    else:
        yaxis_range = None

    layout = go.Layout(
        title='Power Spectral Density',
        xaxis={
            'title': 'Frequency [Hz]',
            'zeroline': False
        },
        yaxis={
            'range': yaxis_range,
            'title': 'Amplitude [dB]',
            'zeroline': False
        },
        showlegend=False,
    )
    fig = go.Figure(data=[trace], layout=layout)
    return fig


def waveform(y: np.ndarray, fs: int):
    t = np.linspace(0, len(y) / fs, num=len(y))
    trace = go.Scattergl(x=t, y=y)

    layout = go.Layout(
        title='Waveform',
        xaxis={
            'title': 'Time [s]',
            'zeroline': False
        },
        yaxis={
            'title': 'Amplitude',
            'zeroline': False
        },
        showlegend=False,
    )
    fig = go.Figure(data=[trace], layout=layout)
    return fig


def waveform_downsampled(y: np.ndarray, fs: int, max_points=5e4, max_fs=1000):
    target_fs = fs
    if max_points < y.shape[-1]:
        target_fs = min(max_fs, (fs * y.shape[-1]) // max_points)
    hop = fs // target_fs

    n_frames = 1 + int((len(y) - hop) / hop)
    y = as_strided(y, shape=(hop, n_frames), strides=(y.itemsize, hop * y.itemsize)).max()
    return y


def waveform_shaded(signal: np.ndarray, fs: int, start=0, end=None):
    if end is None:
        end = len(signal) / fs
    ymargin_factor = 1.1
    x_range = [start, end]
    y_range = [ymargin_factor * signal.min(), ymargin_factor * signal.max()]
    t = np.linspace(start, end, num=len(signal))
    df = pd.DataFrame(data={'Time': t, 'Signal': signal})
    cvs = ds.Canvas(x_range=x_range, y_range=y_range, plot_width=1500)

    cols = ['Signal']
    aggs = OrderedDict((c, cvs.line(df, 'Time', c)) for c in cols)
    img = tf.shade(aggs['Signal'])
    arr = np.array(img)
    z = arr.tolist()
    dims = len(z[0]), len(z)

    x = np.linspace(x_range[0], x_range[1], dims[0])
    y = np.linspace(y_range[0], y_range[1], dims[0])

    fig = {
        'data': [{
            'x': x,
            'y': y,
            'z': z,
            'type': 'heatmap',
            'showscale': False,
            'colorscale': [[0, 'rgba(255, 255, 255,0)'], [1, '#75baf2']],
            }],
        'layout': {
            'height': 350,
            'xaxis': {
                'title': 'Time [s]',
                'showline': True,
                'zeroline': False,
                'showgrid': False,
                'showticklabels': True
            },
            'yaxis': {
                'title': 'Amplitude',
                'fixedrange': True,
                'showline': False,
                'zeroline': False,
                'showgrid': False,
                'showticklabels': False,
                'ticks': ''
            },
            'title': 'Waveform'
        }
    }
    return fig


def calculate_spectrogram(y, fs, block_size=1024, backend='yaafe'):
    if backend == 'yaafe':
        freq, time, Sxx = yaafe_wrapper.calculate_spectrogram(y, fs, block_size=block_size)
    elif backend == 'scipy':
        freq, time, Sxx = signal.spectrogram(y, fs=fs, nperseg=block_size, noverlap=None)
        Sxx = Sxx.T # transpose to get the same shape as yaafe, i.e. [time, freq]
    else:
        raise NotImplemented(f'Backend {backend} not implemented')
    return freq, time, Sxx


def shapes_from_onsets(onsets, x_min, x_max, color='#d3d3d3'):
    if onsets:
        shapes = []
        for start, end in onsets:
            if (start > x_min) and (end < x_max):
                shape = {
                    'type': 'rect',
                    'xref': 'x',
                    'yref': 'paper',
                    'x0': start,
                    'y0': 0,
                    'x1': end,
                    'y1': 1,
                    'fillcolor': color,
                    'opacity': 0.1,
                    'line': {
                        'width': 0,
                    }
                }
                shapes.append(shape)
    else:
        shapes = None
    return shapes


def spectrogram_shaded(S, time, fs: int, start_time=0, end_time=None, onsets=None):
    """

    :param S: spectogram 2d array
    :param fs:
    :param start_time:
    :param end_time:
    :param block_size:
    :param step_size:
    :return:
    """
    if start_time and end_time:
        condition = (time > start_time) & ( time < end_time)
        S = S[condition]
        time = time[condition]

    freq = np.linspace(0, fs // 2, num=S.shape[-1])

    # highres_threshold = 4000
    # if len(time) < highres_threshold:
    #     x = time
    #     y = freq
    #     z = np.log(S).tolist()
    # else:
    S = np.log(S)
    xrdata = xr.DataArray(S, coords={'time': time, 'freq': freq}, dims=('time', 'freq'))
    x_range = [time[0], time[-1]]
    y_range = [0, freq[-1]]
    cvs = ds.Canvas(plot_width=1500, plot_height=S.shape[-1], x_range=x_range, y_range=y_range)

    raster = cvs.raster(xrdata.T, interpolate='nearest')
    img = tf.shade(raster)
    arr = np.array(img)

    z = arr.tolist()
    x = np.linspace(x_range[0], x_range[1], len(z[0]))
    y = np.linspace(y_range[0], y_range[1], len(z))

    fig = {
        'data': [{
            'x': x,
            'y': y,
            'z': z,
            'type': 'heatmap',
            'showscale': False,
            'colorscale': [[0, '#75baf2'], [1, 'rgba(255, 255, 255,0)']],
            'hovertemplate': "Frequency: %{y:.0f} Hz<br>" + "Time: %{x:.2f} s<br>" + "<extra></extra>",
            }],
        'layout': {
            'height': 400,
            'xaxis': {
                'title': 'Time [s]',
                'showline': True,
                'zeroline': False,
                'showgrid': False,
                'showticklabels': True
            },
            'yaxis': {
                'title': 'Frequency [Hz]',
                'showline': False,
                'zeroline': False,
                'showgrid': False,
                'showticklabels': True,
            },
            'title': 'Spectrogram'
        }
    }
    return fig
