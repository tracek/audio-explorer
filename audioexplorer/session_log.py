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

import json
import uuid
import ipinfo
import httpagentparser
import sqlalchemy as db
import boto3
from functools import lru_cache
from settings import DB_ENGINE, DB_USER, DB_DATABASE_NAME, DB_HOSTNAME, DB_PASSWORD, AWS_REGION

engine = db.create_engine(f'{DB_ENGINE}://{DB_USER}:{DB_PASSWORD}@{DB_HOSTNAME}/{DB_DATABASE_NAME}')
metadata = db.MetaData(bind=engine, reflect=True)
session_id = str(uuid.uuid4())


def insert_user(datetime, filename, agent, user_ip, embedding_type, fftsize, bandpass, onset_threshold, sample_len,
                selected_features, action_type):
    user_os, browser = httpagentparser.simple_detect(agent)

    d = {'datetime': datetime,
         'user_os': user_os,
         'user_browser': browser,
         'user_ip': user_ip,
         'filename': filename,
         'embedding_type': embedding_type,
         'fft_size': fftsize,
         'filter_lowpass': bandpass[0],
         'filter_highpass': bandpass[1],
         'onset_threshold': onset_threshold,
         'sample_len': sample_len,
         'selected_features': ','.join(selected_features),
         'user_action_type': action_type,
         'user_session_id': session_id}

    extra_ip_info = get_ipinfo(user_ip)
    d.update(extra_ip_info)
    users = metadata.tables['users']
    users.insert().values(**d).execute()
    return d


@lru_cache(maxsize=1)
def get_ipinfo(ip_address: str) -> dict:
    apikey = get_ipinfo_secret()
    ipinfo_handler = ipinfo.getHandler(apikey)
    details = ipinfo_handler.getDetails(ip_address).all
    d = {'user_hostname': details.get('hostname', None),
         'user_city': details.get('city', None),
         'user_region': details.get('region', None),
         'user_country_code': details.get('country', None),
         'user_country_name': details.get('country_name', None),
         'user_latitude': details.get('latitude', None),
         'user_longitude': details.get('longitude', None),
         'user_loc': details.get('loc', None),
         'user_org': details.get('org', None)}

    return d


@lru_cache(maxsize=1)
def get_ipinfo_secret() -> str:
    secret_name = "audioexplorer/ipinfo"

    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=AWS_REGION
    )

    secret = client.get_secret_value(
        SecretId=secret_name
    )

    api_key = json.loads(secret['SecretString'])['IPINFO_TOKEN']
    return api_key