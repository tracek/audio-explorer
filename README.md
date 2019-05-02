# Audio Explorer

Work in progress. Much of the notes below are just download from my head without much structure. The latter will come in time.

#### Useful commands

Build docker image: `docker image build [path] user/name:latest`

Pull and run miniconda:
```
docker pull continuumio/miniconda3
docker run -i -t continuumio/miniconda3 /bin/bash
```

#### Working with Elastic Beanstalk

Install AWS CLI for EB: `pip install awsebcli`

Prcedure:
 
 * Initialise the environment: `eb init`
 * Create and deploy new instance of type: `eb create -i [type]`
 * Deploy `eb deploy`


#### Troubleshooting

Problem: Elastic Beanstalk deployment via Docker fails due thin pool getting full.

Solution: 
* Use EC2 that has a drive with sufficient space (mind most of EC2 uses EBS volumes)
* Follow instructions from [Server Fault](https://serverfault.com/questions/840937/aws-elasticbeanstalk-docker-thin-pool-getting-full-and-causing-re-mount-of-files)

#### Contact information

My email address:
```bash
python -c 'import base64; print(base64.b64decode("bHVrYXN6LnRyYWNld3NraUBvdXRsb29rLmNvbQ=="))'
```

#### Licence

Audio Explorer is released under the version 3 of the GNU General Public License. Read COPYING for more details. 