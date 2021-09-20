import json
import os
import time

import arrow
import requests
import schedule
from dotenv import load_dotenv

load_dotenv()

def test():
    print('This is working')
    rb = {
        'subject': "This is a test",
        'options': [{'title': "1"}, {'title': "2"}],
        'expiration': int(arrow.utcnow().shift(hours=1).timestamp()),
        'visibility': 'public',
        'type': 'multi'
    }
    request_body = json.dumps(rb)
    url = "https://api.groupme.com/v3/poll/71088558"
    
    
    headers = {
        'x-access-token': os.environ.get('API_KEY_GROUPME'),
        'Content-Type': 'application/json'
        }
    response = requests.post(url, data=request_body, headers=headers)
    return response

schedule.every().minute.at(':01').do(test)

while True:
    schedule.run_pending()
    time.sleep(1)