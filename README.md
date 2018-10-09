## Distributed Load Testing Using Fargate

Running performance load testing is extremely important to understand how your services will scale and behave once 
deployed to production. However, organizations tend to skip this type of testing because it can be challenging and 
time consuming to setup. One of the main challenges is how to simulate a scenario that mimics the load expected in 
a production environment; In a real world scenario, requests from users typically come from different geographic 
locations and are likely to come in parrallel. This repository is an example of how to setup a distributed load testing
infrastructure using AWS Fargate and the tesing tool Taurus. 

![Architecture](docs/arch.png)

### License Summary

This sample code is made available under a modified MIT license. See the LICENSE file.

### Requirements

- Python 2.7
- Docker CLI
- Access to an AWS account

### Instructions

- Build the docker image

```bash
docker build -t whatever/imageName .
```

- Push the image to a docker registry. For simplicity, the public DockerHub. 

```bash
docker login
docker push whatever/imageName
```

- Configure your test scenario by editing the `tests/my-test.yml` file. 
You can check more about the syntax of this file in the Taurus docs: https://gettaurus.org/kb/Index . 

```yaml
execution:
- concurrency: 5
  ramp-up: 1m
  hold-for: 5m
  scenario: aws-website-test

scenarios:
  aws-website-test:
    requests:
    - http://aws.amazon.com
```

- Create the Fargate clusters by running the Cloud Formation template in `cloudformation/main.yml` on
every region where you want to run tests from. This example works for `us-east-1`, `us-east-2` and `us-west-2`
but is fairly easy to extend for other regions. 

- Once you have created the CloudFormation stacks on every region. You need to edit the `bin/runner.py` python file
to add the list of regions with its cloud formation stack names that you launched on each region. 

### Run the tests

Finally, to start running your tests. You need to run the `runner.py` python script.
It's recommended to create a virtualenv to install the script dependencies. 
 
```bash
pip install virtualenv
cd bin/
virtualenv env
source env/bin/activate
```

Then you can install the dependencies

```bash
pip install -r requirements.txt
```

And run the script

```bash
python runner.py
```
