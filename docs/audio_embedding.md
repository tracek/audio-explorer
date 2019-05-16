# Audio embedding

## Audio features

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

## Dimensionality reduction
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
