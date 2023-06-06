import boto3
import requests


def get_current_region_imds_v2():
    # First, we need to get the session token
    TOKEN_URL = 'http://169.254.169.254/latest/api/token'
    token_headers = {'X-aws-ec2-metadata-token-ttl-seconds': '21600'}  # Token TTL set to 6 hours
    token_response = requests.put(TOKEN_URL, headers=token_headers)
    token = token_response.content.decode('utf-8')

    # Now we can use this token to make further metadata requests
    metadata_headers = {'X-aws-ec2-metadata-token': token}
    REGION_URL = 'http://169.254.169.254/latest/dynamic/instance-identity/document'
    region_response = requests.get(REGION_URL, headers=metadata_headers)
    region_data = region_response.json()

    return region_data['region']


def get_all_kinesis_streams(region_name):
    kinesis = boto3.client('kinesis', region_name=region_name)
    paginator = kinesis.get_paginator('list_streams')

    all_streams = []
    for page in paginator.paginate():
        all_streams.extend(page['StreamNames'])

    return all_streams


if __name__ == '__main__':
    streams = get_all_kinesis_streams(get_current_region_imds_v2())
    print(streams)
