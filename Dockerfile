FROM continuumio/miniconda3:4.5.4
RUN conda install -c conda-forge --quiet --yes \
    Python=3.6.8 \
    dash=0.37.0 \
    dash-core-components=0.43.1 \
    dash-html-components=0.13.5 \
    dash-table=3.4.0

COPY . /app
WORKDIR /app
EXPOSE 8080
CMD ["python", "application.py"]