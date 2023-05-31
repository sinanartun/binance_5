import json

import boto3
import requests

url_token = "http://169.254.169.254/latest/api/token"
url_meta_data = "http://169.254.169.254/latest/meta-data/iam/info"
headers = {"X-aws-ec2-metadata-token-ttl-seconds": "21600"}

# Request to get the token
response = requests.put(url_token, headers=headers)

if response.status_code == 200:
    token = response.text
    headers["X-aws-ec2-metadata-token"] = token

    # Request to get the meta-data
    response = requests.get(url_meta_data, headers=headers)

    s3 = boto3.client(
        's3'
    )
    res = s3.list_buckets()
    print(json.dumps(res, indent=4, sort_keys=True, default=str))

    if response.status_code == 200:
        print(response.text)
    else:
        print(f"Error: Unable to fetch meta-data. HTTP status code: {response.status_code}")
else:
    print(f"Error: Unable to get token. HTTP status code: {response.status_code}")
