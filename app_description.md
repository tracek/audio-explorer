### Why Audio Explorer
Manual labelling of audio is time consuming and error prone. With this tool we aim to augument operator by allowing to easily navigate recordings and label selected audio pieces. Instead of looking at raw audio, we extract number of audio features from each sample. The latter typically consists of dozens of calculated values (features), which would be impossible to visualise (e.g. 20 features per sample effectively means 20-dimensional space). 

### How do we solve the problem
We take the multidimensional space of computed audio features and project it to two dimensions, while retaining most of the information that describes the sample. That means that audio pieces that sound similar will be packed closely together, while those that sound quite different should be far apart. User can select cluster of similar-sounding samples and mark them, using her / his expertise. 

### What am I looking at?
We have investigated audio recordings from St Helena that contain [storm petrels](https://en.wikipedia.org/wiki/Storm_petrel) calls. That particular set of recordings has labels with information at what time interval we can hear a bird. However, in vast majority of cases, the labels are not present. Moreover, if there are relatively few labelled recordings, it's very difficult for computer systems to learn to recognise given sound.

#### Scatter plot
The scatter plot above is the result of running the dimensionality reduction algorithms on audio recordings, resulting in a 2D visualization of the dataset. Each data point is a short (~0.8s) sample retrieved from audio. Red dots denote storm petrels, while blue is anything else. Click on a data point to play audio and produce spectrogram.

It should be noted that **at any point we are not using the labels (colours) to create clusters**. The colour is there for the demo purpose and to see how different dimensionality reduction algorithms perform. 

With **Lasso Select** tool (present in right-upper corner of the plot) user can select data points of interest. These will be displayed then in Table and available for download.

#### Dimensionality reduction
Dimensionality reduction techniques reduce number of variables by projecting them to a lower-dimensional space. The aim in our case is to retain as much as possible of original information, while enjoying exploration of the data in much in familiar 2D space. We're looking at following methods:
* [t-Distributed Stochastic Neighbor embedding](https://en.wikipedia.org/wiki/T-distributed_stochastic_neighbor_embedding)
* [kernel Principal Component Analysis](https://en.wikipedia.org/wiki/Kernel_principal_component_analysis)
* [linear Principal Component Analysis](https://en.wikipedia.org/wiki/Principal_component_analysis)
* [Independent Component Analysis](https://en.wikipedia.org/wiki/Independent_component_analysis)
* [Uniform Manifold Approximation and Projection](https://arxiv.org/pdf/1802.03426)

As can be easily seen, vast majority of storm petrels are grouped together, especially with algorithms that do better job at capturing non-linear characteristic of the data: Uniform Manifold Approximation and Projection (UMAP) and t-Distributed Stochastic Neighbor embedding (t-SNE).

#### Table
Displays basic properties of the audio features. The content is to be defined. For the demo purpose we have elected "mean frequency". "Download Data" allows to download the selected data points as CSV.

#### Spectrogram
A spectrogram is a visual representation of the spectrum of frequencies of a signal as it varies with time. For each selected sample in the graph we plot spectogram of the respective audio. It allows further verification of similarity between samples as well as provide insights into frequency structure of the signal.
 

### How to use the app
1. Upload your audio (not implemented yet). For the demo purpose we use St Helena recordings.
2. Inspect the clusters. Play audio for various samples to see how they are grouped together.
3. Use "Lasso Selection" to mark recordings of interest.
4. Download the selection.

### TODO
* Add upload button to upload and process (extract features) of user recordings.
* Remove ineffective dimensionality reduction algorithms. It's fun to have these for demo purpose, but for the tool itself we need only one - but a good one. Best candidates seem to be t-SNE and UMAP.


### Further development
Here are some ideas how we can take the development further:
1. Select samples with noise or other sound that is of no interest. Use this selection to clean the original recording of these sounds (frequencies) by spectral subtraction.
2. Consider putting a box for user to label a file to download. Now it comes with predefined name.



 

