#     Copyright 2019 Lukasz Tracewski
#
#     Licensed under the Apache License, Version 2.0 (the "License");
#     you may not use this file except in compliance with the License.
#     You may obtain a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#     Unless required by applicable law or agreed to in writing, software
#     distributed under the License is distributed on an "AS IS" BASIS,
#     WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#     See the License for the specific language governing permissions and
#     limitations under the License.

import os
import boto3
import dash
import dash_table
import dash_audio_components
import dash_upload_components
import dash_core_components as dcc
import dash_html_components as html
import httpagentparser
from datetime import datetime
from flask import request
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from botocore.client import Config

from settings import S3_BUCKET
from audioexplorer.audio_io import read_wave_local, read_wave_part_from_s3, convert_to_wav
from audioexplorer.features import get, FEATURES
from audioexplorer.embedding import get_embeddings, EMBEDDINGS
from audioexplorer.visualize import make_scatterplot, specgram_base64
from audioexplorer import dbconnect


app = dash.Dash(__name__, external_stylesheets=['https://codepen.io/chriddyp/pen/bWLwgP.css', "https://codepen.io/chriddyp/pen/brPBPO.css"])
dash_upload_components.decorate_server(app.server, "uploads")
application = app.server

with open('docs/app_description.md', 'r') as file:
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


def NamedSlider(id, min, max, value, step=None, marks=None, slider_type=dcc.Slider, hidden=False):
    div = html.Div([
        html.Div(id=f'name-{id}', hidden=hidden),
            slider_type(
                id=id,
                min=min,
                max=max,
                marks=marks,
                step=step,
                value=value,
            )
        ],
        style={'margin': '25px 5px 30px 0px'},
        hidden=hidden,
        id=f'slidercontainer-{id}'
    )

    return div

main_app = html.Div(
    className="container",
    style={
        'width': '95%',
        'max-width': 'none',
        'font-size': '1.5rem',
        'padding': '10px 30px'
    },
    children=[
        dcc.Store(id='signed-url-store', storage_type='memory'),
        dcc.Store(id='feature-store', storage_type='memory'),
        dcc.Store(id='filename-store', storage_type='memory'),

        # Body
        html.Div(className="row", children=[
            html.Div(className="eight columns", children=[
                html.Div(id='error-report', style={'color': 'red'}),
                dcc.Graph(
                    id='graph',
                    style={'height': '90vh'}
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
                        textLabel="UPLOAD AUDIO",
                        startButton=False,
                        pauseButton=False,
                        cancelButton=False,
                        defaultStyle=upload_style,
                        activeStyle=upload_style,
                        completeStyle=upload_style,
                        completedMessage='UPLOAD AUDIO'
                    ),
                    html.Button('Apply', id='apply-button', style=upload_style),
                ], style={'columnCount': 2}),
                dcc.Dropdown(
                    id='algorithm-dropdown',
                    options=[{'label': label, 'value': value} for value, label in EMBEDDINGS.items()],
                    placeholder='Select embedding',
                    value='umap'
                ),
                html.H4('Select features'),
                dcc.Checklist(
                    id='features-selection',
                    options=[{'label': label, 'value': value} for value, label in FEATURES.items()],
                    values=['freq'],
                    labelStyle={'display': 'inline-block', 'margin': '6px'}
                ),
                html.H4('Algorithm parameters'),
                NamedSlider(
                    id='fft-size',
                    min=2**7,
                    max=2**11,
                    marks={i: i for i in [2**i for i in range(7,12)]},
                    value=2**9
                ),
                NamedSlider(
                    id='bandpass',
                    min=0,
                    max=8000,
                    step=100,
                    marks={
                        0: 'None',
                        500: '500 Hz',
                        4000: '4000 Hz',
                        5000: '5000 Hz',
                        6000: '6000 Hz',
                        8000: 'None'
                    },
                    value=[500, 6000],
                    slider_type=dcc.RangeSlider
                ),
                NamedSlider(
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
                    id='sample-len',
                    min=0.1,
                    max=1.0,
                    step=0.01,
                    marks={
                        0.1: '0.1 s',
                        0.2: '0.2 s',
                        0.3: '0.3 s',
                        0.5: '0.5 s',
                        1.0: '1.0 s',
                    },
                    value=0.26
                ),
                NamedSlider(
                    id='embedding-neighbours',
                    min=5,
                    max=100,
                    step=5,
                    marks={
                        5: 'Low',
                        15: 'Normal',
                        50: 'Strong',
                        100: 'Beyond reason'
                    },
                    value=40
                ),
                html.Div(id='div-spectrogram', style={'margin-top': '20px'})
            ]),
        ]),
    ]
)

table = html.Div(
    className="container",
    style={
        'width': '95%',
        'max-width': 'none',
        'font-size': '1.5rem',
        'padding': '10px 30px'
    },
    children=[
        html.Div(id='features-container')
    ]
)

app.layout = html.Div([
    dcc.Tabs(id='tabs', children=[
        dcc.Tab(label='Explore', children=[
            main_app
        ]),
        dcc.Tab(label='Table', children=[
            html.Div(
                children=table
            )
        ]),
        dcc.Tab(label='About', children=[
            html.Div(
                style={
                    'width': '75%',
                    'margin': '30px auto',
                },
                children=dcc.Markdown(description_md)
            )
        ]),
    ])
])


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


def clustering_strength_translator(type, value):
    if type in ['umap', 'isomap']:
        return {'n_neighbors': value}
    elif type == 'tsne':
        return {'perplexity': value}
    return None


@app.callback(Output('features-container', 'children'),
              [Input('feature-store', 'data')])
def show_features_in_table(data):
    if data is None:
        raise PreventUpdate

    feature_table = dash_table.DataTable(
        id='features-table',
        columns=[{'name': i, 'id': i} for i in data[0].keys()],
        data=data,
        pagination_mode='fe',
        pagination_settings={'page_size': 20, 'current_page': 0}
    )
    return feature_table


@app.callback(Output('name-fft-size', 'children'),
              [Input('fft-size', 'value')])
def display_value(value):
    return f'FFT window size: {value}'


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


@app.callback(Output('name-embedding-neighbours', 'children'),
              [Input('embedding-neighbours', 'value')])
def display_value(value):
    return f'Number of neighbours: {value}'

@app.callback(Output('slidercontainer-embedding-neighbours', 'style'),
              [Input('algorithm-dropdown', 'value')])
def show_extra_options(value):
    if value in ['umap', 'isomap']:
        return {'display': 'block'}
    else:
        return {'display': 'none'}


@app.callback(Output('filename-store', 'data'),
              [Input('upload-data', 'fileNames')])
def convert_upload_to_wave(filenames):
    if filenames is not None:
        if request.headers.getlist("X-Forwarded-For"):
            user_ip = request.headers.getlist("X-Forwarded-For")[0]
        else:
            user_ip = request.remote_addr

        if ',' in user_ip:
            user_ip = user_ip.split(',')[0]

        filepath = 'uploads/' + filenames[-1]
        time_now = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
        filename, ext = os.path.splitext(os.path.basename(filepath))
        key = f'{filename}_{time_now}_{user_ip}.wav'
        agent = request.headers.get('User-Agent')
        user_os, browser = httpagentparser.simple_detect(agent)


        d = {'datetime': time_now,
             'user_os': user_os,
             'user_browser': browser,
             'user_ip': user_ip,
             'upload': key}
        dbconnect.insert_user(d)

        convert_to_wav(filepath, 'uploads/' + key)
        return key
    else:
        raise PreventUpdate


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
               Output('feature-store', 'data'),
               Output('error-report', 'children')],
              [Input('filename-store', 'data'),
               Input('apply-button', 'n_clicks')],
              [State('algorithm-dropdown', 'value'),
               State('fft-size', 'value'),
               State('bandpass', 'value'),
               State('onset-threshold', 'value'),
               State('sample-len', 'value'),
               State('embedding-neighbours', 'value'),
               State('features-selection', 'values')])
def plot_embeddings(filename, n_clicks, embedding_type, fftsize, bandpass, onset_threshold, sample_len,
                    neighbours, selected_features):
    if filename is not None:
        filepath = 'uploads/' + filename
        lowpass, highpass = bandpass
        min_duration = sample_len - 0.05
        fs, X = read_wave_local(filepath)
        features = get(X, fs, n_jobs=1, selected_features=selected_features, lowcut=lowpass, highcut=highpass,
                       block_size=fftsize, onset_detector_type='hfc', onset_silence_threshold=-90,
                       onset_threshold=onset_threshold, min_duration_s=min_duration,    sample_len=sample_len)
        features_for_emb = features.drop(columns=['onset', 'offset'])

        params = clustering_strength_translator(embedding_type, neighbours)

        try:
            embeddings, warning_msg = get_embeddings(features_for_emb, type=embedding_type, n_jobs=1, **params)

            # features.insert(0, column='filename', value=filenames[-1])
            extra_data = ['onset', 'offset']
            if 'freq_mean' in features:
                mean_freq = features['freq_mean'].astype(int).astype(str) + ' Hz'
            elif 'pitch_median' in features:
                mean_freq = features['pitch_median'].astype(int).astype(str) + ' Hz'
            else:
                mean_freq = None
            figure = make_scatterplot(x=embeddings[:, 0], y=embeddings[:, 1],
                                      customdata=features[extra_data],
                                      text=mean_freq)

            return figure, features.round(2).to_dict(orient='rows'), warning_msg
        except Exception as ex:
            return dcc.Graph(), None, str(ex)
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
