import boto3

# デバッグするときに使う
from pprint import pprint

from boto3.dynamodb.conditions import Key, Attr

dynamodb = boto3.resource('dynamodb')
playerTable = dynamodb.Table('Player')

def lambda_handler(event, context):
    connection_id = event.get('requestContext',{}).get('connectionId')
    player = playerTable.scan(
         FilterExpression=Attr('id').eq(connection_id)
    ).get('Items')

    playerTable.delete_item(
        Key = {
            'id': connection_id,
            'game_id': player[0]['game_id']
        }
    )

    return { 'statusCode': 200, 'body': 'ok' }
