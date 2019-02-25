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


def make_scatterplot(x, y) -> go.Figure:

    trace0 = go.Scatter(
        x=x,
        y=y,
        mode='markers',
        marker=dict(
            size=4,
            color='red',
            opacity=0.8)
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


def make_scatterplot_with_labels(x, y, labels=None, text='', title='') -> go.Figure:
    colors = ['red' if l == 1 else 'lightblue' for l in labels]

    trace0 = go.Scatter(
        x=x,
        y=y,
        mode='markers',
        marker=dict(
            size=4,
            color=colors,
            opacity=0.5),
        text=text)

    layout = go.Layout(
        title=title,
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


def specgram_base64(signal: np.ndarray, fs: int, start: int, end: int) -> str:
    f, ax = plt.subplots()
    xticks = np.linspace(start, end, 6).round(1)
    ax.set_xticklabels(xticks)
    plt.specgram(signal, Fs=fs)
    plt.xlabel('Time [s]')
    plt.ylabel('Frequency [Hz]')
    plt.title('Spectrogram')

    stream = BytesIO()
    plt.savefig(stream, format='png')
    stream.seek(0)
    base64_jpg = base64.b64encode(stream.read()).decode("utf-8")
    return base64_jpg
