import os
import dash
import dash_audio_components
import dash_core_components as dcc
import dash_html_components as html

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


if __name__ == '__main__':
    application.run(host='0.0.0.0', debug=True, port=8080)
