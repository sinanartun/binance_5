import asyncio
import datetime

import boto3
from binance import AsyncClient, BinanceSocketManager
from botocore.exceptions import ClientError


async def main():
    kinesis_client = boto3.client(
        'kinesis',
        region_name='eu-north-1'
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
                response = kinesis_client.put_record(StreamName='awsbc5', Data=line, PartitionKey=str('1'))

            except ClientError:
                print("Couldn't put record in stream 'binance'")
                raise
            else:
                print(response)
            print(res)

    await client.close_connection()


loop = asyncio.get_event_loop()
loop.run_until_complete(main())
