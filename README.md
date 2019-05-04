# Audio Explorer

Audio Explorer helps is audio data discovery and labelling by utilising unsupervised and supervised machine learning - and good deal of statistics with digital signal processing.

The program computes audio features per short fragments of submitted audio piece and then finds projection to 2-dimensional space by using linear or [non-linear dimensionality reduction](https://en.wikipedia.org/wiki/Nonlinear_dimensionality_reduction). Audio fragments are then represented as points; similar sample will be close together, while those which are different further apart. User can click on a point to play the audio fragment and inspect resulting [spectrogram](https://en.wikipedia.org/wiki/Spectrogram). 

#### Why build it?

Manual labelling of audio is time consuming and error prone. With this tool we aim to augment user by allowing to easily navigate recordings and label selected audio pieces. Instead of looking at raw audio, we extract number of audio features from each sample. The latter typically consists of dozens of calculated values (features), which would be impossible to visualise (e.g. 20 features per sample effectively means 20-dimensional space). Audio Explorer allows to compute over 100 features per audio fragment.

The main driver behind creation of this software were problems I faced when developing an algorithm to classify bird calls for the [Royal Society for the Protection of Birds](https://www.rspb.org.uk/). 

#### How do we solve the problem?
We take the multidimensional space of computed audio features and project it to two dimensions, while retaining most of the information that describes the sample. That means that audio pieces that sound similar will be packed closely together, while those that sound quite different should be far apart. User can select cluster of similar-sounding samples and mark them.

## Development

See [CONTRIBUTING](CONTRIBUTING.md).


## Acknowledgement

My thanks to:
* AWS Cloud Credits for Research for supporting the project! Elastic Beanstalk, EC2, S3, RDS, Secrets Manager and CloudWatch work excellent and enable both rapid model prototyping and development of the software.
* My colleagues from RSPB who have supplied the audio recordings and supported along the way.


## Licence

Audio Explorer is released under the version 3 of the GNU General Public License. Read COPYING for more details. The project is and will remain open source - that's a promise. 

## Contact information

```bash
python -c 'import base64; print(base64.b64decode("bHVrYXN6LnRyYWNld3NraUBvdXRsb29rLmNvbQ=="))'
```