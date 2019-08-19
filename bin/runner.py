# Copyright 2018 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this
# software and associated documentation files (the "Software"), to deal in the Software
# without restriction, including without limitation the rights to use, copy, modify,
# merge, publish, distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
# INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
# PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
import boto3
import uuid
import os


# Will be passed as environment variable to the Fargate docker containers.
# Useful with the Elasticsearch example as the test suite will read the cluster URL from this variable.
ENDPOINT_UNDER_TEST = os.getenv('ENDPOINT_UNDER_TEST', 'http://strawberry.banana.com')
TASK_COUNT = int(os.getenv('TASK_COUNT', 3))

def get_regions_from_environment_variables():
    regions = []
    region_count = 1
    next_region = os.environ.get('REGION_' + str(region_count))
    while next_region:
        regions.append({
            'name': next_region,
            'stackName': os.environ.get('REGION_' + str(region_count) + '_STACK_NAME')
        })
        region_count += 1
        next_region = os.environ.get('REGION_' + str(region_count))

    return regions


def start_distributed_load_test():
    run_id = str(uuid.uuid4())
    print('Started new load test with runId = {}'.format(run_id))

    print('Getting list of regions from environment variables')
    regions = get_regions_from_environment_variables()
    totalTasks = int(TASK_COUNT)
    if int(totalTasks * len(regions)) > 50:
        print('Too many tasks - lower number of task per region')
        exit(0)


    for region in regions:

        if not region['stackName']:
            continue
       
        lastPass = int(totalTasks % 10)
        totalPasses = int(totalTasks / 10) 
        
        if  lastPass > 0:
            totalPasses = int(totalPasses + 1)
       
        if  totalPasses > 1:
            print('Batching Task Requests in Groups of 10. Total passes = {}'.format(str(totalPasses)))
        
        if  lastPass > 0:
            print('Last batch will contain {} task requests'.format(str(lastPass)))
        
        while totalPasses > 0:
            cloud_formation = boto3.client('cloudformation', region_name=region['name'])
            ecs = boto3.client('ecs', region_name=region['name'])

            print('Describing CloudFormation stack {} in region {}'.format(region['stackName'], region['name']))
            stacks = cloud_formation.describe_stacks(
                StackName=region['stackName']
            )

            if not stacks['Stacks']:
                print("CloudFormation stack {} not found in region {}".format(region['stackName'], region['name']))
                exit(0)

            stack = stacks['Stacks'][0]
            outputs = stack['Outputs']
            stack_outputs = {}

            print('Extracting cluster values from CloudFormation stack')
            for output in outputs:
                stack_outputs[output['OutputKey']] = output['OutputValue']       
           
            currentPass = totalPasses
            
            tasksInThisPass = 0           
            
            if  currentPass == 1:
                tasksInThisPass = lastPass
            
            if  currentPass > 1:
                tasksInThisPass = 10
        
            response = ecs.run_task(
                cluster=stack_outputs['FargateClusterName'],
                taskDefinition=stack_outputs['TaskDefinitionArn'],
                count=tasksInThisPass,
                startedBy=run_id,
                launchType='FARGATE',
                overrides={
                    'containerOverrides': [
                        {
                            'name': 'dlt-fargate-task',
                            'environment': [
                                {
                                    'name': 'ENDPOINT_UNDER_TEST',
                                    'value': ENDPOINT_UNDER_TEST
                                },
                            ],
                        },
                    ]
                },
                networkConfiguration={
                    'awsvpcConfiguration': {
                        'assignPublicIp': 'ENABLED',
                        'securityGroups': [stack_outputs['TaskSecurityGroup']],
                        'subnets': [
                            stack_outputs['SubnetA'],
                            stack_outputs['SubnetB'],
                            stack_outputs['SubnetC']
                        ]
                    }
                }
            )

            if not response or response['failures']:
                print('Failed to schedule tasks')
                exit(0)

            for task in response['tasks']:
                print('Task scheduled {}', task['taskArn'])    
            totalPasses = currentPass - 1   


if __name__ == '__main__':
    start_distributed_load_test()
