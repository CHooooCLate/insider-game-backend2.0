import boto3
import datetime
import json
import random

# デバッグするときに使う
from pprint import pprint

from boto3.dynamodb.conditions import Key, Attr

dynamodb = boto3.resource('dynamodb')
playerTable = dynamodb.Table('Player')
themeTable = dynamodb.Table('Theme')
sequenceTable = dynamodb.Table('Sequence')

def lambda_handler(event, context):
    # GameID
    gameId = json.loads(event.get('body', '{}')).get('gameId')

    domain_name = event.get('requestContext',{}).get('domainName')
    stage       = event.get('requestContext',{}).get('stage')

    # エントリー済みのプレイヤーを取得
    players = playerTable.scan(
         FilterExpression=Attr('game_id').eq(gameId)
    ).get('Items')
    if players is None:
        return { 'statusCode': 500,'body': 'something went wrong' }

    # テーマのIDの最大値を取得
    sequenceKey = 'Theme'
    themeCount = sequenceTable.get_item(
        Key = {
            'sequence_key' : sequenceKey
        }
    )

    # ランダムにテーマ取得
    num = random.randint(1, themeCount['Item']['sequence'])
    theme = themeTable.get_item(
        Key = {
            'id' : str(num)
        }
    )

    # 役職リストを作成
    roleList = {}
    for i in range(len(players)):
        if i == 0:
            roleList[i] = 'insider'
        elif i == 1:
            roleList[i] = 'master'
        else:
            roleList[i] = 'common'

    datetimeFormat = datetime.datetime.today()

    for player in players:
        # プレイヤーごとに役職選択
        role = random.choice(list(roleList.items()))

        del roleList[role[0]]

        # プレイヤーの役職、テーマ、スタンプを更新
        playerTable.update_item(
            Key= {
                'id': player['id'],
                'game_id': gameId
            },
            UpdateExpression='set #r=:r, #t=:theme, #s=:stamp',
            ExpressionAttributeNames={
                '#r': 'role',
                '#t': 'theme',
                '#s': 'stamp'
            },
            ExpressionAttributeValues={
                ':r': role[1],
                ':theme': theme['Item']['name'],
                ':stamp': datetimeFormat.strftime("%Y/%m/%d %H:%M:%S")
            }
        )

    # 再設定したプレイヤーリストを取得
    players = playerTable.scan(
         FilterExpression=Attr('game_id').eq(gameId)
    ).get('Items')

    apigw_management = boto3.client('apigatewaymanagementapi',
                                    endpoint_url=F"https://{domain_name}/{stage}")

    # 各プレイヤーに開始を通知
    for player in players:
        result = json.dumps({
            'action': 'start',
            'players': players
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
