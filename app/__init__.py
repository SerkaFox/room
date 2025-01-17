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
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'alumno'
app.config['MYSQL_PASSWORD'] = 'alumno'
app.config['MYSQL_DB'] = 'flask_auth'
app.config['MYSQL_DATABASE_CHARSET'] = 'utf8mb4'
app.config['JWT_SECRET_KEY'] = 'your_jwt_secret_key'
app.config['JWT_EXPIRATION_DELTA'] = timedelta(days=7)  # Срок действия токена

from app import auth, chat_sql, games, quiz, roulette 
