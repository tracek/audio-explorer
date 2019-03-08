import os
import boto3
import json
import pandas as pd
import dash
import dash_audio_components
import dash_resumable_upload
import dash_core_components as dcc
import dash_html_components as html
from datetime import datetime
from collections import namedtuple
from flask import request
from dash.dependencies import Input, Output

from settings import S3_BUCKET
from audioexplorer.audio_io import read_wave_local
from audioexplorer.feature_extractor import get_features_from_ndarray
from audioexplorer.embedding import get_embeddings
from audioexplorer.visualize import make_scatterplot


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
dash_resumable_upload.decorate_server(app.server, "uploads")
application = app.server

Sample = namedtuple('Sample', ['path', 'start', 'end'])


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
        # Header
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
                maxFileSize=10 * 1024 * 1024 * 1000,  # 500 MB
                service="/upload_resumable",
                textLabel="Drag and Drop Here to upload!",
                startButton=False,
                pauseButton=False,
                cancelButton=False,
                defaultStyle=upload_style,
                activeStyle=upload_style,
                completeStyle=upload_style
            ),
            html.Div(id='upload-output'),
        ]),

        # Body
        html.Div(className="row", children=[
            html.Div(className="eight columns", children=[
                html.Div(id='embedding-graph'),
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


def copy_file_to_bucket(filepath_input):
    remote_ip = str(request.remote_addr)
    time_now = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
    filename, ext = os.path.splitext(os.path.basename(filepath_input))
    key = f'{filename}_{time_now}_{remote_ip}.{ext}'
    s3 = boto3.resource('s3')
    bucket = s3.Bucket('audioexplorer')
    with open(filepath_input, 'rb') as data:
        bucket.upload_fileobj(data, key)


def copy_b64_to_bucket(decoded_b64, filename, content_type):
    s3 = boto3.resource('s3')
    remote_ip = str(request.remote_addr)
    time_now = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
    filename, ext = os.path.splitext(filename)
    key = f'audioexplorer/{filename}_{time_now}_{remote_ip}.{ext}'
    obj = s3.Object(S3_BUCKET, key)
    obj.put(Body=decoded_b64, ContentType=content_type)


# def store_df(df: pd.DataFrame):
#     df.to_json()
#
#
# def get_sample_from_pointclick(click) -> Sample:
#     idx = click['points'][0]['pointIndex']
#     data = df.iloc[idx]
#     sample = Sample(path='data/raw/' + data['sound.files'],
#                     start=data['start'],
#                     end=data['end'])
#     return sample


@app.callback(Output('upload-completed', 'children'),
              [Input('upload-data', 'fileNames')])
def plot_embeddings(filenames):
    if filenames is not None:
        filepath = 'uploads/' + filenames[-1]
        copy_file_to_bucket(filepath)

        return html.Label('Completed!')




@app.callback(Output('embedding-graph', 'children'),
              [Input('upload-data', 'fileNames')])
def plot_embeddings(filenames):
    if filenames is not None:
        filepath = 'uploads/' + filenames[-1]
        fs, X = read_wave_local(filepath)
        features = get_features_from_ndarray(X, fs, n_jobs=1)
        features_for_emb = features.drop(columns=['onsets', 'offset'])
        embeddings = get_embeddings(features_for_emb, type='tsne', perplexity=60)
        features.insert(0, column='filename', value=filenames[-1])
        figure = make_scatterplot(x=embeddings[:, 0], y=embeddings[:, 1], customdata=features.values)

        graph = html.Div([
            dcc.Graph(
                id='example-graph',
                figure=figure,
                style={'height': '80vh'}
            )
        ])

        return graph


# @app.callback(Output('audio-player', 'overrideProps'),
#               [Input('storm-petrel-embedding', 'clickData')])
# def update_player_status(click_data):
#     if click_data:
#         sample = get_sample_from_pointclick(click_data)
#         audio_path = S3_STREAMED_PREFIX + sample.path
#         return {'autoPlay': True,
#                 'src': audio_path,
#                 'from_position': sample.start,
#                 'to_position': sample.end + EXTRA_SOUND_DURATION}



if __name__ == '__main__':
    application.run(host='0.0.0.0', debug=True, port=8080)
