import json
import os

import arrow
import requests
from dotenv import load_dotenv

load_dotenv()


def get_game_data():
    base_url = 'https://api.the-odds-api.com/v4'
    api_key = os.environ.get('API_KEY_BET')
    sport = 'americanfootball_nfl'
    regions = 'us'
    markets = 'spreads'
    r = requests.get(f'{base_url}/sports/{sport}/odds?apiKey={api_key}&regions={regions}&markets={markets}')
    return r.json()

def build_form(game):
    subject = f"{game['away_team']} @ {game['home_team']}"
    start_time = arrow.get(game['commence_time'])
    books = game['bookmakers']
    books.sort(key=lambda x: x['key'])
    book = books[0]
    options = []
    
    for market in book['markets']:
        for outcome in market['outcomes']:
            spread = outcome.get('point', 'PK')
            try:
                str_spread = str(spread) if spread < 0 else f'+{str(spread)}'
            except:
                str_spread = spread
            if spread > 0:
                options.append({'title': f"{outcome['name']} {str_spread} (1 point)"})
                options.append({'title': f"{outcome['name']} ML (3 points)"})
            elif spread < 0:
                options.append({'title': f"{outcome['name']} {str_spread} (2 points)"})
                options.append({'title': f"{outcome['name']} ML (1 point)"})
    request_body = {
        'subject': subject,
        'options': options,
        'expiration': int(start_time.shift(minutes=-15).timestamp()),
        'visibility': 'anonymous',
        'type': 'single'
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
    now = arrow.utcnow()
    # if now.format('dddd') not in {'Saturday', 'Sunday', 'Monday'}:
    #     return
    data = get_game_data()
    output = []
    for game in data:
        kickoff = arrow.get(game['commence_time'])
        # if kickoff < now.shift(hours=3):
        output.append(create_poll(game))
    return output

