# Case study: Storm Petrels

![storm petrel](https://www.rspb.org.uk/globalassets/images/birds-and-wildlife/bird-species-illustrations/storm-petrel_1200x675.jpg?preset=landscape_mobile)

Storm petrel is little bigger than a sparrow it appears all black with a white rump. 
Its tail is not forked, unlike Leach's petrel. In flight it flutters over the water, feeding with its wings held up in a 'V' with feet pattering across the waves. At sea it often feeds in flocks and will follow in the wake of ships, especially trawlers. ([_source_](https://www.rspb.org.uk/birds-and-wildlife/wildlife-guides/bird-a-z/storm-petrel/))

We are interested in change of their population on St Helena.

## Remote monitoring

Information on population change can tell us a great deal on how much conservation efforts are working - or not. Is everything fine or we should implement some actions? How's the bird population doing? Remote monitoring is essential in tracking how well we are doing in reaching biodiversity targets, e.g. Aichi Biodiversity Targets 11 and 13.

## Why Audio Explorer?

Case of Storm Petrels from St Helena was the main drive behind creating the Audio Explorer. RSPB has lots of audio recordings from the island and was interested in estimating population change and their activity. Typically, supervised machine learning systems need reliable labels to inform the algorithm about what is that we are looking for. Labelling of audio recordings is labourious, error prone and subjective activity. It depends on our perception and judgement. One person might bird call that other would consider too faint - or not hear at all. 

#### Garbage In - Garbage Out

The trouble with that approach is that when incorrect labels are fed to supervised machine learning algorithms, we risk that the system won't learn what we intend - and only a narrow band that is presented. Worse, if we skip over some calls and denote them as noise, the system might get quite confused on what's the species of interest. That's what was happening in case of storm petrels and labels we have had initially. We needed better labels, not only to tell the system how the storm petrel sounds - but also how it does not sound.

## Data

The recordings from St Helena consist of over 500h of data recorded in stereo with 44khz sampling rate. We downsampled and compressed the data such that upload to Audio Explorer would take much less time - check the [FAQ](faq.md) for details. For the analysis we used 16khz sampling rate.

## Method 

THIS SECTION WILL BE EXPANDED SHORTLY

Having quality labels is crucial to enable successful supervised machine learning. Audio Explorer enabled us to label in 2 hours over 200 hours of recordings. ~50h was then used for training and validation, while rest for testing.

The results are very promising: ~99% accuracy. It should be attributed partially to the fact that the case was not complicated, there are not many sounds that can confuse the algorithm. The only "competition" to storm petrels make brown noddy.

Here's the ROC:

<iframe width="900" height="800" frameborder="0" scrolling="no" src="//plot.ly/~tracewsl/339.embed"></iframe
