import os
from flask import Flask
from .dbManager import DataBase
# from flask_login import LoginManager

app = Flask(__name__)
db = DataBase()
