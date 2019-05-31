# Developer notes

The web app is hosted on AWS and uses following components:

* Elastic Beanstalk with Application Load Balancer: orchestration
* S3: storage
* Route 53: DNS service
* Relational Database Service (RDS) with postgresql
* Secrets Manager: protect secrets (plotly, ipinfo)
* Gunicorn: WSGI


Elastic Beanstalk automatically handles the details of capacity provisioning, load balancing, scaling, and application health monitoring.

## Set up development environment

To set up your development environment, run the following commands:

1. Fork and clone the Audio Explorer [repo](https://github.com/tracek/audio-explorer).
2. Move into the clone: `cd audio-explorer`.
3. Create Anaconda environment: `conda env create -f environment.yml`.

## Documentation

Build docs: `mkdocs build`

Deploy docs to GitHub: `mkdocs gh-deploy`

## Deployment

### Elastic Beanstalk

Install AWS CLI for EB: `pip install awsebcli`

Prcedure:

1. Initialise the environment: `eb init`
2. Create and deploy new instance of type: `eb create -i [type]`
3. Deploy `eb deploy`. Hit it to deliver every new chunk.

SSH to the machine on Elastic Beanstalk: `eb ssh`


### Docker

Build docker image: `docker image build [path] user/name:latest`

Example:

    docker build -t tracek/audio-explorer:latest -t tracek/audio-explorer:0.1 .
    
SSH to the container: `sudo docker exec -it [container id] /bin/bash`


## **Troubleshooting**

Problem: Elastic Beanstalk deployment via Docker fails due thin pool getting full.

Solution:

- Use EC2 that has a drive with sufficient space (mind most of EC2 uses EBS volumes)
- Follow instructions from [Server Fault](https://serverfault.com/questions/840937/aws-elasticbeanstalk-docker-thin-pool-getting-full-and-causing-re-mount-of-files)

The latter comes recommended, as default thin pool is ~12 GB, which is not enough for Audio Explorer. Bumping it to 40 GB is a good choice - that's why we have `.ebextensions/04_docker.config`.

## Pull Request Guidelines

Use the [GitHub flow](https://guides.github.com/introduction/flow/) when proposing contributions to this repository (i.e. create a feature branch and submit a PR against the master branch). How to create pull request is discussed [here](https://help.github.com/en/articles/creating-a-pull-request). 