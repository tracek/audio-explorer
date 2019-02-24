# Audio Explorer

Work in progress. Much of the notes below are just download from my head without much structure. The latter will come in time.

### Useful commands

Build docker image: `docker image build [path]`

Pull and run miniconda:
```
docker pull continuumio/miniconda3
docker run -i -t continuumio/miniconda3 /bin/bash
```

#### Working with Elastic Beanstalk

Install AWS CLI for EB: `pip install awsebcli`

Prcedure:
 
 * `eb init`
 * `eb create`
 * `eb deploy`
