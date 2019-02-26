import os
import base64
import boto3
import dash
import dash_audio_components
import dash_resumable_upload
import dash_core_components as dcc
import dash_html_components as html
from io import BytesIO
from datetime import datetime
from flask import request
from dash.dependencies import Input, Output, State

from settings import S3_BUCKET
from audioexplorer.feature_extractor import get_features_from_file
from audioexplorer.embedding import get_embeddings
from audioexplorer.visualize import make_scatterplot


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
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
                maxFileSize=5 * 1024 * 1024 * 1000,  # 500 MB
                service="/upload_resumable",
                textLabel="Drag and Drop Here to upload!",
                startButton=False,
                pauseButton=False,
                cancelButton=False,
                defaultStyle=upload_style,
                activeStyle=upload_style,
                completeStyle=upload_style
            ),
            html.Div(id='compid'),
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


def copy_b64_to_bucket(decoded_b64, filename, content_type):
    s3 = boto3.resource('s3')
    remote_ip = str(request.remote_addr)
    time_now = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
    filename, ext = os.path.splitext(filename)
    key = f'audioexplorer/{filename}_{time_now}_{remote_ip}.{ext}'
    obj = s3.Object(S3_BUCKET, key)
    obj.put(Body=decoded_b64, ContentType=content_type)


@app.callback(Output('upload-output', 'children'),
              [Input('upload-data', 'fileNames')])
def display_files(fileNames):
    if fileNames is not None:
        return html.Ul([html.Li(
            html.Img(height="50", width="100", src=x)) for x in fileNames])



if __name__ == '__main__':
    application.run(host='0.0.0.0', debug=True, port=8080)
