import boto3

dynamodb = boto3.resource('dynamodb')
playerTable = dynamodb.Table('Player')

def lambda_handler(event, context):
    connection_id = event.get('requestContext',{}).get('connectionId')

    playerTable.delete_item(Key={ 'id': connection_id })

    return { 'statusCode': 200, 'body': 'ok' }
