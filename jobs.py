import json
import os
import time

import arrow
import requests
from dotenv import load_dotenv

load_dotenv()


def get_game_data():
    base_url = 'https://api.the-odds-api.com/v4'
    api_key = os.environ.get('API_KEY_BET')
    sport = 'americanfootball_nfl'
    regions = 'us'
    markets = 'spreads,totals'
    r = requests.get(f'{base_url}/sports/{sport}/odds?apiKey={api_key}&regions={regions}&markets={markets}')
    return r.json()

def build_form(game):
    subject = f"{game['home_team']} vs. {game['away_team']}"
    start_time = arrow.get(game['commence_time'])
    books = game['bookmakers']
    books.sort(key=lambda x: x['key'])
    book = books[-1]
    options = []
    
    for market in book['markets']:
        for outcome in market['outcomes']:
            if market['key'] == 'spreads':
                spread = outcome.get('point', 'PK')
                try:
                    spread = str(spread) if spread < 0 else f'+{str(spread)}'
                except:
                    spread = spread
                options.append({'title': f"{outcome['name']} {spread}"})
            else:
                options.append({'title': f"{outcome['name']} {outcome['point']}"})
    options.append({'title': "No Bet"})
    request_body = {
        'subject': subject,
        'options': options,
        'expiration': int(start_time.shift(minutes=-15).timestamp()),
        'visibility': 'public',
        'type': 'multi'
    }
    return request_body

def create_poll(game):
    group_id = os.environ.get('GROUPME_GROUP_ID')
    url = f"https://api.groupme.com/v3/poll/{group_id}"
    request_body = json.dumps(build_form(game))
    
    headers = {
        'x-access-token': os.environ.get('API_KEY_GROUPME'),
        'Content-Type': 'application/json'
        }
    response = requests.post(url, data=request_body, headers=headers)
    return response
    


def run():
    data = get_game_data()
    now = arrow.utcnow()
    for game in data:
        kickoff = arrow.get(game['commence_time'])
        if kickoff < now.shift(hours=3):
            create_poll(game)


run()
