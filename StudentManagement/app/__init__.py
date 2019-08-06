from flask import Flask
from app.database import DB
app=Flask(__name__)
app.secret_key='secretkey'
app.config['JSON_SORT_KEYS'] = False
DB.init()
