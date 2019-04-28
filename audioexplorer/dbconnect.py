import sqlalchemy as db
from settings import DB_ENGINE, DB_USER, DB_DATABASE_NAME, DB_HOSTNAME, DB_PASSWORD

engine = db.create_engine(f'{DB_ENGINE}://{DB_USER}:{DB_PASSWORD}@{DB_HOSTNAME}/{DB_DATABASE_NAME}')
metadata = db.MetaData(bind=engine, reflect=True)

def insert_user(user_dict: dict):
    users = metadata.tables['users']
    users.insert().values(**user_dict).execute()