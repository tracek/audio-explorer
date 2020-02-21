# About

Hi, I'm Lukasz! I am a software engineer and scientist, founder of Datana Solutions.

![myimg](https://i.imgur.com/p1mCb7p.jpg)

## Why Audio Explorer?

Manual labelling of audio is time consuming and error prone. With this tool we aim to augment user by allowing to easily navigate recordings and label selected audio pieces. Instead of looking at raw audio, we extract number of audio features from each sample. The latter typically consists of dozens of calculated values (features), which would be impossible to visualise (e.g. 20 features per sample effectively means 20-dimensional space). Audio Explorer allows to compute over 100 features per audio fragment.


## How do we achieve that?

The program computes audio features per short fragments of submitted audio piece and then finds projection to 2-dimensional space by using linear or [non-linear dimensionality reduction](https://en.wikipedia.org/wiki/Nonlinear_dimensionality_reduction). Audio fragments are then represented as points; similar sample will be close together, while those which are different further apart. 

Cheers!