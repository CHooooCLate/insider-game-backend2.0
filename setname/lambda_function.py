import boto3
import datetime
import json

from boto3.dynamodb.conditions import Key, Attr

dynamodb = boto3.resource('dynamodb')
playerTable = dynamodb.Table('Player')
sequenceTable = dynamodb.Table('Sequence')

def lambda_handler(event, context):
    # 接続ID
    connection_id = event.get('requestContext',{}).get('connectionId')
    # リクエスト
    body = json.loads(event.get('body', '{}'))
    # プレイヤー名
    name = body['name']
    # GameID
    body.setdefault('gameId', '')
    gameId = body['gameId']

    domain_name = event.get('requestContext',{}).get('domainName')
    stage       = event.get('requestContext',{}).get('stage')

    if gameId == '':
        sequenceKey = 'Game'

        # シーケンスを1つ進める
        res = sequenceTable.update_item(
            Key= {
                'sequence_key': sequenceKey
            },
            UpdateExpression="ADD #name :increment",
            ExpressionAttributeNames={
                '#name':'sequence'
            },
            ExpressionAttributeValues={
                ":increment": int(1)
            },
            ReturnValues="UPDATED_NEW"
        )

        gameId = str(res['Attributes']['sequence'])

    datetimeFormat = datetime.datetime.today()

    # プレイヤーを追加
    playerTable.put_item(
        Item = {
            'id' : connection_id,
            'game_id' : gameId,
            'name' : name,
            'theme' : '0',
            'role' : '0',
            'stamp' : datetimeFormat.strftime("%Y/%m/%d %H:%M:%S")
        }
    )

    # GameIDを通知
    apigw_management = boto3.client('apigatewaymanagementapi',
                                    endpoint_url=F"https://{domain_name}/{stage}")

    # 再設定したプレイヤーリストを取得
    players = playerTable.scan(
         FilterExpression=Attr('game_id').eq(gameId)
    ).get('Items')
    # 各プレイヤーに開始を通知
    for player in players:
        try:
            result = json.dumps({
                'action': 'setname',
                'playerId': connection_id,
                'gameId': gameId,
                'name': name
            })
            _ = apigw_management.post_to_connection(ConnectionId=player['id'],
                                                         Data=result)
        except:
            import traceback
            traceback.print_exc()

    return {
        'statusCode': 200,
        'body': 'ok'
    }
