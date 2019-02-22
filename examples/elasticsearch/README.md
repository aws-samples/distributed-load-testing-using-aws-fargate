## Load Testing an Amazon Elasticsearch Cluster

To start, follow the instructions in the main [README](https://github.com/aws-samples/distributed-load-testing-using-aws-fargate/blob/master/README.md) 
and do the following changes: 

### Modify the Dockerfile
Open the [Dockerfile](https://github.com/aws-samples/distributed-load-testing-using-aws-fargate/blob/master/Dockerfile) 
in the root directory of the project and uncomment the elasticsearch instruction and comment out the http one. It should
look like this: 

```Dockerfile
# ADD examples/http /bzt-configs/
ADD examples/elasticsearch /bzt-configs/
```

Then add an environment variable to the TestRunner step in the CodePipeline to specify your Elasticsearch cluster URL. 
The environment variable name should be `ENDPOINT_UNDER_TEST` and it's value should be the http endpoint of the cluster.
If you open the runner.py script under the `bin` folder. You will see how the script is using the environment variable. 

### Modify Test Scenarios

I have written a `consumer.test.js` and a `producer.test.js` scenarios for demonstration 
purposes under the `examples/elasticsearch` folder, but you can edit them to fit your needs. In this example, 
the producer will create random JSON documents to be indexed in the cluster, while the consumer will issue *search* 
requests of randomly generated words. If you look at the `taurus.yml` file, you can see both scenarios specified, 
which means that Taurus will execute both scripts in parallel.

### Testing a Private Elasticsearch Cluster

If the Elasticsearch is private, meaning that it's endpoint is not accessible from the internet. Then head to the 
`v2.0-beta` version of this project: https://github.com/aws-samples/distributed-load-testing-using-aws-fargate/releases/tag/v0.2-beta 
and use that code base. The current one is no longer compatible for private connectivity as the Fargate clusters 
get created in it's own VPC. 
 