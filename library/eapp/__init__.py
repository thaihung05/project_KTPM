from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = "passwordAbc123"
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:Abc123@localhost/librarydb?charset=utf8mb4"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
app.config["due_time"] = 14
app.config["PAGE_SIZE"] = 50
app.config['FINE_PER_DAY'] = 5000


db = SQLAlchemy(app)
login = LoginManager(app=app)
login.login_view = 'login_view'
