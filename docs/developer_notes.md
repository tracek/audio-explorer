# Developer notes

The web app is hosted on AWS. It scales to up to 3 instances and uses `nginx` load balancer. The traffic is secured and managed though Route 53. AWS provides a certificate too. The code repository contains complete load balancer configuration required to run the app in the wild. 

Elastic Beanstalk automatically handles the details of capacity provisioning, load balancing, scaling, and application health monitoring.

## Set up development environment

To set up your development environment, run the following commands:

1. Fork and clone the Audio Explorer [repo](https://github.com/tracek/audio-explorer).
2. Move into the clone: `cd audio-explorer`.
3. Create Anaconda environment: `conda env create -f environment.yml`.

#### TODO

Currently Audio Explorer uploads every upload to my S3. We need a local mode that will allow anyone to easily experiment and develop the code.

## Pull Request Guidelines

Use the [GitHub flow](https://guides.github.com/introduction/flow/) when proposing contributions to this repository (i.e. create a feature branch and submit a PR against the master branch). How to create pull request is discussed [here](https://help.github.com/en/articles/creating-a-pull-request). 