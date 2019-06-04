# Case study: Storm Petrels

## Introduction

Case of Storm Petrels from St Helena was the main drive behind creating the Audio Explorer. RSPB has lots of audio recordings from the island and was interested in estimating population change and their activity. Typically, supervised machine learning systems need reliable labels to inform the algorithm about what is that we are looking for. Labelling of audio recordings is labourious, error prone and subjective activity. It depends on our perception and judgement. One person might bird call that other would consider too faint - or not hear at all. 

#### Garbage In - Garbage Out

The trouble with that approach is that when incorrect labels are fed to supervised machine learning algorithms, we risk that the system won't learn what we intend - and only a narrow band that is presented. Worse, if we skip over some calls and denote them as noise, the system might get quite confused on what's the species of interest. That's what was happening in case of storm petrels and labels we have had initially. We needed better labels, not only to tell the system how the storm petrel sounds - but also how it does not sound.

## Data

The recordings from St Helena consist of over 500h of data recorded in stereo with 44khz sampling rate. We downsampled and compressed the data such that upload to Audio Explorer would take much less time - check the [FAQ](faq.md) for details. For the analysis we used 16khz sampling rate.

## Method

Our goal was to count all storm petrel calls. To achieve it

Having quality labels is crucial to enable successfuly supervised machine learning, 