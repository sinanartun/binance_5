import json
import string
import time
from random import choice

import boto3

ec2_client = boto3.client('ec2', region_name='eu-north-1')


def subnets_associated_with_VPC():
    # Find subnet associated with VPC
    subnet_a = ""
    subnet_b = ""
    all_subnets = ec2_client.describe_subnets()
    for subnet in all_subnets["Subnets"]:
        if subnet['CidrBlock'] == "10.0.2.0/24":
            subnet_a = subnet['SubnetId']

        if subnet['CidrBlock'] == "10.0.3.0/24":
            subnet_b = subnet['SubnetId']

    return subnet_a, subnet_b


def get_vpc_id():
    all_vpcs = ec2_client.describe_vpcs()
    return all_vpcs["Vpcs"][1]["VpcId"]


def create_new_security_group(vpc_id):
    waiter = ec2_client.get_waiter('security_group_exists')
    response = ec2_client.create_security_group(
        Description='For lambda_vpc example.',
        GroupName=f"lambda_ec2_sg_id_{''.join(choice(string.ascii_lowercase) for _ in range(10))}",
        VpcId=vpc_id,
    )

    waiter.wait(GroupIds=[response['GroupId']])
    time.sleep(3)
    return response


def create_ec2_instance(subnet_id, security_group_id):
    # Create a new Key Pair
    key_pair_name = f"lambda_ec2_instance_key_pair{''.join(choice(string.ascii_lowercase) for _ in range(10))}"
    key_pair = ec2_client.create_key_pair(KeyName=key_pair_name)

    # Block Device Mappings
    block_device_mappings = [
        {
            'DeviceName': '/dev/sda1',  # for t3.micro ınstance type
            'Ebs': {
                'VolumeSize': 10,
                'VolumeType': 'gp3'  # Its free tier option
            }
        }
    ]

    instance_response = ec2_client.run_instances(
        ImageId='ami-02d0b04e8c50472ce',  # Indicates Amazon Linux 2 AMI - Kernel 5.10, SSD Volume Type (Free Tier)
        InstanceType='t3.micro',  # Indicates Family:t3, 2vCPU 1GiB Memory (Free Tier)
        MinCount=1,
        MaxCount=1,
        NetworkInterfaces=[
            {
                'DeviceIndex': 0,
                'SubnetId': subnet_id,
                'Groups': [security_group_id],
                'AssociatePublicIpAddress': True,
                'DeleteOnTermination': True,
            }
        ],
        BlockDeviceMappings=block_device_mappings,
        KeyName=key_pair_name
    )

    waiter = ec2_client.get_waiter('instance_exists').wait(WaiterConfig={'Delay': 5, 'MaxAttempts': 20})

    print("EC2 Instance created successfully.")

    # Instance'a etiket ekleme
    instance_id = instance_response['Instances'][0]['InstanceId']
    response = ec2_client.create_tags(
        Resources=[instance_id],
        Tags=[
            {
                'Key': 'Name',
                'Value': f'ec2_with_lambda_trigger_{"".join(choice(string.ascii_lowercase) for _ in range(10))}'
            },
        ]
    )

    print("Added tag to EC2 Instance : `Creation ec2 using with lambda`")
    print("EC2 Configuration done.")


def lambda_handler(event, context):
    subnet_a, subnet_b = subnets_associated_with_VPC()
    vpc_id = get_vpc_id()
    security_group_response = create_new_security_group(vpc_id)

    security_group_id = security_group_response['GroupId']

    print(f"{subnet_a=} {subnet_b=}")
    print(f"{vpc_id=}")
    print(f"{security_group_id=}")

    create_ec2_instance(subnet_a, security_group_id)

    # TODO implement
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
