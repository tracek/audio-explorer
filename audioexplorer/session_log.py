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

import json
import ipinfo
import httpagentparser
import sqlalchemy as db
import boto3
from functools import lru_cache
from settings import DB_ENGINE, DB_USER, DB_DATABASE_NAME, DB_HOSTNAME, DB_PASSWORD, AWS_REGION, SERVE_LOCAL


def insert_user(datetime, filename, agent, user_ip, embedding_type, fftsize, bandpass, onset_threshold, sample_len,
                selected_features, action_type, session_id):
    # if not SERVE_LOCAL:
    user_os, browser = httpagentparser.simple_detect(agent)
    engine = db.create_engine(f'{DB_ENGINE}://{DB_USER}:{DB_PASSWORD}@{DB_HOSTNAME}/{DB_DATABASE_NAME}')
    metadata = db.MetaData(bind=engine, reflect=True)

    d = {'datetime': datetime,
         'user_os': user_os,
         'user_browser': browser,
         'user_ip': user_ip,
         'filename': filename,
         'embedding_type': embedding_type,
         'fft_size': fftsize,
         'filter_lowpass': bandpass[0] if bandpass else None,
         'filter_highpass': bandpass[1] if bandpass else None,
         'onset_threshold': onset_threshold,
         'sample_len': sample_len,
         'selected_features': ','.join(selected_features) if selected_features else None,
         'user_action_type': action_type,
         'user_session_id': session_id}

    extra_ip_info = get_ipinfo(user_ip)
    d.update(extra_ip_info)
    users = metadata.tables['users']
    conn = users.insert().values(**d).execute()
    conn.close()

    return d


# def first_session(session_id):
#     text = db.text('user_session_id = :uuid')
#     text = text.bindparams(uuid=session_id)
#     users = metadata.tables['users']
#     r = users.select(text).execute().fetchone()
#     if r:
#         return False
#     else:
#         return True


@lru_cache(maxsize=100)
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