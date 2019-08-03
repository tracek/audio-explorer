FROM continuumio/miniconda3:4.6.14

RUN apt-get update && apt-get install -y sox libsox-fmt-mp3

RUN conda install -c conda-forge --quiet --yes \
    Python=3.6.8 \
    aubio=0.4.9 \
    yaafe=0.70 \
    librosa=0.7.0 \
    pandas=0.25 \
    numpy=1.17.0 \
    joblib=0.13.2 \
    matplotlib=3.1.1 \
    scikit-learn=0.21.3 \
    scipy=1.3.0 \
    boto3=1.9.200 \
    umap-learn=0.3.9 \
    python-dotenv=0.10.3 \
    sqlalchemy=1.3.6 \
    psycopg2=2.8.3 \
    datashader=0.7.0 \
    gunicorn=19.9.0


RUN pip install --no-cache-dir httpagentparser \
    ipinfo \
    dash_audio_components \
    dash_upload_components \
    noisereduce \
    sox==1.3.7 \
    dash==1.0.2 \
    dash-table==4.0.2

COPY . /app
WORKDIR /app
EXPOSE 8080
CMD ["gunicorn", "-w", "8", "-b", "0.0.0.0:8080", "application:server"]