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

import base64
import numpy as np
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import plotly.graph_objs as go
from io import BytesIO


def test_scatter() -> go.Figure:
    N = 100
    random_x = np.random.randn(N)
    random_y = np.random.randn(N)

    # Create a trace
    trace = go.Scatter(
        x=random_x,
        y=random_y,
        mode='markers'
    )

    # Plot and embed in ipython notebook!
    fig = go.Figure(data=[trace])
    return fig


def make_scatterplot(x, y, customdata=None, text=None, opacity=0.8) -> go.Figure:

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


def specgram_base64(signal: np.ndarray, fs, start, end) -> str:
    f, ax = plt.subplots()
    # xticks = np.linspace(start, end, 8).round(2)
    # ax.set_xticklabels(xticks)

    plt.specgram(signal, Fs=fs, xextent=[start, end])
    plt.xlabel('Time [s]')
    plt.ylabel('Frequency [Hz]')
    plt.title('Spectrogram')
    ax.axvline(x=start + 0.2, color='red', alpha=0.3)
    ax.axvline(x=end - 0.2, color='red', alpha=0.3)

    with BytesIO() as stream:
        plt.savefig(stream, format='png')
        stream.seek(0)
        base64_jpg = base64.b64encode(stream.read()).decode("utf-8")
    plt.close(f)
    return base64_jpg
