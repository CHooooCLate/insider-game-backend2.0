import json
import sys
import logging
import boto3
import botocore

dynamodb = boto3.resource('dynamodb')
connections = dynamodb.Table('connection')


def lambda_handler(event, context):

    post_data = json.loads(event.get('body', '{}')).get('data')
    print(post_data)
    domain_name = event.get('requestContext',{}).get('domainName')
    stage       = event.get('requestContext',{}).get('stage')

    items = connections.scan(ProjectionExpression='id').get('Items')
    if items is None:
        return { 'statusCode': 500,'body': 'something went wrong' }

    apigw_management = boto3.client('apigatewaymanagementapi',
                                    endpoint_url=F"https://{domain_name}/{stage}")
    print(domain_name)
    print(stage)
    for item in items:
        try:
            print(item)
            _ = apigw_management.post_to_connection(ConnectionId=item['id'],
                                                         Data=post_data)
        except:
            import traceback
            traceback.print_exc()
    return { 'statusCode': 200,'body': 'ok' }
