import json
import mysql.connector
import os

def lambda_handler(event, context):
    print(event["Records"][0]["s3"]["bucket"]["name"])
    bucket = event["Records"][0]["s3"]["bucket"]["name"]
    key = event["Records"][0]["s3"]["object"]["key"]

    s3_uri = "s3://" + bucket + "/" + key

    try:
        conn = mysql.connector.connect(
            host="bubenimcluster.cluster-cf8yseyg6rz2.eu-west-1.rds.amazonaws.com",
            user="admin",
            password="haydegidelum",
            database="bubenimdatabase",
            port=63306
        )
        sql = "LOAD DATA FROM S3 '"
        sql += s3_uri
        sql +="""'
INTO TABLE bubenimdatabase.BTCUSDT 
FIELDS TERMINATED BY '\t'
LINES TERMINATED BY '\n'
(bid, parameter, price, quantity, time, maker);"""

        cursor = conn.cursor()
        cursor.execute(sql)
        conn.commit()
        cursor.close()
        conn.close()

        return {
            'statusCode': 200,
            'body': json.dumps("success")
        }

    except mysql.connector.Error as err:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(err)})
        }
