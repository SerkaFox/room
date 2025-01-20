from flask import Flask
from flask_mysqldb import MySQL
from flask_bcrypt import Bcrypt
import pymysql
from datetime import timedelta


app = Flask(__name__)
mysql = MySQL(app)
bcrypt = Bcrypt(app)

app.secret_key = 'your_secret_key'

# Настройки MySQL
app.config['MYSQL_HOST'] = 'serkafox.mysql.pythonanywhere-services.com'
app.config['MYSQL_USER'] = 'serkafox'
app.config['MYSQL_PASSWORD'] = 'forum785'
app.config['MYSQL_DB'] = 'serkafox$default'
app.config['MYSQL_DATABASE_CHARSET'] = 'utf8mb4'
app.config['JWT_SECRET_KEY'] = 'your_jwt_secret_key'
app.config['JWT_EXPIRATION_DELTA'] = timedelta(days=7)  # Срок действия токена

from app import auth, chat_sql, games, quiz, roulette
