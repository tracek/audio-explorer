# Contributing to Audio Explorer

Audio Explorer is and will remain open source - that's a promise. I might want to relicence it in future to e.g. MIT if it turns out it fits better open source or conservation science community.

> The GNU GPL does not give users permission to attach other licenses to the program. But the copyright holder for a program can release it under several different licenses in parallel... If you are the copyright holder for the code, you can release it under various different non-exclusive licenses at various times.

Once you contribute to the code, I'd need to get your written permission to relicence the code. If for any reason you'd be unreachable or unhappy with, say, MIT licence, I'd have to try to disentangle your contribution from the code base, causing severe overhead. For this reason, I will kindly ask to assign the copyright to the project. For further explanation, see [this answer on Stack Exchange](https://opensource.stackexchange.com/questions/5796/projects-which-require-copyright-assignment-from-contributors).

## Getting Started

To set up your development environment, run the following commands:
1. Fork and clone the Audio Explorer [repo](https://github.com/tracek/audio-explorer).
2. Move into the clone: `cd audio-explorer`.
3. Create Anaconda environment: `conda env create -f environment.yml`.

#### TODO

Currently Audio Explorer uploads every upload to my S3. We need a local mode that will allow anyone to easily experiment and develop the code.

## Coding Style

Please lint your code with `pylint` and `flake8`.

## Pull Request Guidelines

Use the [GitHub flow](https://guides.github.com/introduction/flow/) when proposing contributions to this repository (i.e. create a feature branch and submit a PR against the master branch). How to create pull request is discussed [here](https://help.github.com/en/articles/creating-a-pull-request). 
