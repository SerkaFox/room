from flask import render_template, request, jsonify, session, redirect, url_for, flash, redirect
import pymysql
from app import app, mysql
import random
from app.auth import get_current_user, logout


from werkzeug.utils import secure_filename
import os

# Путь для сохранения изображений
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Убедитесь, что папка для загрузки изображений существует
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/chat', methods=['GET', 'POST'])
def chat():
    user = get_current_user()  # Получаем данные пользователя из токена
    if not user:  # Если пользователь не авторизован
        flash('Вам нужно войти в систему', 'warning')
        return redirect('/login')

    user_id = user['user_id']  # Извлекаем user_id из токена
    username = user['username']  # Извлекаем имя пользователя из токена

    if request.method == 'POST':
        message = request.form.get('message', '').strip()
        image = request.files.get('image')

        image_path = None
        if image and image.filename != '':
            filename = secure_filename(image.filename)
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            image.save(image_path)

        cur = mysql.connection.cursor()
        cur.execute("""
            INSERT INTO chat_messages (user_id, username, message, image_path)
            VALUES (%s, %s, %s, %s)
        """, (user_id, username, message, image_path))
        mysql.connection.commit()
        cur.close()

        flash('Сообщение отправлено!', 'success')
        return redirect(url_for('chat'))

    # Получение последних сообщений
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT id, username, message, image_path, created_at
        FROM chat_messages
        ORDER BY created_at DESC
        LIMIT 20
    """)
    messages = cur.fetchall()
    cur.close()

    # Передаём текущего пользователя в шаблон
    return render_template('chat.html', messages=messages, current_user=username)


from flask import request, jsonify

@app.route('/edit_message', methods=['POST'])
def edit_message():
    user = get_current_user()  # Проверяем токен и получаем данные пользователя
    if not user:  # Если пользователь не авторизован
        return jsonify({'error': 'Unauthorized'}), 403

    data = request.get_json()
    message_id = data.get('message_id')
    updated_message = data.get('updated_message')

    if not message_id or not updated_message:  # Проверка входных данных
        return jsonify({'error': 'Invalid data'}), 400

    cur = mysql.connection.cursor()

    # Проверяем, что сообщение принадлежит текущему пользователю
    cur.execute("SELECT username FROM chat_messages WHERE id = %s", (message_id,))
    result = cur.fetchone()
    if not result or result[0] != user['username'].lower():  # Сравниваем имя пользователя из токена
        cur.close()
        return jsonify({'error': 'Permission denied'}), 403

    # Обновляем сообщение
    cur.execute("UPDATE chat_messages SET message = %s WHERE id = %s", (updated_message, message_id))
    mysql.connection.commit()

    # Получаем обновленные данные из базы
    cur.execute("SELECT id, username, message, image_path, created_at FROM chat_messages WHERE id = %s", (message_id,))
    updated_message_data = cur.fetchone()
    cur.close()

    return jsonify({
        'id': updated_message_data[0],
        'username': updated_message_data[1],
        'message': updated_message_data[2],
        'image_path': updated_message_data[3],
        'created_at': updated_message_data[4].strftime('%Y-%m-%d %H:%M:%S')
    }), 200



@app.route('/delete_message', methods=['POST'])
def delete_message():
    user = get_current_user()  # Проверяем токен и получаем данные пользователя
    if not user:  # Если пользователь не авторизован
        return jsonify({'error': 'Unauthorized'}), 403

    data = request.get_json()
    message_id = data.get('message_id')

    if not message_id:  # Проверяем, что `message_id` передан
        return jsonify({'error': 'Invalid data'}), 400

    cur = mysql.connection.cursor()

    # Проверяем, что сообщение принадлежит текущему пользователю
    cur.execute("SELECT username FROM chat_messages WHERE id = %s", (message_id,))
    result = cur.fetchone()
    if not result or result[0] != user['username']:  # Сравниваем имя пользователя из токена
        cur.close()
        return jsonify({'error': 'Permission denied'}), 403

    # Удаляем сообщение
    cur.execute("DELETE FROM chat_messages WHERE id = %s", (message_id,))
    mysql.connection.commit()
    cur.close()

    return jsonify({'status': 'success'}), 200




@app.route('/fetch_messages', methods=['GET'])
def fetch_messages():
    user = get_current_user()
    if not user:  # Проверяем, авторизован ли пользователь
        return jsonify({'error': 'Unauthorized'}), 403

    user_id = user['user_id']  # Извлекаем user_id из токена
    username = user['username']  # Извлекаем имя пользователя из токена
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT id, username, message, image_path, created_at
        FROM chat_messages
        ORDER BY created_at DESC
        LIMIT 20
    """)
    messages = cur.fetchall()
    cur.close()

    # Рендерим только часть HTML с сообщениями
    return render_template('messages.html', messages=messages, current_user=username)


# Настраиваем маршрут для скачивания файла
@app.route('/download/<filename>')
def download_file(filename):
    # Указываем путь к папке, где находятся файлы
    return send_from_directory('uploads', filename, as_attachment=True)


@app.route('/sql_console', methods=['GET', 'POST'])
def sql_console():
    result = []
    command_history = session.get('command_history', [])
    error = ""
    tables = []
    random_gifs = [
        "https://media.giphy.com/media/3o6ZsYm5pbbMT1A6YM/giphy.gif",
        "https://media.giphy.com/media/l41lZxzroU33typuU/giphy.gif",
        "https://media.giphy.com/media/xT9IgIc0lryrxvqVGM/giphy.gif",
        "https://media.giphy.com/media/26AHONQ79FdWZhAI0/giphy.gif",
        "https://media.giphy.com/media/111ebonMs90YLu/giphy.gif",
        "https://media.giphy.com/media/l0HlNaQ6gWfllcjDO/giphy.gif",
        "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExbTl3amN3Yms2M2phc2V6eWQ1bzZxNXA4NWl6c2c4cWMxcGpldXk4aCZlcD12MV9naWZzX3NlYXJjaCZjdD1n/V4NSR1NG2p0KeJJyr5/giphy.gif",
        "https://media.giphy.com/media/pUVOeIagS1rrqsYQJe/giphy.gif?cid=790b7611m9wjcwbk63jasezyd5o6q5p85izsg8qc1pjeuy8h&ep=v1_gifs_search&rid=giphy.gif&ct=g",
        "https://media.giphy.com/media/CuuSHzuc0O166MRfjt/giphy.gif?cid=790b7611m9wjcwbk63jasezyd5o6q5p85izsg8qc1pjeuy8h&ep=v1_gifs_search&rid=giphy.gif&ct=g",
        "https://media.giphy.com/media/xT8qBgHkfCACqvjJny/giphy.gif?cid=790b7611m9wjcwbk63jasezyd5o6q5p85izsg8qc1pjeuy8h&ep=v1_gifs_search&rid=giphy.gif&ct=g",
        "https://media.giphy.com/media/unxCGmTuBvwo2djRLA/giphy.gif?cid=ecf05e47uc9htkir7jsdx303sspch001j937gyc5j3dstvwu&ep=v1_gifs_search&rid=giphy.gif&ct=g",
        "https://media.giphy.com/media/unxCGmTuBvwo2djRLA/giphy.gif?cid=ecf05e47uc9htkir7jsdx303sspch001j937gyc5j3dstvwu&ep=v1_gifs_search&rid=giphy.gif&ct=g",
        "https://media.giphy.com/media/4hnQDVKVARZ6w/giphy.gif?cid=ecf05e47uc9htkir7jsdx303sspch001j937gyc5j3dstvwu&ep=v1_gifs_search&rid=giphy.gif&ct=g",
        "https://media.giphy.com/media/CrFLL3CnRpw5ddlBMm/giphy.gif?cid=ecf05e47na241anfwafbubhf9cuixmlly0gf65up7hwoeggd&ep=v1_gifs_search&rid=giphy.gif&ct=g",
        "https://media.giphy.com/media/JqmupuTVZYaQX5s094/giphy.gif?cid=ecf05e47na241anfwafbubhf9cuixmlly0gf65up7hwoeggd&ep=v1_gifs_search&rid=giphy.gif&ct=g",
        "https://media.giphy.com/media/okZ8eqHMUPDdLEAIkf/giphy.gif?cid=ecf05e47na241anfwafbubhf9cuixmlly0gf65up7hwoeggd&ep=v1_gifs_search&rid=giphy.gif&ct=g",
        "https://media.giphy.com/media/GfVdawuuKIU1qfLByo/giphy.gif?cid=ecf05e47na241anfwafbubhf9cuixmlly0gf65up7hwoeggd&ep=v1_gifs_search&rid=giphy.gif&ct=g",
        "https://media.giphy.com/media/78XCFBGOlS6keY1Bil/giphy.gif?cid=ecf05e47emgaxmyxitykxgw2hu10olxdgdkhz26jdvc3m567&ep=v1_gifs_search&rid=giphy.gif&ct=g",
        "https://media.giphy.com/media/RbDKaczqWovIugyJmW/giphy.gif?cid=ecf05e47emgaxmyxitykxgw2hu10olxdgdkhz26jdvc3m567&ep=v1_gifs_search&rid=giphy.gif&ct=g",
        "https://media.giphy.com/media/nFLW7PNGgN3lI68rdv/giphy.gif?cid=ecf05e4770rvbhewirlnoqqdeayo2v3jwyqhj1k29wb2yszu&ep=v1_gifs_search&rid=giphy.gif&ct=g",
        "https://media.giphy.com/media/ua7vVw9awZKWwLSYpW/giphy.gif?cid=ecf05e47bittra8yszbu2huxkgv3jcmte04ku2z1gu0xb4ue&ep=v1_gifs_search&rid=giphy.gif&ct=g"
    ]
    selected_gif = random.choice(random_gifs)  # Случайная GIF
    db_config = {
        'host': app.config['MYSQL_HOST'],
        'user': app.config['MYSQL_USER'],
        'password': app.config['MYSQL_PASSWORD'],
        'database': app.config['MYSQL_DB'],  # Указываем базу данных
        'port': app.config.get('MYSQL_PORT', 3306),  # Указываем порт, если он отличается от стандартного
        'ssl_ca': app.config.get('MYSQL_SSL_CA'),  # Указываем путь к сертификату SSL, если используется
        'ssl_disabled': False  # Убедитесь, что SSL не отключён
    }

    selected_db = session.get('selected_database')  # Получаем текущую базу из сессии

    # Получение списка баз данных
    try:
        connection = pymysql.connect(**db_config)
        with connection.cursor() as cursor:
            cursor.execute("SHOW DATABASES;")
            databases = [db[0] for db in cursor.fetchall()]

            # Исключаем системные базы данных
            excluded_databases = ['information_schema', 'mysql', 'performance_schema', 'sys', 'flask_auth']
            databases = [db for db in databases if db not in excluded_databases]
    except Exception as e:
        flash(f"Ошибка при получении списка баз данных: {str(e)}", "danger")
        databases = []
    finally:
        if 'connection' in locals() and connection.open:
            connection.close()

    # Если отправлена форма для выбора базы данных
    if request.method == 'POST' and 'database' in request.form:
        selected_db = request.form['database']
        session['selected_database'] = selected_db  # Сохраняем выбранную базу в сессии
        flash(f"База данных '{selected_db}' выбрана.", "success")
        return redirect(url_for('sql_console'))

    # Если выбрана база данных, получаем список таблиц
    if selected_db:
        try:
            connection = pymysql.connect(
                host=app.config['MYSQL_HOST'],
                user=app.config['MYSQL_USER'],
                password=app.config['MYSQL_PASSWORD'],
                database=selected_db
            )
            with connection.cursor() as cursor:
                cursor.execute("SHOW TABLES;")
                tables = [table[0] for table in cursor.fetchall()]
        except Exception as e:
            flash(f"Ошибка при получении списка таблиц: {str(e)}", "danger")
        finally:
            if 'connection' in locals() and connection.open:
                connection.close()

    # Если отправлена форма с SQL-командой
    if request.method == 'POST' and 'sql_command' in request.form:
        sql_command = request.form['sql_command']
        # Сохраняем команду в историю
        if sql_command not in command_history:
            command_history.insert(0, sql_command)
            if len(command_history) > 10:  # Храним только последние 10 команд
                command_history.pop()
            session['command_history'] = command_history
        if not selected_db:
            flash("Сначала выберите базу данных.", "warning")
            return redirect(url_for('sql_console'))

        try:
            connection = pymysql.connect(
                host=app.config['MYSQL_HOST'],
                user=app.config['MYSQL_USER'],
                password=app.config['MYSQL_PASSWORD'],
                database=selected_db,
                cursorclass=pymysql.cursors.DictCursor  # Включаем DictCursor
            )
            with connection.cursor() as cursor:
                cursor.execute(sql_command)

                # Если это SELECT, возвращаем результат
                if sql_command.strip().upper().startswith("SELECT"):
                    result = cursor.fetchall()
                else:
                    connection.commit()
                    result = [{"status": "Comando ha ejecutado correcto."}]

                # Обновляем список баз данных после создания/удаления базы
                if sql_command.strip().upper().startswith(("CREATE DATABASE", "DROP DATABASE")):
                    cursor.execute("SHOW DATABASES;")
                    databases = [db[0] for db in cursor.fetchall()]
                    databases = [db for db in databases if db not in excluded_databases]  # Применяем фильтр
        except Exception as e:
            error = str(e)
        finally:
            if 'connection' in locals() and connection.open:
                connection.close()

    return render_template(
        'sql_console.html',
        databases=databases,
        selected_db=selected_db,
        tables=tables,
        result=result,
        error=error,
        selected_gif=selected_gif,
        command_history=command_history,
    )


