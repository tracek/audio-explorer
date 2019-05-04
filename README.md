## Audio Explorer

[Audio Explorer](http://audioexplorer.online) helps in audio data discovery and labelling by utilising unsupervised machine learning, statistics and digital signal processing.

The program computes audio features per short fragments of submitted audio piece and then finds projection to 2-dimensional space by using linear or [non-linear dimensionality reduction](https://en.wikipedia.org/wiki/Nonlinear_dimensionality_reduction). Audio fragments are then represented as points; similar sample will be close together, while those which are different further apart. User can click on a point to play the audio fragment and inspect resulting [spectrogram](https://en.wikipedia.org/wiki/Spectrogram). 

- [Audio Explorer](#audio-explorer)
    + [Pre-alpha](#pre-alpha)
    + [Why build it?](#why-build-it-)
    + [How do we solve the problem?](#how-do-we-solve-the-problem-)
- [Details](#details)
    + [Building blocks](#building-blocks)
    + [Web application](#web-application)
      - [When user hits upload](#when-user-hits-upload)
      - [What to do next?](#what-to-do-next-)
    + [Command Line Interface](#command-line-interface)
    + [Audio features](#audio-features)
- [Development](#development)
- [Acknowledgement](#acknowledgement)
- [Licence](#licence)
- [Contact information](#contact-information)


#### Pre-alpha

The app is a work in progress, a pre-alpha. There are a number of features coming and some of the existing, including user workflow, will change. Once the audio embedding problem is better understood, I plan to hide or remove many of the algorithm-tweaking options, so the user should not ponder whether to use 256 or 512 FFT size. Good number of things can be done to improve User Experience.

#### Why build it?

Manual labelling of audio is time consuming and error prone. With this tool we aim to augment user by allowing to easily navigate recordings and label selected audio pieces. Instead of looking at raw audio, we extract number of audio features from each sample. The latter typically consists of dozens of calculated values (features), which would be impossible to visualise (e.g. 20 features per sample effectively means 20-dimensional space). Audio Explorer allows to compute over 100 features per audio fragment.

The main driver behind creation of this software were problems I faced when developing an algorithm to classify bird calls for the [Royal Society for the Protection of Birds](https://www.rspb.org.uk/). Accurate species classification is needed to estimate (change in) population size and therefore crucial for biodiversity monitoring.

#### How do we solve the problem?
We take the multidimensional space of computed audio features and project it to two dimensions, while retaining most of the information that describes the sample. That means that audio pieces that sound similar will be packed closely together, while those that sound quite different should be far apart. User can select cluster of similar-sounding samples and mark them.

## Worflow example

1. Tune the algorithm parameters or accept the defaults. 
2. Grab an audio file you want to analyse. If you don't have anything at hand, [here](https://s3.eu-central-1.amazonaws.com/audioexplorer-public/sthelena_example.mp3) is an audio that contains some bird calls, primarily storm petrels, recorded on St. Helena. Can you spot bird calls on the scatter plot? To download the recording, right-click on the link and select "save link as..." and then *Upload* it. Audio Explorer works with majority of popular audio formats, all thanks to [sox](http://sox.sourceforge.net).
3. Play with the parameters, add / remove features and see how it influences the plot by clicking *Apply*.
4. Click a point on the graph to hear the audio and see the spectrogram. Mind that what you hear and see is longer than selected `Sample length` by 0.4s. 0.2s margin is added to the beginning and end to get better impression of the sound surrounding.  
5. Calculated audio features can be inspected, sorted and filtered through custom-made query language by selecting _Table_ tab. You can use the following expressions: `<=`, `<`, `>=` and `>`, e.g. `> 2000`.
6. Use *Lasso select* (top right menu that appears after hovering over the graph) to select interesting cluster. The selection will be reflected in *Table*.
7. Download the selection from *Table*.

There will be more to enable user to label samples and clean from the noise. Coming soon!

## Details

This section goes into the inner-workings of the application.

#### Building blocks
The web application is made with Dash (Python + React) and is accompanied by a CLI (served through [click](https://click.palletsprojects.com/en/7.x/)). The web app is deployed with AWS Elastic Beanstalk (Docker deployment) and is supported by the following AWS services: EC2, S3, RDS, Secrets Manager, Route 53 and CloudWatch. 

#### Web application

The web app is hosted on AWS. It scales to up to 3 instances and uses `nginx` load balancer. The traffic is secured and managed though Route 53. AWS provides a certificate too. The code repository contains complete load balancer configuration required to run the app in the wild. 

Elastic Beanstalk automatically handles the details of capacity provisioning, load balancing, scaling, and application health monitoring.

##### When user hits upload

What's happening behind the scences when user hits upload: 
1. The audio file gets uploaded to the EC2 instance.
2. The file is converted to mono 16 bits per sample Waveform Audio File Format (WAV) and uploaded to S3. We'll be serving audio from a signed S3 url (private bucket). Mind that the audio is stored, so don't upload anything confidential. In parallel, next step is executed.
3. Search for audio onsets according to supplied parameters. The onset detection can be disabled to process complete file. 
4. Compute selected audio features per each audio fragment.
5. Run embedding algorithm over computed features and plot them. Each audio fragment becomes a point on the scatter plot that user can click to inspect spectrogram and play the audio.
6. The algorithm parameters and user IP is stored in a database.


#### Command Line Interface

`audiocli` is a command line program that helps in extracting audio features and diemnsionality reduction. It's primary purpose is to build offline embeddings for the Audio Explorer. User can create a model with large volume of audio data and then use it to embed new audio files into that space.   

#### Audio features

Given audio fragment, thee following features are computed:
* Frequency statistics: mean, median, first, third and inter quartile 
* Pitch statistics: mean, median, first, third and inter quartile
* [Chroma](https://en.wikipedia.org/wiki/Chroma_feature): short-term pitch profile 
* Linear Predictor Coefficients ([LPC](https://en.wikipedia.org/wiki/Linear_predictive_coding))
* Line Spectral Frequency ([LSF](https://en.wikipedia.org/wiki/Line_spectral_pairs)) coefficients 
* Mel-Frequency Cepstral Coefficients ([MFCC](https://en.wikipedia.org/wiki/Mel-frequency_cepstrum))
* Octave Band Signal Intensity (OBSI)
* [Spectral crest factor per band](https://en.wikipedia.org/wiki/Crest_factor)
* Decrease: average spectral slope
* Flatness: spectral flatness using the ratio between geometric and arithmetic mean
* Flux: flux of spectrum between consecutives frames
* Rolloff: frequency so that 99% of the energy is contained below
* Variation: normalized correlation of spectrum between consecutive frames


## Development

See [CONTRIBUTING](CONTRIBUTING.md).


## Acknowledgement

My special thanks to:
* AWS Cloud Credits for Research for supporting the project! Thanks to AWS I could rapidly prototype the models and the app itself. 
* My colleagues from RSPB who have supplied the audio recordings and supported along the way.


## Licence

Audio Explorer is released under the version 3 of the GNU General Public License. Read COPYING for more details. The project is and will remain open source - that's a promise. 

## Contact information 

Please send any questions and feedback to:

```bash
python -c 'import base64; print(base64.b64decode("bHVrYXN6LnRyYWNld3NraUBvdXRsb29rLmNvbQ=="))'
```