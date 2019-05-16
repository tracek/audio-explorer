## Audio Explorer

[Audio Explorer](http://audioexplorer.online) helps in audio data discovery and labelling by utilising unsupervised machine learning, statistics and digital signal processing.

The program computes audio features per short fragments of submitted audio piece and then finds projection to 2-dimensional space by using linear or [non-linear dimensionality reduction](https://en.wikipedia.org/wiki/Nonlinear_dimensionality_reduction). Audio fragments are then represented as points; similar sample will be close together, while those which are different further apart. User can click on a point to play the audio fragment and inspect resulting [spectrogram](https://en.wikipedia.org/wiki/Spectrogram). 

## Documentation

Check the [docs](https://tracek.github.io/audio-explorer) to learn about the program and the gory details of how it works.

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

or post an issue on GitHub.

Cheers!