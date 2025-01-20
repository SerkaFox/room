from flask import render_template, request, jsonify, redirect, url_for, send_from_directory, make_response
from app import app, mysql
from werkzeug.utils import secure_filename
import os
import json
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
    user = get_current_user()
    if not user:
        flash('Вам нужно войти в систему', 'warning')
        return redirect('/login')

    excluded_users = ['profe', 'serka']
    cur = mysql.connection.cursor()
    query = f"""
        SELECT username, estrellas, star_thresholds, porcentaje
        FROM users
        WHERE username NOT IN ({', '.join(['%s'] * len(excluded_users))})
        ORDER BY estrellas DESC, username ASC
    """
    cur.execute(query, excluded_users)
    all_users = cur.fetchall()

    # Преобразование активированных наград в список
    users_with_thresholds = []
    for username, estrellas, star_thresholds, porcentaje in all_users:
        activated_thresholds = json.loads(star_thresholds) if star_thresholds else []
        users_with_thresholds.append((username, estrellas, activated_thresholds, porcentaje))

    cur.close()

    return render_template(
        'all_users.html',
        username=user['username'],
        all_users=users_with_thresholds
    )



@app.route('/update_stars', methods=['POST'])
def update_stars():
    try:
        user = get_current_user()
        if not user:
            return jsonify({"success": False, "message": "Usuario no autenticado."}), 401

        data = request.get_json()
        if not data:
            return jsonify({"success": False, "message": "No se enviaron datos."}), 400

        username = data.get('username')
        threshold = data.get('threshold')  # Используем threshold вместо change

        # Проверяем наличие обязательных параметров
        if not username or threshold is None:
            return jsonify({"success": False, "message": "Datos inválidos. Faltan parámetros obligatorios."}), 400

        try:
            threshold = int(threshold)  # Преобразуем threshold в целое число
        except ValueError:
            return jsonify({"success": False, "message": "El parámetro 'threshold' debe ser un número entero."}), 400

        # Логика обработки изменений звёзд
        cur = mysql.connection.cursor()
        cur.execute("SELECT estrellas, star_thresholds FROM users WHERE username = %s", [username])
        result = cur.fetchone()

        if result is None:
            return jsonify({"success": False, "message": "Usuario no encontrado."}), 404

        current_stars, star_thresholds = result

        # Преобразуем star_thresholds в список
        if star_thresholds:
            activated_thresholds = json.loads(star_thresholds)
        else:
            activated_thresholds = []

        # Проверяем, можно ли добавить звезду для данного порога
        if threshold in activated_thresholds:
            return jsonify({"success": False, "message": "Esta estrella ya fue activada."}), 400

        # Добавляем звезду
        activated_thresholds.append(threshold)
        new_stars = current_stars + 1

        # Обновляем данные в базе
        cur.execute(
            "UPDATE users SET estrellas = %s, star_thresholds = %s WHERE username = %s",
            [new_stars, json.dumps(activated_thresholds), username]
        )
        mysql.connection.commit()
        cur.close()

        return jsonify({"success": True, "new_stars": new_stars, "activated_thresholds": activated_thresholds})

    except Exception as e:
        print(f"Error en /update_stars: {e}")
        return jsonify({"success": False, "message": "Error interno del servidor."}), 500


@app.route('/update_stars_simple', methods=['POST'])
def update_stars_simple():
    try:
        user = get_current_user()
        if not user:
            return jsonify({"success": False, "message": "Usuario no autenticado."}), 401

        data = request.get_json()
        if not data:
            return jsonify({"success": False, "message": "No se enviaron datos."}), 400

        username = data.get('username')
        threshold = data.get('threshold')

        if not username or threshold is None:
            return jsonify({"success": False, "message": "Datos inválidos. Faltan parámetros obligatorios."}), 400

        try:
            threshold = int(threshold)  # Преобразуем threshold в целое число
        except ValueError:
            return jsonify({"success": False, "message": "El parámetro 'threshold' debe ser un número entero."}), 400

        cur = mysql.connection.cursor()
        cur.execute("SELECT estrellas FROM users WHERE username = %s", [username])
        result = cur.fetchone()

        if result is None:
            return jsonify({"success": False, "message": "Usuario no encontrado."}), 404

        current_stars = result[0]
        new_stars = current_stars + threshold

        if new_stars < 0:
            return jsonify({"success": False, "message": "No se pueden tener menos de 0 estrellas."}), 400

        # Обновляем количество звёзд
        cur.execute("UPDATE users SET estrellas = %s WHERE username = %s", [new_stars, username])
        mysql.connection.commit()
        cur.close()

        return jsonify({"success": True, "new_stars": new_stars})

    except Exception as e:
        print(f"Error en /update_stars_simple: {e}")
        return jsonify({"success": False, "message": "Error interno del servidor."}), 500

