# Command Line Interface

`audiocli` is a command line program that helps in extracting audio features and diemnsionality reduction. It's primary purpose is to build offline embeddings for the Audio Explorer. User can create a model with large volume of audio data and then use it to embed new audio files into that space. 

```bash
Usage: audiocli.py [OPTIONS] COMMAND [ARGS]...

Options:
  --quiet  Run in a silent mode
  --help   Show this message and exit.

Commands:
  a2f  Audio to HDF5 features
  f2m  Features to embedding model
  m2e  Model to embedddings
```

Following options are available:

##### a2f - Audio to Features

```bash
Usage: audiocli.py a2f [OPTIONS]

  Audio to HDF5 features

Options:
  -in, --input TEXT           Path to audio in WAV format.  [required]
  -out, --output TEXT         Output file or directory. If directory does not
                              exist it will be created. The output files will
                              have the same base name as input.
  -j, --jobs INTEGER          Number of jobs to run. Defaults to all cores
                              [default: -1]
  -c, --config PATH           Feature extractor config.
  -m, --multi                 Process audio files in parallel. The setting
                              will produce an HDF5 file per input, with the
                              same base name. Large memory footprint. If not
                              set, a single output file will be produced.
  -f, --format [fixed|table]  HDF5 format. Table is slightly slower and
                              requires pytables (will not work outside
                              Python), but allows to read specific columns.
  --help                      Show this message and exit.

```

Example:
```bash
./audiocli.py a2f --input data/raw/storm_petrels_16k/ --output data/features/features_02s/ --jobs 4 --config audioexplorer/algo_config.ini --multi --format table
```

The program loads complete file into memory, so watch out for memory usage 

##### f2m - Features to Model

```bash
Usage: audiocli.py f2m [OPTIONS]

  Features to embedding model

Options:
  -in, --input TEXT               Path to h5 features.  [required]
  -out, --output TEXT             Output directory.
  -j, --jobs INTEGER              Number of jobs to run  [default: -1]
  -a, --algo [umap|tsne|isomap|spectral|loclin|pca|kpca|fa|ica]
                                  Embedding to use
  -p, --grid PATH                 JSON with grid search parameters for the
                                  embedding algo
  --help                          Show this message and exit.
```

Example:

```bash
audiocli.py f2m --input data/features/features_02s/ --output data/models/ --jobs 6 --algo umap --grid data/umap_grid.json --select freq
```