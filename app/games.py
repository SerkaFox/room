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
    
@app.route('/all_users')
def all_users():
    # Получаем текущего пользователя
    user = get_current_user()
    if not user:
        flash('Вам нужно войти в систему', 'warning')
        return redirect('/login')

    # Список пользователей, которых нужно исключить
    excluded_users = ['profe', 'serka']  # Добавьте здесь имена исключаемых пользователей

    # SQL-запрос для получения всех пользователей, кроме исключенных
    cur = mysql.connection.cursor()
    format_strings = ', '.join(['%s'] * len(excluded_users))
    query = f"""
        SELECT username, estrellas 
        FROM users
        WHERE username NOT IN ({format_strings})
        ORDER BY estrellas DESC, username ASC
    """
    cur.execute(query, excluded_users)
    all_users = cur.fetchall()
    cur.close()

    # Передаем список пользователей в шаблон
    return render_template(
        'all_users.html',
        username=user['username'],
        all_users=all_users
    )




@app.route('/update_stars', methods=['POST'])
def update_stars():
    user = get_current_user()
    # if not user or user['username'] != 'profe':
    #     return jsonify({"success": False, "message": "Acceso denegado."}), 403

    data = request.get_json()
    username = data.get('username')
    threshold = data.get('threshold')

    if not username or not threshold:
        return jsonify({"success": False, "message": "Datos inválidos."}), 400

    cur = mysql.connection.cursor()
    cur.execute("SELECT estrellas, last_star_threshold FROM users WHERE username = %s", [username])
    result = cur.fetchone()

    if result is None:
        return jsonify({"success": False, "message": "Usuario no encontrado."}), 404

    current_stars, last_threshold = result
    if threshold <= last_threshold:
        return jsonify({"success": False, "message": "El usuario ya recibió una estrella para este nivel."}), 400

    # Обновляем количество звезд и порог
    new_stars = current_stars + 1
    cur.execute(
        "UPDATE users SET estrellas = %s, last_star_threshold = %s WHERE username = %s",
        [new_stars, threshold, username]
    )
    mysql.connection.commit()
    cur.close()

    return jsonify({"success": True, "new_stars": new_stars})

