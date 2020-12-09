import json
import logging
import boto3

dynamodb = boto3.resource('dynamodb')
connections = dynamodb.Table('connection')


def lambda_handler(event, context):
    connection_id = event.get('requestContext',{}).get('connectionId')
    result = connections.delete_item(Key={ 'id': connection_id })
    return { 'statusCode': 200, 'body': 'ok' }
