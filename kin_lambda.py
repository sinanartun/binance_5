import asyncio
import datetime
import os
from operator import itemgetter

import boto3
import requests
from binance import AsyncClient, BinanceSocketManager
from botocore.exceptions import ClientError


def handler(event, context):
    asyncio.run(main())


def get_current_region_imds_v2():
    token_url = 'http://169.254.169.254/latest/api/token'
    token_headers = {'X-aws-ec2-metadata-token-ttl-seconds': '21600'}  # Token TTL set to 6 hours
    token_response = requests.put(token_url, headers=token_headers)
    token = token_response.content.decode('utf-8')
    metadata_headers = {'X-aws-ec2-metadata-token': token}
    region_url = 'http://169.254.169.254/latest/dynamic/instance-identity/document'
    region_response = requests.get(region_url, headers=metadata_headers)
    region_data = region_response.json()

    return region_data['region']


def get_all_kinesis_streams():
    region_name = get_current_region_imds_v2()
    kinesis = boto3.client('kinesis', region_name=region_name)
    paginator = kinesis.get_paginator('list_streams')

    all_streams = []
    for page in paginator.paginate():
        for stream_name in page['StreamNames']:
            stream_description = kinesis.describe_stream(StreamName=stream_name)
            creation_time = stream_description['StreamDescription']['StreamCreationTimestamp']
            all_streams.append({
                'StreamName': stream_name,
                'CreationTime': creation_time,
            })

    return sorted(all_streams, key=itemgetter('CreationTime'), reverse=True)


async def main():
    current_region = get_current_region_imds_v2()
    kinesis_client = boto3.client(
        'kinesis',
        region_name=current_region
    )

    kinesis_stream_name_path = '/tmp/kinesis_stream_name'

    if os.path.exists(kinesis_stream_name_path):
        with open(kinesis_stream_name_path, "r") as f:
            kinesis_stream_name = f.read()
    else:
        kinesis_streams = get_all_kinesis_streams()

        if len(kinesis_streams) < 1:
            print(f"There is no Kinesis Data Stream in your Region: {current_region} !!!")
            print(f"Create a Kinesis Data Stream in: {current_region} !!!")
            exit()
        kinesis_stream_name = kinesis_streams[0]['StreamName']
        f = open(kinesis_stream_name_path, 'w')
        f.write(kinesis_stream_name)
        f.close()

    binance_client = await AsyncClient.create()
    bsm = BinanceSocketManager(binance_client)
    trade_socket = bsm.trade_socket('BTCUSDT')
    # BTCUSDT parametresindeki market hareketlerinin datasını istiyoruz.
    async with trade_socket as tscm:
        while True:
            res = await tscm.recv()
            print(res)

            timestamp = f"{datetime.datetime.fromtimestamp(int(res['T'] / 1000)):%Y-%m-%d %H:%M:%S}"
            maker = '0'
            if res['m']:  # Satın almış ise 1, satış yaptı ise 0.
                maker = '1'

            line = str(res['t']) + '\t'
            line += str(res['s']) + '\t'
            line += '{:.2f}'.format(round(float(res['p']), 2)) + '\t'
            line += str(res['q'])[0:-3] + '\t'
            line += str(timestamp) + '\t'
            line += str(maker) + '\n'

            print(line)
            try:
                response = kinesis_client.put_record(StreamName=kinesis_stream_name, Data=line,
                                                     PartitionKey=str(res['t']))

            except ClientError:
                print(f"Couldn't put record in stream {kinesis_stream_name}")
                raise
            else:
                print(response)
            print(res)

    await binance_client.close_connection()
