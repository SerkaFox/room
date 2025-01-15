from flask import render_template, request, jsonify, redirect, url_for, send_from_directory, make_response
from app import app, mysql
from werkzeug.utils import secure_filename
import os
from app.auth import get_current_user


UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/save_result', methods=['POST'])
def save_result():
    user = get_current_user()  # Проверяем токен и получаем данные пользователя
    if not user:  # Если пользователь не авторизован
        return jsonify({'status': 'error', 'message': 'Not logged in.'}), 403

    data = request.get_json()
    score = data.get('score', 0)

    user_id = user['user_id']  # Получаем `user_id` из токена
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO game_results (user_id, score) VALUES (%s, %s)", (user_id, score))
    mysql.connection.commit()
    cur.close()

    return jsonify({'status': 'success', 'message': 'Score saved successfully.'})

@app.route('/save_galaga_result', methods=['POST'])
def save_galaga_result():
    user = get_current_user()  # Проверяем токен и получаем данные пользователя
    if not user:  # Если пользователь не авторизован
        return jsonify({'status': 'error', 'message': 'Not logged in.'}), 403

    data = request.get_json()
    score = data.get('score', 0)

    user_id = user['user_id']  # Получаем `user_id` из токена
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO galaga_results (user_id, score) VALUES (%s, %s)", (user_id, score))
    mysql.connection.commit()
    cur.close()

    return jsonify({'status': 'success', 'message': 'Galaga score saved successfully.'})

@app.route('/galaga')
def galaga():
    return send_from_directory('static/galaga', 'index.html')