import os
import base64
import boto3
import dash
import dash_audio_components
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
application = app.server


with open('app_description.md', 'r') as file:
    description_md = file.read()


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
            dcc.Upload(
                id='upload-data',
                children=html.Div([
                    'To start, Drag and Drop audio or ',
                    html.A('Select Files')
                ]),
                style={
                    'width': '75%',
                    'height': '60px',
                    'lineHeight': '60px',
                    'borderWidth': '1px',
                    'borderStyle': 'dashed',
                    'borderRadius': '5px',
                    'textAlign': 'center',
                    'margin': '30px auto'
                },
                # Allow multiple files to be uploaded
                multiple=False
            ),
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


@app.callback(Output('embedding-graph', 'children'),
              [Input('upload-data', 'contents')],
              [State('upload-data', 'filename'),
               State('upload-data', 'last_modified')])
def update_figure(contents, filename, last_modified):
    if contents is not None:
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)

        copy_b64_to_bucket(decoded, filename, content_type)

        features = get_features_from_file(BytesIO(decoded), n_jobs=1)
        embeddings = get_embeddings(features, type='tsne', perplexity=60)
        figure = make_scatterplot(x=embeddings[:, 0], y=embeddings[:, 1])

        return html.Div([
            dcc.Graph(
                id='example-graph',
                figure=figure,
                style={'height': '80vh'}
            )
        ])



if __name__ == '__main__':
    application.run(host='0.0.0.0', debug=True, port=8080)
