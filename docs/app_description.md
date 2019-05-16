## Audio Explorer

Copyright 2019 Lukasz Tracewski

Audio Explorer helps in audio data discovery and labelling by utilising unsupervised and supervised machine learning - and good deal of statistics with digital signal processing.

The program computes audio features per short fragments of submitted audio piece and then finds projection to 2-dimensional space by using linear or [non-linear dimensionality reduction](https://en.wikipedia.org/wiki/Nonlinear_dimensionality_reduction). Audio fragments are then represented as points; similar sample will be close together, while those which are different further apart. User can click on a point to play the audio fragment and inspect resulting [spectrogram](https://en.wikipedia.org/wiki/Spectrogram). 

### Why build it?

Manual labelling of audio is time consuming and error prone. With this tool we aim to augment user by allowing to easily navigate recordings and label selected audio pieces. Instead of looking at raw audio, we extract number of audio features from each sample. The latter typically consists of dozens of calculated values (features), which would be impossible to visualise (e.g. 20 features per sample effectively means 20-dimensional space). Audio Explorer allows to compute over 100 features per audio fragment.

### Worflow 

1. Tune the algorithm parameters or accept the defaults. 
2. Upload an audio file you want to analyse. If you don't have anything at hand, [here](https://s3.eu-central-1.amazonaws.com/audioexplorer-public/sthelena_example.mp3) is an audio that contains some bird calls, primarily storm petrels, recorded on St. Helena. Can you spot bird calls on the scatter plot? To download the recording, right-click on the link and select "save link as..." and then *Upload* it. Audio Explorer works with majority of popular audio formats, all thanks to [sox](http://sox.sourceforge.net).
3. Play with the parameters, add / remove features and see how it influences the plot by clicking *Apply*.
4. Click a point on the graph to hear the audio and see the spectrogram. Mind that what you hear and see is longer than selected `Sample length` by `0.4s`. `0.2s` margin is added to the beginning and end to get better impression of the sound surrounding.  
5. Calculated audio features can be inspected, sorted and filtered through custom-made query language by selecting _Table_ tab. You can use the following expressions: `<=`, `<`, `>=` and `>`, e.g. `> 2000`.
6. Use *Lasso select* (top right menu that appears after hovering over the graph) to select interesting cluster. The selection will be reflected in *Table*.
7. For the selected audio fragments a power spectrum will be plotted (units: Voltage<sup>2</sup>), scaled to dB.
8. Now that we have frequencies present in the selected fragments, user can decide to reduce presence of these frequencies in rest of the audio.  
9. Once you're happy with the selection, you can download the data from *Table*.


### Audio features

Given audio fragment, we compute the following features:
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

**Don't know what to choose**? Accept the default. 


### How do we solve the problem?
We take the multidimensional space of computed audio features and project it to two dimensions, while retaining most of the information that describes the sample. Audio pieces that sound similar will be packed closely together, while those that sound quite different should be far apart. User can select cluster of similar-sounding samples and mark them.

### What am I looking at?
The scatter plot is the result of running the dimensionality reduction algorithms on audio recordings resulting in a 2D visualization of the dataset. Each data point is a short sample retrieved from audio. 


#### Dimensionality reduction
Dimensionality reduction techniques reduce number of variables by projecting them to a lower-dimensional space. The aim in our case is to retain as much as possible of original information, while enjoying exploration of the data in much in familiar 2D space. We're looking at following methods:
* [Uniform Manifold Approximation and Projection](https://arxiv.org/pdf/1802.03426)
* [t-Distributed Stochastic Neighbor embedding](https://en.wikipedia.org/wiki/T-distributed_stochastic_neighbor_embedding)
* [Principal Component Analysis](https://en.wikipedia.org/wiki/Principal_component_analysis)
* [Kernel Principal Component Analysis](https://en.wikipedia.org/wiki/Kernel_principal_component_analysis)
* [Factor Analysis](https://en.wikipedia.org/wiki/Factor_analysis)
* [Independent Component Analysis](https://en.wikipedia.org/wiki/Independent_component_analysis)
* [Isomap: Isometric Mapping](https://en.wikipedia.org/wiki/Isomap)
* [Spectral embedding](https://en.wikipedia.org/wiki/Spectral_clustering)
* [Locally Linear Embedding](https://cs.nyu.edu/~roweis/lle/papers/lleintro.pdf)


#### Spectrogram
A spectrogram is a visual representation of the spectrum of frequencies of a signal as it varies with time. For each selected sample in the graph we plot spectogram of the respective audio. It allows further verification of similarity between samples as well as provide insights into frequency structure of the signal.
 

