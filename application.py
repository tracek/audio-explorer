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

import os
import uuid
import re
import operator
import boto3
import dash
import dash_table
import dash_audio_components
import dash_upload_components
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import numpy as np
import pandas as pd
import urllib.parse
import noisereduce as nr
from datetime import datetime
from flask import request
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from botocore.client import Config

from settings import S3_BUCKET, AWS_REGION, SERVE_LOCAL, SAMPLING_RATE, AUDIO_MARGIN, TEMP_STORAGE
from audioexplorer.features import get, FEATURES
from audioexplorer.embedding import get_embeddings, EMBEDDINGS
from audioexplorer import audio_io
from audioexplorer import visualize
from audioexplorer import session_log
from audioexplorer import filters

if SERVE_LOCAL: # Play audio from the local machine
    import simpleaudio as sa

app = dash.Dash(__name__, external_stylesheets=['https://codepen.io/chriddyp/pen/bWLwgP.css',
                                                "https://codepen.io/chriddyp/pen/brPBPO.css"])
app.config['suppress_callback_exceptions']=True
dash_upload_components.decorate_server(app.server, TEMP_STORAGE)
server = app.server

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


def named_slider(id, min, max, value, step=None, marks=None, slider_type=dcc.Slider, hidden=False):
    div = html.Div([
        html.Div(id=f'name-{id}', hidden=hidden),
        slider_type(
            id=id,
            min=min,
            max=max,
            marks=marks,
            step=step,
            value=value,
        )],
        style={'margin': '25px 5px 30px 0px'},
        hidden=hidden,
        id=f'slidercontainer-{id}'
    )
    return div


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
    s3_client = boto3.client('s3', region_name=AWS_REGION, config=Config(signature_version='s3v4'))
    url = s3_client.generate_presigned_url('get_object', Params={'Bucket': S3_BUCKET, 'Key': key}, ExpiresIn=3600)
    return url


def map_parameters(embedding_type, value):
    if embedding_type in ['umap', 'isomap']:
        return {'n_neighbors': value}
    elif embedding_type == 'tsne':
        return {'perplexity': value}
    return {}


def get_user_ip():
    if request.headers.getlist("X-Forwarded-For"):
        user_ip = request.headers.getlist("X-Forwarded-For")[0]
    else:
        user_ip = request.remote_addr
    if ',' in user_ip:
        user_ip = user_ip.split(',')[0]
    return user_ip


def resolve_filtering_expression(df: pd.DataFrame, filter_expression: str):
    condition = None
    ops = {
        ">": operator.gt,
        "<": operator.lt,
        ">=": operator.ge,
        "<=": operator.le
    }
    match = re.search('|'.join(ops.keys()), filter_expression)
    if match:
        operator_s = filter_expression[match.start(): match.end()]
        col_name = filter_expression[:match.start()].replace('\"', '').replace(' ', '')
        filter_value = float(filter_expression[match.end() + 1:])
        condition = ops[operator_s](df[col_name], filter_value)
    return condition


def log_user_action(action_type, datetime, session_id, filename=None, embedding_type=None, fftsize=None, bandpass=None,
                    onset_threshold=None, sample_len=None, selected_features=None):
    user_ip = get_user_ip()
    agent = request.headers.get('User-Agent')
    user_data = session_log.insert_user(
        action_type=action_type,
        datetime=datetime,
        session_id=session_id,
        filename=filename,
        agent=agent,
        user_ip=user_ip,
        embedding_type=embedding_type,
        fftsize=fftsize,
        bandpass=bandpass,
        onset_threshold=onset_threshold,
        sample_len=sample_len,
        selected_features=selected_features,
    )
    return user_data


def relayout_autosize_triggered():
    res = False
    triggers = dash.callback_context.triggered
    if len(triggers) == 1:
        relayout_event = triggers[0].get('prop_id') == 'spectrogram-full-graph.relayoutData'
        if relayout_event:
            res = True if triggers[0].get('value').get('autosize') else False
    return res


def relayout_range_change_triggered():
    res = False
    triggers = dash.callback_context.triggered
    if len(triggers) == 1:
        relayout_event = triggers[0].get('prop_id') == 'spectrogram-full-graph.relayoutData'
        if relayout_event:
            res = True if triggers[0].get('value').get('xaxis.range[0]') else False
    return res


def event_triggered(event, option=None):
    res = False
    triggers = dash.callback_context.triggered
    if len(triggers) == 1:
        res = True if triggers[0].get('prop_id') == event else False
        if option and res:
            res = True if triggers[0].get('value').get(option) else False
    return res


@app.callback(Output('dummy-div', 'children'),
              [Input('sessionid-store', 'data')])
def login(session_id):
    log_user_action(
        action_type='Login',
        datetime=datetime.now().strftime("%Y-%m-%d_%H:%M:%S"),
        session_id=session_id
    )
    raise PreventUpdate


@app.callback(Output('features-container', 'children'),
              [Input('feature-store', 'data')])
def show_features_in_table(data):
    if data is None:
        raise PreventUpdate

    feature_table = dash_table.DataTable(
        id='features-table',
        columns=[{'name': i, 'id': i} for i in data[0].keys()],
        data=data,
        pagination_settings={'page_size': 20, 'current_page': 0},
        pagination_mode='be',
        filtering='be',
        filtering_settings='',
        sorting='be',
        sorting_type='multi',
        sorting_settings=[]
    )
    return feature_table


@app.callback(Output('features-table', "data"),
             [Input('feature-store', 'data'),
              Input('embedding-graph', 'selectedData'),
              Input('features-table', "pagination_settings"),
              Input('features-table', "sorting_settings"),
              Input('features-table', "filtering_settings")])
def update_table(data, select_data, pagination_settings, sorting_settings, filtering_settings):
    filtering_expressions = filtering_settings.split(' && ')
    df = pd.DataFrame(data)
    if select_data:
        selected_points = [point['pointIndex'] for point in select_data['points']]
        df = df.loc[selected_points]
    for filter_expression in filtering_expressions:
        condition = resolve_filtering_expression(df=df, filter_expression=filter_expression)
        if condition is not None:
            df = df.loc[condition]

    if len(sorting_settings):
        df = df.sort_values(
            [col['column_id'] for col in sorting_settings],
            ascending=[
                col['direction'] == 'asc'
                for col in sorting_settings
            ],
            inplace=False
        )

    return df.iloc[
        pagination_settings['current_page']*pagination_settings['page_size']:
        (pagination_settings['current_page'] + 1)*pagination_settings['page_size']
    ].to_dict('records')


@app.callback(Output('div-download-table', 'children'),
             [Input('div-download-explore', 'children')])
def update_download_link(link):
    return link


@app.callback(Output('div-download-explore', 'children'),
              [Input('embedding-graph', 'selectedData'),
               Input('input-filename', 'value'),
               Input('feature-store', 'data')],
              [State('filename-store', 'data')])
def update_download_link_explore(select_data, user_input_filename, data, original_filename):
    if data and (user_input_filename or original_filename):
        df = pd.DataFrame(data)
        if select_data:
            selected_points = [point['pointIndex'] for point in select_data['points']]
            df = df.loc[selected_points].reindex()
            text = f"Download {len(selected_points)} out of {len(data)} points"
        else:
            text = f'Download all'

        csv_string = df.to_csv(index=False, encoding='utf-8')
        csv_string = "data:text/csv;charset=utf-8," + urllib.parse.quote(csv_string)

        if user_input_filename:
            filename = user_input_filename + '.csv'
        else:
            filename = original_filename + '.csv'

        download_button = html.A(
            text,
            id='download-link-explore',
            download=filename,
            href=csv_string,
            target="_blank",
        )
        return download_button


@app.callback(Output('input-filename', 'value'),
              [Input('upload-data', 'fileNames')])
def update_input_filename(filenames):
    if filenames is not None:
        filename = os.path.splitext(filenames[-1])[0]
        return filename


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


@app.callback(Output('mapping-store', 'data'),
              [Input('upload-data', 'fileNames')])
def create_file_key_mapping(filenames):
    if filenames is not None:
        user_ip = get_user_ip()
        filepath = TEMP_STORAGE + filenames[-1]
        time_now = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
        filename, ext = os.path.splitext(os.path.basename(filepath))
        key = f'{filename}_{time_now}_{user_ip}.wav'
        return {'key': key, 'filepath': filepath, 'time': time_now}
    else:
        raise PreventUpdate


@app.callback(Output('filename-store', 'data'),
              [Input('mapping-store', 'data')])
def convert(mapping):
    audio_io.convert_to_wav(input_path=mapping['filepath'], output_path=TEMP_STORAGE + mapping['key'])
    return mapping['key']


@app.callback(Output('userdata-store', 'data'),
             [Input('mapping-store', 'data'),
              Input('apply-button', 'n_clicks')],
             [State('algorithm-dropdown', 'value'),
              State('fft-size', 'value'),
              State('bandpass', 'value'),
              State('onset-threshold', 'value'),
              State('sample-len', 'value'),
              State('features-selection', 'values'),
              State('sessionid-store', 'data')])
def log_user_action_cb(mapping, apply_clicks, embedding_type, fftsize, bandpass, onset_threshold, sample_len,
                       selected_features, session_id):
    if apply_clicks:
        action_type = 'Reload'
        time = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
    else:
        action_type = 'Upload'
        time = mapping['time']

    user_data = log_user_action(
        action_type=action_type,
        datetime=time,
        session_id=session_id,
        filename=mapping['key'],
        embedding_type=embedding_type,
        fftsize=fftsize,
        bandpass=bandpass,
        onset_threshold=onset_threshold,
        sample_len=sample_len,
        selected_features=selected_features
    )

    return user_data


@app.callback(Output('signed-url-store', 'data'),
              [Input('filename-store', 'data')])
def upload_to_s3(filename):
    if filename is not None:
        filepath = TEMP_STORAGE + filename
        if not SERVE_LOCAL:
            copy_file_to_bucket(filepath, filename)
            url = generate_signed_url(filename)
            return url
        else:
            return filepath
    else:
        raise PreventUpdate


@app.callback([Output('embedding-graph', 'figure'),
               Output('feature-store', 'data'),
               Output('div-report-selection', 'children'),
               Output('div-report-selection', 'style')],
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
        filepath = TEMP_STORAGE + filename
        lowpass, highpass = bandpass
        min_duration = sample_len - 0.05
        fs, X = audio_io.read_wave_local(filepath)
        features = get(X, fs, n_jobs=1, selected_features=selected_features, lowcut=lowpass, highcut=highpass,
                       block_size=fftsize, onset_detector_type='hfc', onset_silence_threshold=-90,
                       onset_threshold=onset_threshold, min_duration_s=min_duration,    sample_len=sample_len)

        params = map_parameters(embedding_type, neighbours)

        style = {'display': 'inline-block', 'margin-left': 'auto',
                 'margin-right': '20px', 'float': 'right'}

        try:
            embeddings, algo, msg = get_embeddings(
                data=features.drop(columns=['onset', 'offset']),
                type=embedding_type, n_jobs=1,
                **params)

            # features.insert(0, column='filename', value=filenames[-1])
            extra_data = ['onset', 'offset']
            if 'freq_mean' in features:
                mean_freq = features['freq_mean'].astype(int).astype(str) + ' Hz'
            elif 'pitch_median' in features:
                mean_freq = features['pitch_median'].astype(int).astype(str) + ' Hz'
            else:
                mean_freq = None
            figure = visualize.scatter_plot(x=embeddings[:, 0], y=embeddings[:, 1],
                                            customdata=features[extra_data],
                                            text=mean_freq)

            if msg is None:
                msg = f'Found {len(embeddings)} samples'
            else:
                style['color'] = 'red'

            return figure, features.round(2).to_dict(orient='rows'), msg, style
        except Exception as ex:
            style['color'] = 'red'
            return go.Figure(), None, str(ex), style
    else:
        raise PreventUpdate


@app.callback(Output('audio-player', 'overrideProps'),
              [Input('embedding-graph', 'clickData')],
              [State('signed-url-store', 'data')])
def update_player_status(click_data, url):
    if click_data:
        start, end = click_data['points'][0]['customdata']
        if SERVE_LOCAL:
            wav = audio_io.read_wav_part_from_local(url, start - AUDIO_MARGIN, end + AUDIO_MARGIN)
            sa.play_buffer(wav, 1, 2, SAMPLING_RATE)
            raise PreventUpdate
        else:
            return {'autoPlay': True,
                    'src': url,
                    'from_position': start - AUDIO_MARGIN,
                    'to_position': end + AUDIO_MARGIN}
    else:
        raise PreventUpdate


@app.callback(Output('div-spectrogram', 'children'),
              [Input('embedding-graph', 'clickData'),
               Input('embedding-graph', 'selectedData'),
               Input('apply-button', 'n_clicks'),
               Input('filename-store', 'data')],
               [State('bandpass', 'value')])
def display_click_image(click_data, select_data, n_clicks, url, bandpass):
    if url:
        lowcut, higcut = bandpass
        if click_data is not None and event_triggered('embedding-graph.clickData'):
            start, end = click_data['points'][0]['customdata']
            wav = audio_io.read_wav_part_from_local(
                path=TEMP_STORAGE + url,
                start_s=start - AUDIO_MARGIN,
                end_s=end + AUDIO_MARGIN
            )
            wav = filters.frequency_filter(wav, fs=SAMPLING_RATE, lowcut=lowcut, highcut=higcut)
            im = visualize.specgram_base64(y=wav, fs=SAMPLING_RATE, start=start, end=end, margin=AUDIO_MARGIN)

            return html.Img(
                src='data:image/png;base64, ' + im,
                style={
                    'height': '25vh',
                    'display': 'block',
                    'margin': 'auto'
                }
            )
        else:
            if select_data is not None:
                onsets = [point['customdata'] for point in select_data['points']]
                wavs = audio_io.read_wav_parts_from_local(path=TEMP_STORAGE + url, onsets=onsets)
                wavs = np.concatenate(wavs)
            else:
                fs, wavs = audio_io.read_wave_local(TEMP_STORAGE + url)

            wavs = filters.frequency_filter(wavs, fs=SAMPLING_RATE, lowcut=lowcut, highcut=higcut)
            fig = visualize.power_spectrum(wavs, fs=SAMPLING_RATE)
            return dcc.Graph(id='spectrum', figure=fig)
    else:
        raise PreventUpdate


@app.callback(Output('spectrogram-full-graph', 'figure'),
             [Input('embedding-graph', 'selectedData'),
              Input('filename-store', 'data'),
              Input('spectrogram-full-graph', 'relayoutData'),
              Input('apply-button', 'n_clicks')],
             [State('bandpass', 'value'),
              State('feature-store', 'data'),
              State('spectrogram-full-graph', 'figure')])
def full_spectrogram_graph(select_data, url, selection, n_clicks, bandpass, features, fig):
    if url is not None:
        if relayout_autosize_triggered():
            raise PreventUpdate
        temp_path = f'/tmp/{os.path.splitext(url)[0]}'
        spectrum_path = temp_path + '_spectrum.npy'
        time_path = temp_path + '_time.npy'

        if select_data and event_triggered('embedding-graph.selectedData'):
            start = fig['data'][0]['x'][0]
            end = fig['data'][0]['x'][-1]
            onsets = [point['customdata'] for point in select_data['points']]
            shapes = visualize.shapes_from_onsets(onsets, x_min=start, x_max=end, color='red')
            fig['layout']['shapes'] = shapes
        elif selection is not None and 'xaxis.range[0]' in selection and 'xaxis.range[1]' in selection:
            start = selection['xaxis.range[0]']
            end = selection['xaxis.range[1]']
            Sxx = np.load(spectrum_path)
            time = np.load(time_path)
            fig = visualize.spectrogram_shaded(S=Sxx, time=time, fs=SAMPLING_RATE, start_time=start, end_time=end)
        elif os.path.exists(spectrum_path) and not event_triggered('apply-button.n_clicks'):
            Sxx = np.load(spectrum_path)
            time = np.load(time_path)
            fig = visualize.spectrogram_shaded(S=Sxx, time=time, fs=SAMPLING_RATE)
        else:
            fs, y = audio_io.read_wave_local(TEMP_STORAGE + url)
            lowcut, higcut = bandpass
            y = filters.frequency_filter(y, fs=SAMPLING_RATE, lowcut=lowcut, highcut=higcut)
            freq, time, Sxx = visualize.calculate_spectrogram(y, fs, backend='yaafe')
            np.save(spectrum_path, Sxx)
            np.save(time_path, time)
            fig = visualize.spectrogram_shaded(S=Sxx, time=time, fs=SAMPLING_RATE)

        return fig
    else:
        raise PreventUpdate


@app.callback(Output('reduce-noise-container', 'children'),
             [Input('embedding-graph', 'selectedData')])
def update_table(select_data):
    if select_data:
        return html.Button('Remove selected frequencies', id='reduce-noise-button')


@app.callback(Output('apply-button', 'n_clicks'),
             [Input('reduce-noise-button', 'n_clicks')],
             [State('filename-store', 'data'),
              State('embedding-graph', 'selectedData')]
)
def reduce_noise(click, url, select_data):
    if url is not None and select_data is not None:
        fs, y = audio_io.read_wave_local(TEMP_STORAGE + url)
        onsets = [point['customdata'] for point in select_data['points']]
        noises = [y[int(start_s * fs): int(end_s * fs)] for start_s, end_s in onsets]
        noises = np.concatenate(noises)
        y = nr.reduce_noise(audio_clip=y, noise_clip=noises)
        audio_io.save_wav(y, fs, path=TEMP_STORAGE + url)
        return 1


def generate_layout():
    session_id = str(uuid.uuid4())
    div = html.Div([
        dcc.Tabs(id='tabs', children=[
            dcc.Tab(label='Explore', children=[
                html.Div(
                    className="container",
                    style={
                        'width': '92%',
                        'max-width': 'none',
                        'font-size': '1.5rem',
                        'padding': '10px 10px'
                    },
                    children=[
                        dcc.Store(id='signed-url-store', storage_type='memory'),
                        dcc.Store(id='feature-store', storage_type='memory'),
                        dcc.Store(id='filename-store', storage_type='memory'),
                        dcc.Store(id='mapping-store', storage_type='memory'),
                        dcc.Store(id='userdata-store', storage_type='memory'),
                        dcc.Store(id='sessionid-store', storage_type='memory', data=session_id),
                        html.Div(id='dummy-div', style={'display': 'none'}),

                        # Body
                        html.Div(className="row", children=[
                            html.Div(className="eight columns", children=[
                                dcc.Graph(
                                    id='embedding-graph',
                                    style={'height': '90vh'}
                                ),
                                dash_audio_components.DashAudioComponents(
                                    id='audio-player',
                                    style={'width': '90%'},
                                    src='',
                                    autoPlay=True,
                                    controls=False
                                ),
                                html.Div(className='row', children=[
                                    html.Div(className='seven columns', children=[
                                        dcc.Input(id='input-filename', type='text', debounce=True,
                                                  placeholder='Filename',
                                                  style={'display': 'inline-block', 'width': '340px',
                                                         'margin-right': '30px'}),
                                        html.Div(id='div-download-explore',
                                                 style={'display': 'inline-block', 'margin-right': '60px'}),
                                    ]),
                                    html.Div(className='five columns', children=[
                                        html.Div(id='div-report-selection')
                                    ])
                                ])
                            ]),
                            html.Div(className="four columns", children=[
                                html.Div([
                                    dash_upload_components.Upload(
                                        id='upload-data',
                                        maxFiles=1,
                                        simultaneousUploads=3,
                                        chunkSize=4 * 1024 * 1024,
                                        maxFileSize=5 * 1024 * 1024 * 500,  # 500 MB
                                        service="/upload_resumable",
                                        textLabel="UPLOAD",
                                        startButton=False,
                                        pauseButton=False,
                                        cancelButton=False,
                                        defaultStyle=upload_style,
                                        activeStyle=upload_style,
                                        completeStyle=upload_style,
                                        completedMessage='UPLOAD'
                                    ),
                                    html.Button('Apply', id='apply-button', style=upload_style),
                                ], style={'columnCount': 2}),
                                dcc.Dropdown(
                                    id='algorithm-dropdown',
                                    options=[{'label': label, 'value': value} for value, label in EMBEDDINGS.items()],
                                    placeholder='Select embedding',
                                    value='umap'
                                ),
                                html.H4('Parameters'),
                                dcc.Checklist(
                                    id='features-selection',
                                    options=[{'label': label, 'value': value} for value, label in FEATURES.items()],
                                    values=['freq'],
                                    labelStyle={'display': 'inline-block', 'margin': '6px'}
                                ),
                                named_slider(
                                    id='fft-size',
                                    min=2 ** 7,
                                    max=2 ** 11,
                                    marks={i: f'{i}' for i in [2 ** i for i in range(7, 12)]},
                                    value=2 ** 9
                                ),
                                named_slider(
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
                                named_slider(
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
                                named_slider(
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
                                named_slider(
                                    id='embedding-neighbours',
                                    min=5,
                                    max=100,
                                    step=5,
                                    marks={
                                        5: '5',
                                        20: '20',
                                        50: '50',
                                        100: '100'
                                    },
                                    value=20
                                ),
                                html.Div(id='div-spectrogram', style={'margin-top': '20px'}),
                                html.Div(id='reduce-noise-container', style={'margin-top': '20px'})
                            ]),
                        ]),
                    ]
                )
            ]),
            dcc.Tab(label='Profile', children=[
                html.Div(
                    children=html.Div(
                        className="container",
                        style={
                            'width': '95%',
                            'max-width': 'none',
                            'font-size': '1.5rem',
                            'padding': '10px 30px'
                        },
                        children=[
                            dcc.Graph(
                                id='spectrogram-full-graph'
                            ),
                        ]
                    )
                ),
            ]),
            dcc.Tab(label='Table', children=[
                html.Div(
                    children=html.Div(
                        className="container",
                        style={
                            'width': '95%',
                            'max-width': 'none',
                            'font-size': '1.5rem',
                            'padding': '10px 30px'
                        },
                        children=[
                            html.Div(id='features-container'),
                            html.Div(id='div-download-table')
                        ]
                    )
                ),
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
    return div


app.layout = generate_layout()


if __name__ == '__main__':
    app.run_server(debug=True, port=8080)
