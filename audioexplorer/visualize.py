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
import matplotlib.pyplot as plt
import plotly.graph_objs as go
from io import BytesIO
from scipy import signal


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


def specgram_base64(y: np.ndarray, fs: int, start: float, end: float, margin: float=0.2) -> str:
    f, ax = plt.subplots()
    # xticks = np.linspace(start, end, 8).round(2)
    # ax.set_xticklabels(xticks)

    plt.specgram(y, Fs=fs, xextent=[start, end])
    plt.xlabel('Time [s]')
    plt.ylabel('Frequency [Hz]')
    plt.title('Spectrogram')
    ax.axvline(x=start + margin, color='red', alpha=0.3)
    ax.axvline(x=end - margin, color='red', alpha=0.3)

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