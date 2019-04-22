import os
import boto3
import dash
import dash_audio_components
import dash_upload_components
import dash_core_components as dcc
import dash_html_components as html
from datetime import datetime
from flask import request
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate
from botocore.client import Config

from settings import S3_BUCKET
from audioexplorer.audio_io import read_wave_local, read_wave_part_from_s3, convert_to_wav
from audioexplorer.features import get, FEATURES
from audioexplorer.embedding import get_embeddings, EMBEDDINGS
from audioexplorer.visualize import make_scatterplot, specgram_base64


app = dash.Dash(__name__, external_stylesheets=['https://codepen.io/chriddyp/pen/bWLwgP.css', "https://codepen.io/chriddyp/pen/brPBPO.css"])
dash_upload_components.decorate_server(app.server, "uploads")
application = app.server

with open('app_description.md', 'r') as file:
    description_md = file.read()

upload_style = {
    'width': '100%',
    'height': '30px',
    'lineHeight': '30px',
    'borderWidth': '1px',
    'borderStyle': 'solid',
    'borderRadius': '5px',
    'textAlign': 'center',
    'margin': '15px auto'
}


def NamedSlider(name, id, min, max, value, step=None, marks=None, slider_type=dcc.Slider):

    return html.Div([
        html.Div(id=f'name-{id}', children=name),
        slider_type(
            id=id,
            min=min,
            max=max,
            marks=marks,
            step=step,
            value=value),
    ], style={'margin': '25px 5px 30px 0px'},)


def NamedSlider2(name, short, min, max, value, step=None, marks=None, slider_type=dcc.Slider):

    return html.Div(
        style={'margin': '25px 5px 30px 0px'},
        children=[
            f"{name}:",
            html.Div(style={'margin-left': '5px'}, children=[
                slider_type(
                    id=f'slider-{short}',
                    min=min,
                    max=max,
                    marks=marks,
                    step=step,
                    value=value)
            ])
        ])


app.layout = html.Div(
    className="container",
    style={
        'width': '90%',
        'max-width': 'none',
        'font-size': '1.5rem',
        'padding': '10px 30px'
    },
    children=[
        dcc.Store(id='signed-url-store', storage_type='memory'),
        dcc.Store(id='feature-store', storage_type='memory'),
        dcc.Store(id='filename-store', storage_type='memory'),
        html.Div(className="row", children=[
            html.H2(
                'Audio Explorer pre-alpha',
                id='title',
                style={
                    'width': '75%',
                    'margin': '30px auto',
                }
            ),
        ]),

        # Body
        html.Div(className="row", children=[
            html.Div(className="eight columns", children=[
                dcc.Graph(
                    id='graph',
                    style={'height': '80vh'}
                ),
                dash_audio_components.DashAudioComponents(
                    id='audio-player',
                    style={'width': '90%'},
                    src='',
                    autoPlay=True,
                    controls=False
                )
            ]),
            html.Div(className="four columns", children=[
                html.Div([
                    dash_upload_components.Upload(
                        id='upload-data',
                        maxFiles=1,
                        simultaneousUploads=1,
                        maxFileSize=10 * 1024 * 1024 * 1000,  # 1000 MB
                        service="/upload_resumable",
                        textLabel="Drag and Drop Here to upload!",
                        startButton=False,
                        pauseButton=False,
                        cancelButton=False,
                        defaultStyle=upload_style,
                        activeStyle=upload_style,
                        completeStyle=upload_style
                    ),
                    html.Button('Apply', id='apply-button', style=upload_style),
                ], style={'columnCount': 2}),
                dcc.Dropdown(
                    id='algorithm',
                    options=[{'label': label, 'value': value} for value, label in EMBEDDINGS.items()],
                    placeholder='Select embedding'
                ),
                html.H4('Select features'),
                dcc.Checklist(
                    options=[{'label': label, 'value': value} for value, label in FEATURES.items()],
                    values=['freq'],
                    labelStyle={'display': 'inline-block', 'margin': '6px'}
                ),
                html.H4('Algorithm parameters'),
                NamedSlider(
                    name='FFT window size',
                    id='fft-size',
                    min=2**7,
                    max=2**11,
                    marks={i: i for i in [2**i for i in range(7,12)]},
                    value=2**8
                ),
                NamedSlider(
                    name='Bandpass filter [Hz]',
                    id='bandpass',
                    min=0,
                    max=8000,
                    step=100,
                    marks={
                        0: 'None',
                        500: '500 Hz',
                        2000: '2000 Hz',
                        4000: '4000 Hz',
                        5000: '5000 Hz',
                        6000: '6000 Hz',
                        8000: 'None'
                    },
                    value=[500, 6000],
                    slider_type=dcc.RangeSlider
                ),
                NamedSlider(
                    name='Onset detection threshold',
                    id='onset-threshold',
                    min=0,
                    max=0.1,
                    step=0.005,
                    marks={
                        0: 'None',
                        0.01: '0.01',
                        0.05: '0.05',
                        0.1: '0.1'
                    },
                    value=0.01
                ),
                NamedSlider(
                    name='Sample length',
                    id='sample-len',
                    min=0.1,
                    max=1,
                    step=0.01,
                    marks={
                        0.1: '0.1 s',
                        0.2: '0.2 s',
                        0.3: '0.3 s',
                        0.5: '0.5 s',
                        1.0: '1.0 s'
                    },
                    value=0.26
                ),
                html.Div(id='div-spectrogram', style={'margin-top': '20px'})
            ]),
        ]),

        html.Div(
            className='row',
            children=html.Div(
                style={
                    'width': '75%',
                    'margin': '30px auto',
                },
                children=dcc.Markdown(description_md)
            )
        )
    ]
)


def copy_file_to_bucket(filepath_input, key):
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(S3_BUCKET)
    with open(filepath_input, 'rb') as data:
        bucket.upload_fileobj(data, key, ExtraArgs={'ContentType': 'audio/wav'})


def generate_signed_url(key: str):
    """
    Create a signed url so that user can play the audio uploaded to a private bucket.
    :param key: bucket key
    :return: signed url
    """
    s3_client = boto3.client('s3', region_name='eu-central-1', config=Config(signature_version='s3v4'))
    url = s3_client.generate_presigned_url('get_object', Params={'Bucket': S3_BUCKET, 'Key': key}, ExpiresIn=3600)
    return url


@app.callback(Output('name-bandpass', 'children'),
              [Input('bandpass', 'value')])
def display_value(value):
    return f'Bandpass filter: {value[0]} - {value[1]} Hz'


@app.callback(Output('name-onset-threshold', 'children'),
              [Input('onset-threshold', 'value')])
def display_value(value):
    return f'Onset detection threshold: {value}'


@app.callback(Output('name-sample-len', 'children'),
              [Input('sample-len', 'value')])
def display_value(value):
    return f'Sample length: {value} s'


@app.callback(Output('filename-store', 'data'),
              [Input('upload-data', 'fileNames')])
def convert_upload_to_wave(filenames):
    if filenames is not None:
        remote_ip = str(request.remote_addr)
        filepath = 'uploads/' + filenames[-1]
        time_now = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
        filename, ext = os.path.splitext(os.path.basename(filepath))
        key = f'{filename}_{time_now}_{remote_ip}.wav'
        convert_to_wav(filepath, 'uploads/' + key)
        return key
    else:
        raise PreventUpdate()


@app.callback(Output('signed-url-store', 'data'),
              [Input('filename-store', 'data')])
def upload_to_s3(filename):
    if filename is not None:
        filepath = 'uploads/' + filename
        copy_file_to_bucket(filepath, filename)
        url = generate_signed_url(filename)
        return url
    else:
        raise PreventUpdate()


@app.callback([Output('graph', 'figure'),
               Output('feature-store', 'data')],
              [Input('filename-store', 'data')])
def plot_embeddings(filename):
    if filename is not None:
        filepath = 'uploads/' + filename
        fs, X = read_wave_local(filepath)
        features = get(X, fs, n_jobs=1, lowcut=500, highcut=6000, block_size=512, onset_detector_type='hfc',
                       onset_silence_threshold=-90, onset_threshold=0.01, min_duration_s=0.15, sample_len=0.26)
        features_for_emb = features.drop(columns=['onset', 'offset'])
        embeddings = get_embeddings(features_for_emb, type='tsne', perplexity=60)
        # features.insert(0, column='filename', value=filenames[-1])
        extra_data = ['onset', 'offset']
        mean_freq = features['freq_mean'].astype(int).astype(str) + ' Hz'
        figure = make_scatterplot(x=embeddings[:, 0], y=embeddings[:, 1],
                                  customdata=features[extra_data],
                                  text=mean_freq)

        return figure, features.to_dict(orient='rows')
    else:
        raise PreventUpdate()


@app.callback(Output('audio-player', 'overrideProps'),
              [Input('graph', 'clickData'),
               Input('signed-url-store', 'data')])
def update_player_status(click_data, url):
    if click_data:
        start, end = click_data['points'][0]['customdata']
        return {'autoPlay': True,
                'src': url,
                'from_position': start - 0.2,
                'to_position': end + 0.2}
    else:
        raise PreventUpdate()


@app.callback(Output('div-spectrogram', 'children'),
              [Input('graph', 'clickData'),
               Input('filename-store', 'data')])
def display_click_image(click_data, url):
    if (click_data is not None) and (url is not None):
        start, end = click_data['points'][0]['customdata']
        wav = read_wave_part_from_s3(
            bucket=S3_BUCKET,
            path=url,
            fs=16000,
            start=start - 0.2,
            end=end + 0.2)
        im = specgram_base64(signal=wav, fs=16000, start=start - 0.2, end=end + 0.2)

        return html.Img(
            src='data:image/png;base64, ' + im,
            style={
                'height': '25vh',
                'display': 'block',
                'margin': 'auto'
            }
        )


if __name__ == '__main__':
    application.run(host='0.0.0.0', debug=True, port=8080)
