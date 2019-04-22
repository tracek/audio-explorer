### Why Audio Explorer
Manual labelling of audio is time consuming and error prone. With this tool we aim to augment user by allowing to easily navigate recordings and label selected audio pieces. Instead of looking at raw audio, we extract number of audio features from each sample. The latter typically consists of dozens of calculated values (features), which would be impossible to visualise (e.g. 20 features per sample effectively means 20-dimensional space). 

### How do we solve the problem
We take the multidimensional space of computed audio features and project it to two dimensions, while retaining most of the information that describes the sample. That means that audio pieces that sound similar will be packed closely together, while those that sound quite different should be far apart. User can select cluster of similar-sounding samples and mark them, using her / his expertise. 

### What am I looking at?
The scatter plot is the result of running the dimensionality reduction algorithms on audio recordings, resulting in a 2D visualization of the dataset. Each data point is a short sample retrieved from audio. 


#### Dimensionality reduction
Dimensionality reduction techniques reduce number of variables by projecting them to a lower-dimensional space. The aim in our case is to retain as much as possible of original information, while enjoying exploration of the data in much in familiar 2D space. We're looking at following methods:
* [t-Distributed Stochastic Neighbor embedding](https://en.wikipedia.org/wiki/T-distributed_stochastic_neighbor_embedding)
* [Uniform Manifold Approximation and Projection](https://arxiv.org/pdf/1802.03426)
* and more ... (TODO)


#### Spectrogram
A spectrogram is a visual representation of the spectrum of frequencies of a signal as it varies with time. For each selected sample in the graph we plot spectogram of the respective audio. It allows further verification of similarity between samples as well as provide insights into frequency structure of the signal.
 

### How to use the app
1. Upload your audio.
2. Inspect the clusters. Play audio for various samples to see how they are grouped together.
3. ... TODO

