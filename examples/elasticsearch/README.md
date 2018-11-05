## Load Testing an Amazon Elasticsearch Cluster

This example assumes that your Elasticsearch cluster is behind a VPC and not exposed publicly to the internet. However, 
either way is possible to test. Having it publicly accessible makes it even easier. 

![Arch](../../docs/elasticsearch.png)

To start, follow all the instructions 
in the main [README](https://github.com/aws-samples/distributed-load-testing-using-aws-fargate/blob/master/README.md), 
except for **Step 2 and 4** in which you need to do the following changes instead.

### Instead of Step 2
Open the [Dockerfile](https://github.com/aws-samples/distributed-load-testing-using-aws-fargate/blob/master/Dockerfile) 
in the root directory of the project and uncomment the elasticsearch instruction and comment out the http one. It should
look like this: 

```Dockerfile
# ADD examples/http /bzt-configs/
ADD examples/elasticsearch /bzt-configs/
```

Then, edit the [runner.py](https://github.com/aws-samples/distributed-load-testing-using-aws-fargate/blob/master/bin/runner.py) 
script and specify your Elasticsearch cluster URL in the environment variable.

```python
ENDPOINT_UNDER_TEST = 'https://vpc-123456789.aws.us-west-2.amazon.com'
```

Finally, write your test scenarios. I have written a `consumer.test.js` and a `producer.test.js` scenarios for 
demonstration purposes, but you can edit them to fit your needs. In this example, the producer will create random JSON
documents to be indexed in the cluster, while the consumer will issue *search* requests of randomly generated words. 
If you look at the `taurus.yml` file, you can see both scenarios specified, which means that Taurus will execute both 
scripts in parallel.

### Instead of Step 4

In the case of your Elasticsearch cluster running behind a VPC, the easiest option would be run the Fargate Docker tasks 
in the same VPC. So, follow **Step 4** just as described in the main [README](https://github.com/aws-samples/distributed-load-testing-using-aws-fargate/blob/master/README.md) 
but use the CloudFormation template located in `cloudformation/main-with-existing-vpc.yml`. This template will let you
choose the VPC and Subnets to place the Fargate cluster. 

For this same reason, run the CloudFormation template in 1 region only and make sure to edit the `bin/runner.py` script
to reflect the one region where you created it. Which should be the same region where Elasticsearch is running. 

```python
regions = [
    {
      'name': 'us-east-1',
      'stackName': 'dlt-fargate',
      'taskCount': 3
    },
#    {
#      'name': 'us-east-2',
#      'stackName': 'dlt-fargate',
#      'taskCount': 3
#    },
#    {
#      'name': 'us-west-2',
#      'stackName': 'dlt-fargate',
#      'taskCount': 3
#    }
]
```

Remember, if your Elasticsearch cluster is publicly accessible, meaning that it's HTTP endpoint is reachable from anywhere 
in the world, you can ignore the previous step and deploy the Fargate cluster in multiple regions and in it's own VPCs. 