# Getting started

TODO - detailed walkthrough

## Explore

Explanation of app sections.

### What am I looking at?
The scatter plot is the result of running the dimensionality reduction algorithms on audio recordings resulting in a 2D visualization of the dataset. Each data point is a short sample retrieved from audio. 

### Spectrogram
A spectrogram is a visual representation of the spectrum of frequencies of a signal as it varies with time. For each selected sample in the graph we plot spectogram of the respective audio. It allows further verification of similarity between samples as well as provide insights into frequency structure of the signal.

## Worflow example

1. Tune the algorithm parameters or accept the defaults. 
2. Upload an audio file you want to analyse. If you don't have anything at hand, [here](https://s3.eu-central-1.amazonaws.com/audioexplorer-public/sthelena_example.mp3) is an audio that contains some bird calls, primarily storm petrels, recorded on St. Helena. Can you spot bird calls on the scatter plot? To download the recording, right-click on the link and select "save link as..." and then *Upload* it. Audio Explorer works with majority of popular audio formats, all thanks to [sox](http://sox.sourceforge.net).
3. Play with the parameters, add / remove features and see how it influences the plot by clicking *Apply*.
4. Click a point on the graph to hear the audio and see the spectrogram. Mind that what you hear and see is longer than selected `Sample length` by `0.4s`. `0.2s` margin is added to the beginning and end to get better impression of the sound surrounding.  
5. Calculated audio features can be inspected, sorted and filtered through custom-made query language by selecting _Table_ tab. You can use the following expressions: `<=`, `<`, `>=` and `>`, e.g. `> 2000`.
6. Use *Lasso select* (top right menu that appears after hovering over the graph) to select interesting cluster. The selection will be reflected in *Table*.
7. For the selected audio fragments a power spectrum will be plotted (units: Voltage<sup>2</sup>), scaled to dB.
8. Now that we have frequencies present in the selected fragments, user can decide to reduce presence of these frequencies in rest of the audio.  
9. Once you're happy with the selection, you can download the data from *Table*.
