FROM continuumio/miniconda3:4.5.11
RUN conda install -c conda-forge --quiet --yes \
    Python=3.6.8 \
    aubio=0.4.9 \
    yaafe=0.70 \
    librosa=0.6.3 \
    pandas=0.24.1 \
    numpy=1.16.1 \
    joblib=0.13.2 \
    matplotlib=3.0.2 \
    scikit-learn=0.20.2 \
    scipy=1.2.1 \
    boto3=1.9.107 \
    umap-learn=0.3.7 \
    sox=14.4.2

RUN pip install --no-cache-dir dash_audio_components dash_resumable_upload \
    dash==0.39.0 \
    dash-html-components==0.14.0 \
    dash-core-components==0.44 \
    dash-table==3.6.0 \
    plotly==3.6.1 \
    sox==1.3.7

COPY . /app
WORKDIR /app
EXPOSE 8080
CMD ["python", "application.py"]