import boto3
import json

from boto3.dynamodb.conditions import Key, Attr

dynamodb = boto3.resource('dynamodb')
playerTable = dynamodb.Table('Player')

def lambda_handler(event, context):
    # 操作したPlayerID
    votePlayerId = json.loads(event.get('body', '{}')).get('votePlayerId')
    # 投票先のPlayerID
    targetPlayerId = json.loads(event.get('body', '{}')).get('targetPlayerId')
    # GameID
    gameId = json.loads(event.get('body', '{}')).get('gameId')

    domain_name = event.get('requestContext',{}).get('domainName')
    stage       = event.get('requestContext',{}).get('stage')

    # 再設定したプレイヤーリストを取得
    players = playerTable.scan(
         FilterExpression=Attr('game_id').eq(gameId)
    ).get('Items')

    apigw_management = boto3.client('apigatewaymanagementapi',
                                    endpoint_url=F"https://{domain_name}/{stage}")

    # 各プレイヤーに開始を通知
    for player in players:
        result = json.dumps({
            'action': 'vote',
            'vote_player_id': votePlayerId,
            'target_player_id': targetPlayerId
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
