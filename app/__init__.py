from flask import Flask
from app.jobs import run

app = Flask(__name__)

@app.route('/')
def index():
    results = run()
    return [r.status_code for r in results]