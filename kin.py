import asyncio
import datetime

import boto3
import requests
from binance import AsyncClient, BinanceSocketManager
from botocore.exceptions import ClientError


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


async def main():
    kinesis_client = boto3.client(
        'kinesis',
        region_name=get_current_region_imds_v2()
    )

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
                # response = kinesis_client.put_record(StreamName='awsbc5', Data=line, PartitionKey=str(res['t']))
                response = kinesis_client.put_record(StreamName='awsbc5', Data=line, PartitionKey=str(res['t']))

            except ClientError:
                print("Couldn't put record in stream 'binance'")
                raise
            else:
                print(response)
            print(res)

    await client.close_connection()


loop = asyncio.get_event_loop()
loop.run_until_complete(main())
