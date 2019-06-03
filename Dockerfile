FROM continuumio/miniconda3:4.6.14

RUN apt-get update && apt-get install -y sox libsox-fmt-mp3

RUN conda install -c conda-forge --quiet --yes \
    Python=3.6.8 \
    aubio=0.4.9 \
    yaafe=0.70 \
    librosa=0.6.3 \
    pandas=0.24.2 \
    numpy=1.16.3 \
    joblib=0.13.2 \
    matplotlib=3.1.0 \
    scikit-learn=0.21.2 \
    scipy=1.3.0 \
    boto3=1.9.155 \
    umap-learn=0.3.8 \
    python-dotenv=0.10.2 \
    sqlalchemy=1.3.3 \
    psycopg2=2.8.2 \
    datashader=0.7.0 \
    gunicorn=19.9.0


RUN pip install --no-cache-dir httpagentparser \
    ipinfo \
    dash_audio_components \
    dash_upload_components \
    noisereduce \
    sox==1.3.7 \
    dash==0.43 \
    dash-table==3.7.0

COPY . /app
WORKDIR /app
EXPOSE 8080
CMD ["gunicorn", "-w", "8", "-b", "0.0.0.0:8080", "application:server"]