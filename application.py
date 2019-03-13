import os
import boto3
import dash
import dash_audio_components
import dash_resumable_upload
import dash_core_components as dcc
import dash_html_components as html
from datetime import datetime
from flask import request
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate
from botocore.client import Config

from settings import S3_BUCKET
from audioexplorer.audio_io import read_wave_local, read_wave_part_from_s3, convert_to_wav
from audioexplorer.feature_extractor import get_features_from_ndarray
from audioexplorer.embedding import get_embeddings
from audioexplorer.visualize import make_scatterplot, specgram_base64


app = dash.Dash(__name__, external_stylesheets=['https://codepen.io/chriddyp/pen/bWLwgP.css', "https://codepen.io/chriddyp/pen/brPBPO.css"])
dash_resumable_upload.decorate_server(app.server, "uploads")
application = app.server

with open('app_description.md', 'r') as file:
    description_md = file.read()

upload_style = {
    'width': '75%',
    'height': '60px',
    'lineHeight': '60px',
    'borderWidth': '1px',
    'borderStyle': 'dashed',
    'borderRadius': '5px',
    'textAlign': 'center',
    'margin': '30px auto'
}


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
        dcc.Store(id='metadata-store', storage_type='memory'),
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
            dash_resumable_upload.Upload(
                id='upload-data',
                maxFiles=1,
                simultaneousUploads=4,
                maxFileSize=5 * 1024 * 1024 * 1000,  # 500 MB
                service="/upload_resumable",
                textLabel="Drag and Drop Here to upload!",
                startButton=False,
                pauseButton=False,
                cancelButton=False,
                defaultStyle=upload_style,
                activeStyle=upload_style,
                completeStyle=upload_style
            )
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
                html.Div(id='upload-completed'),
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
               Output('metadata-store', 'data')],
              [Input('filename-store', 'data')])
def plot_embeddings(filename):
    if filename is not None:
        filepath = 'uploads/' + filename
        fs, X = read_wave_local(filepath)
        features = get_features_from_ndarray(X, fs, n_jobs=1)
        features_for_emb = features.drop(columns=['onset', 'offset'])
        embeddings = get_embeddings(features_for_emb, type='tsne', perplexity=60)
        # features.insert(0, column='filename', value=filenames[-1])
        extra_data = ['onset', 'offset']
        figure = make_scatterplot(x=embeddings[:, 0], y=embeddings[:, 1], customdata=features[extra_data])

        metadata = {'fs': fs}
        return figure, metadata
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
                'from_position': start - 0.4,
                'to_position': end + 0.4}
    else:
        raise PreventUpdate()


@app.callback(Output('div-spectrogram', 'children'),
              [Input('graph', 'clickData'),
               Input('metadata-store', 'data'),
               Input('filename-store', 'data')])
def display_click_image(click_data, metadata, url):
    if (click_data is not None) and (url is not None):
        start, end = click_data['points'][0]['customdata']
        fs = metadata['fs']
        wav = read_wave_part_from_s3(
            bucket=S3_BUCKET,
            path=url,
            fs=fs,
            start=start - 0.4,
            end=end + 0.4)
        im = specgram_base64(signal=wav, fs=fs, start=start - 0.4, end=end + 0.4)

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
