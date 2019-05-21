# Frequently Asked Questions


##### Why bandpass filter only goes to 8000 Hz?

The audio you upload is converted to mono-channel 16 kHz which translates to 8 kHz (half of the sampling frequency). Read on [Nyquist rate](https://en.wikipedia.org/wiki/Nyquist_rate) for explanation.

##### My files take long to upload

Consider reducing the sampling frequency to 16kHz, number of channels to 1 and compressing the file to e.g. mp3. There is an excellent cross-platform tool called [SoX](http://sox.sourceforge.net/)  that can help you. If you have a lot of files that you want to process, here's how you can process them in parallel on Linux / Mac:

```bash
find . -name '*.wav' -type f -print0 | parallel -0 sox --norm {} -r 16000 --channels 1 your-path/{.}.mp3
``` 

The command:
* Finds all wav
* Pipes then to `parallel` tool that will execute subsequent call in parallel 
* `SoX` normalises the audio, resamples to `16 kHz` and one channel and then converts to `mp3`

Read [parallel cheat sheet](https://www.gnu.org/software/parallel/parallel_cheat.pdf) and [full manual](https://www.gnu.org/software/parallel/man.html) for details. 

##### How to install the software?

There are a few approaches:
* Start from scratch from the repo
* Use [Docker image](https://hub.docker.com/r/tracek/audio-explorer)
* Check with me about producing a Virtual Machine image with the software. We could use e.g. [VirtualBox](https://www.virtualbox.org/). 