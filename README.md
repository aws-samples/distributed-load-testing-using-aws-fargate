## Distributed Load Testing Using Fargate

This project launches a solution that runs Distributed Load Tests using 
[AWS Fargate](https://aws.amazon.com/fargate) and [Taurus](https://gettaurus.org). You can use it to test your 
services under high stress scenarios and understand it's behavior and scalability. 

![Architecture](docs/arch.png)

Taurus acts as a wrapper around JMeter and allows you to generate HTTP requests in parallel simulating a 
real-world scenario. This solution shows how to run Taurus on Docker containers and deploy them to Fargate clusters
running in different AWS regions, so that you can simulate requests coming from different geographic locations into 
your service. 

**Note**: Your service (system under test) does not have to be running on AWS. You can configure this solution to hit
any HTTP endpoint as long as it's accessible through the internet. However, this solution is meant to be deployed
on an AWS account. 

## License Summary

This sample code is made available under a modified MIT license. See the LICENSE file.

## Requirements

- An AWS Account
- [Git Credentials for AWS CodeCommit](https://docs.aws.amazon.com/codecommit/latest/userguide/setting-up-gc.html)  

## Getting Started

### 1. Launch Solution

In this step you will launch the `master` CloudFormation stack that will create a Fargate Cluster, an ECR Docker registry, an IAM
Execution Role, a Task Definition, a CloudWatch Log Group, a Security Group, a new VPC, a CodeCommit repository, a CodePipeline 
and 2 CodeBuild projects with their associated IAM Roles. 

Region Name | Region Code | Launch
------|-----|-----
US East (N. Virginia) | us-east-1 | [![Launch in us-east-1](https://camo.githubusercontent.com/210bb3bfeebe0dd2b4db57ef83837273e1a51891/68747470733a2f2f73332e616d617a6f6e6177732e636f6d2f636c6f7564666f726d6174696f6e2d6578616d706c65732f636c6f7564666f726d6174696f6e2d6c61756e63682d737461636b2e706e67)](https://console.aws.amazon.com/cloudformation/home?region=us-east-1#/stacks/new?stackName=DistributedLoadTesting&templateURL=https://s3.amazonaws.com/distributed-load-testing-using-aws-fargate/templates/master.yaml)
US East (Ohio) | us-east-2 | [![Launch in us-east-2](https://camo.githubusercontent.com/210bb3bfeebe0dd2b4db57ef83837273e1a51891/68747470733a2f2f73332e616d617a6f6e6177732e636f6d2f636c6f7564666f726d6174696f6e2d6578616d706c65732f636c6f7564666f726d6174696f6e2d6c61756e63682d737461636b2e706e67)](https://console.aws.amazon.com/cloudformation/home?region=us-east-2#/stacks/new?stackName=DistributedLoadTesting&templateURL=https://s3.amazonaws.com/distributed-load-testing-using-aws-fargate/templates/master.yaml)
US West (Oregon) | us-west-2 | [![Launch in us-west-2](https://camo.githubusercontent.com/210bb3bfeebe0dd2b4db57ef83837273e1a51891/68747470733a2f2f73332e616d617a6f6e6177732e636f6d2f636c6f7564666f726d6174696f6e2d6578616d706c65732f636c6f7564666f726d6174696f6e2d6c61756e63682d737461636b2e706e67)](https://console.aws.amazon.com/cloudformation/home?region=us-west-2#/stacks/new?stackName=DistributedLoadTesting&templateURL=https://s3.amazonaws.com/distributed-load-testing-using-aws-fargate/templates/master.yaml)

You will notice that the CloudFormation `master` stack expands itself into 4 stacks: The master one, which takes care of 
creating resources that will be shared across regions like the ECR Registry and the CodePipeline; The VPC nested stack, 
which creates the network configuration and subnets; The Fargate nested stack which creates the cluster and task definition 
and the Pipeline nested stack that creates the CodeCommit repository and the CodeBuild projects to build and run the 
load tests in Fargate.

### 2. Clone this repository

```bash
git clone https://github.com/aws-samples/distributed-load-testing-using-aws-fargate.git
```

### 3. Modify the load test scenario

Configure your test scenario by editing the `examples/http/taurus.yml` file. The default example shown below runs a load test 
for 5 minutes with 5 concurrent requests per second against https://aws.amazon.com with a ramp-up time of 1 minute. 

```yaml
execution:
- concurrency: 5
  ramp-up: 1m
  hold-for: 5m
  scenario: aws-website-test

scenarios:
  aws-website-test:
    requests:
    - https://aws.amazon.com
```

To learn more about the syntax of this file, check the Taurus docs: https://gettaurus.org/kb/Index.

### 4. Push to CodeCommit

One of the resources that gets created when deploying this solution is a CodeCommit repository that stores your
your load test scenarios. A CodePipeline was also created and connected to the CodeCommit repository, such that when you 
push a new commit the pipeline will be triggered automatically, build your load test scenarios into a Docker image, push 
the image to the ECR registry and then run the tests into the Fargate cluster; all of this automatically!

First, remove the current Git origin of the project because you just cloned it from Github.     

```bash
git remote rm origin
```

Now, set the origin to be your new CodeCommit repository.

```bash
git remote add origin {code_commit_repository_url}
```

Finally, push the code. Note that after you push this, the deployment pipeline will be triggered automatically 
and therefore running the load tests scenarios in the Fargate cluster(s).

```bash
git push -u origin master
```

### 5. Monitor the test execution in CloudWatch

The CloudFormation template should have created a [CloudWatch Metric Filter](https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/FilterAndPatternSyntax.html)
that will capture the average response time for each HTTP request that was issued to your system under test. You should
see something like this in the template:

```yaml
TaurusLogFilterAvgResponseTime:
  Type: AWS::Logs::MetricFilter
  Properties:
    FilterPattern: "[time, logType=INFO*, logTitle=Current*, numVu, vu, numSucc, succ, numFail, fail, avgRt, x]"
    LogGroupName: !Ref FargateTaskCloudWatchLogGroup
    MetricTransformations:
      -
        MetricValue: "$avgRt"
        MetricNamespace: "dlt-fargate/taurus"
        MetricName: "avgResponseTime"
```

What this filter is doing, is parsing the Taurus logs that match that given format and assigning a variable name to each
value in the log. We are going to ignore all values in the log except for `avgRt` which is captured as a new metric and 
stored in your CloudWatch Metrics. 

Once the filter is in place, I recommend to centralize the metrics from the different regions into a single CloudWatch
Dashboard. To pull metrics from different regions into one Dashboard [follow this steps](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/cross_region_dashboard.html).
The Dashboard will look something like this:   

![CloudWatch](docs/cloudwatch.jpg)

## Launch in Additional Regions (Optional)

It may be likely that running this solution from a single AWS region is enough to load test your application. However, 
if you want to take it a step further, you can do so by deploying Fargate clusters in multiple regions and make this a 
real distributed load test simulation. For this, I have created a separate CloudFormation template for you to launch the 
solution in additional regions. The difference between this template and the Master one, is that this one doesn't
create the ECR Docker Registry and the IAM Execution Role, as you can share these resources across all Fargate deployments. 

Use the following buttons to launch the solution in the desired additional regions:  

Additional Region | Region Code | Launch
------|-----|-----
US East (N. Virginia) | us-east-1 | [![Launch in us-east-1](https://camo.githubusercontent.com/210bb3bfeebe0dd2b4db57ef83837273e1a51891/68747470733a2f2f73332e616d617a6f6e6177732e636f6d2f636c6f7564666f726d6174696f6e2d6578616d706c65732f636c6f7564666f726d6174696f6e2d6c61756e63682d737461636b2e706e67)](https://console.aws.amazon.com/cloudformation/home?region=us-east-1#/stacks/new?stackName=DistributedLoadTesting&templateURL=https://s3.amazonaws.com/distributed-load-testing-using-aws-fargate/templates/additional-region.yaml)
US East (Ohio) | us-east-2 | [![Launch in us-east-2](https://camo.githubusercontent.com/210bb3bfeebe0dd2b4db57ef83837273e1a51891/68747470733a2f2f73332e616d617a6f6e6177732e636f6d2f636c6f7564666f726d6174696f6e2d6578616d706c65732f636c6f7564666f726d6174696f6e2d6c61756e63682d737461636b2e706e67)](https://console.aws.amazon.com/cloudformation/home?region=us-east-2#/stacks/new?stackName=DistributedLoadTesting&templateURL=https://s3.amazonaws.com/distributed-load-testing-using-aws-fargate/templates/additional-region.yaml)
US West (Oregon) | us-west-2 | [![Launch in us-west-2](https://camo.githubusercontent.com/210bb3bfeebe0dd2b4db57ef83837273e1a51891/68747470733a2f2f73332e616d617a6f6e6177732e636f6d2f636c6f7564666f726d6174696f6e2d6578616d706c65732f636c6f7564666f726d6174696f6e2d6c61756e63682d737461636b2e706e67)](https://console.aws.amazon.com/cloudformation/home?region=us-west-2#/stacks/new?stackName=DistributedLoadTesting&templateURL=https://s3.amazonaws.com/distributed-load-testing-using-aws-fargate/templates/additional-region.yaml)
   

## Run Locally

Build the image by issuing the following command in the root directory of this project.

```bash
docker build -t load-tests-using-fargate .
```

Then run the docker container locally.

```bash
docker run -it load-tests-using-fargate taurus.yml
```

If the docker ran as expected, you can push the changes to your AWS CodeCommit repository and let the pipeline 
do the rest.