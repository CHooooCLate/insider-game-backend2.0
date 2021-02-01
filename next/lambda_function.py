import boto3
import json

# デバッグするときに使う
#from pprint import pprint

from boto3.dynamodb.conditions import Key, Attr

dynamodb = boto3.resource('dynamodb')
playerTable = dynamodb.Table('Player')

def lambda_handler(event, context):
    # GameID
    gameId = json.loads(event.get('body', '{}')).get('gameId')
    # 経過時間
    elapsedTime = json.loads(event.get('body', '{}')).get('elapsedTime')

    domain_name = event.get('requestContext',{}).get('domainName')
    stage       = event.get('requestContext',{}).get('stage')

    # エントリー済みのプレイヤーを取得
    players = playerTable.scan(
         FilterExpression=Attr('game_id').eq(gameId)
    ).get('Items')
    if players is None:
        return { 'statusCode': 500,'body': 'something went wrong' }

    apigw_management = boto3.client('apigatewaymanagementapi',
                                    endpoint_url=F"https://{domain_name}/{stage}")

    # 各プレイヤーに開始を通知
    for player in players:
        result = json.dumps({
            'action': 'next',
            'elapsedTime': elapsedTime
        })

        try:
            _ = apigw_management.post_to_connection(ConnectionId=player['id'], Data=result)
        except:
            import traceback
            traceback.print_exc()

    return {
        'statusCode': 200,
        'body': 'ok'
    }
