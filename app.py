from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, send_from_directory, make_response
from flask_bcrypt import Bcrypt
from flask_mysqldb import MySQL
from wtforms import Form, StringField, PasswordField, validators
from wtforms.validators import DataRequired
import pymysql
import jwt
from datetime import datetime, timedelta, timezone

# Инициализация Flask
app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Настройки MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'alumno'
app.config['MYSQL_PASSWORD'] = 'alumno'
app.config['MYSQL_DB'] = 'flask_auth'
app.config['MYSQL_DATABASE_CHARSET'] = 'utf8mb4'
app.config['JWT_SECRET_KEY'] = 'your_jwt_secret_key'
app.config['JWT_EXPIRATION_DELTA'] = timedelta(days=7)  # Срок действия токена


@app.after_request
def add_no_cache_headers(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response


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
    if not result or result[0] != user['username']:  # Сравниваем имя пользователя из токена
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

# Инициализация MySQL и Bcrypt
mysql = MySQL(app)
bcrypt = Bcrypt(app)

# Форма регистрации
class RegistrationForm(Form):
    username = StringField('Username', [validators.Length(min=4, max=50), DataRequired()])
    email = StringField('Email', [validators.Length(min=6, max=100), validators.Email(), DataRequired()])
    password = PasswordField('Password', [
        validators.Length(min=6),
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Confirm Password')

# Форма логина
class LoginForm(Form):
    username = StringField('Username', [validators.DataRequired()])
    password = PasswordField('Password', [validators.DataRequired()])

@app.route('/')
def index():
    user = get_current_user()
    if user:  # Если пользователь авторизован
        return redirect(url_for('cuenta'))
    return render_template('index.html')  # Главная страница для неавторизованных пользователей

    
    
@app.route('/reset_profile', methods=['GET', 'POST'])
def reset_profile():
    if request.method == 'POST':
        email = request.form['email']
        new_name = request.form['name']
        new_password = request.form['password']

        # Проверяем, существует ли пользователь с таким email
        cur = mysql.connection.cursor()
        cur.execute("SELECT id FROM users WHERE email = %s", [email])
        user = cur.fetchone()

        if user:
            user_id = user[0]
            # Обновляем имя, если поле не пустое
            if new_name.strip():
                cur.execute("UPDATE users SET username = %s WHERE id = %s", [new_name, user_id])
                flash("✅ Tu nombre de usuario ha sido actualizado exitosamente.", "success")
            # Обновляем пароль, если поле не пустое
            if new_password.strip():
                hashed_password = bcrypt.generate_password_hash(new_password).decode('utf-8')
                cur.execute("UPDATE users SET password_hash = %s WHERE id = %s", [hashed_password, user_id])
                flash("✅ Tu contraseña ha sido actualizada exitosamente.", "success")

            mysql.connection.commit()
        else:
            flash("⚠️ No se encontró un usuario con ese correo electrónico. Verifica e inténtalo nuevamente.", "danger")

        cur.close()
        return redirect(url_for('reset_profile'))

    return render_template('reset_profile.html')
    



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
        'password': app.config['MYSQL_PASSWORD']
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



# Регистрация
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm(request.form)
    if request.method == 'POST' and form.validate():
        username = form.username.data
        email = form.email.data
        password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')

        # Сохранение в базу данных
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s)", (username, email, password))
        mysql.connection.commit()
        cur.close()

        flash('Вы успешно зарегистрированы!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)
    
@app.before_request
def refresh_auth_token():
    user = get_current_user()
    if user:
        token = jwt.encode({
            'user_id': user['user_id'],
            'username': user['username'],
            'exp': datetime.now(timezone.utc) + app.config['JWT_EXPIRATION_DELTA']
        }, app.config['JWT_SECRET_KEY'], algorithm='HS256')

        response = make_response()
        response.set_cookie('auth_token', token, httponly=True, samesite='Lax')



def refresh_token(user):
    token = jwt.encode({
        'user_id': user['user_id'],
        'username': user['username'],
        'exp': datetime.now(timezone.utc) + app.config['JWT_EXPIRATION_DELTA']
    }, app.config['JWT_SECRET_KEY'], algorithm='HS256')
    return token


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        username = form.username.data
        password_candidate = form.password.data

        # Проверка данных из базы
        cur = mysql.connection.cursor()
        result = cur.execute("SELECT * FROM users WHERE username = %s", [username])

        if result > 0:
            data = cur.fetchone()
            user_id = data[0]
            password_hash = data[2]

            if bcrypt.check_password_hash(password_hash, password_candidate):
                # Генерация токена
                token = jwt.encode({
                    'user_id': user_id,
                    'username': username,
                    'exp': datetime.now(timezone.utc) + app.config['JWT_EXPIRATION_DELTA']
                }, app.config['JWT_SECRET_KEY'], algorithm='HS256')

                # Сохранение токена в куки
                response = redirect(url_for('cuenta'))
                response.set_cookie(
                    'auth_token',
                    token,
                    httponly=True,
                    samesite='Lax'  # 'Lax' для страниц одного домена
                )

                flash('Вы успешно вошли!', 'success')
                return response
            else:
                flash('Неправильный пароль', 'danger')
        else:
            flash('Пользователь не найден', 'danger')

        cur.close()
    return render_template('login.html', form=form)



def get_current_user():
    token = request.cookies.get('auth_token')
    print("Token in cookies:", token)  # Отладка
    if not token:
        print("Token not found.")
        return None

    try:
        data = jwt.decode(token, app.config['JWT_SECRET_KEY'], algorithms=['HS256'])
        print("Decoded token data:", data)  # Отладка
        return data
    except jwt.ExpiredSignatureError:
        print("Token expired.")
        return None
    except jwt.InvalidTokenError:
        print("Invalid token.")
        return None



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



@app.route('/cuenta')
def cuenta():
    user = get_current_user()
    if not user:
        flash('Вам нужно войти в систему', 'warning')
        return redirect('/login')

    username = user['username']

    # Получение результатов игр
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT u.username, MAX(r.score) AS score, MAX(r.created_at) AS created_at
        FROM game_results r
        JOIN users u ON r.user_id = u.id
        GROUP BY u.username
        ORDER BY score DESC
        LIMIT 10
    """)
    pacman_results = cur.fetchall()

    cur.execute("""
        SELECT u.username, MAX(r.score) AS score, MAX(r.created_at) AS created_at
        FROM galaga_results r
        JOIN users u ON r.user_id = u.id
        GROUP BY u.username
        ORDER BY score DESC
        LIMIT 10
    """)
    galaga_results = cur.fetchall()
    cur.close()

    return render_template(
        'cuenta.html',
        username=username,
        pacman_results=pacman_results,
        galaga_results=galaga_results
    )

# Опросник
import random

@app.route('/quiz', methods=['GET', 'POST'])
def quiz():
    user = get_current_user()
    if not user:
        flash('Вам нужно войти в систему', 'warning')
        return redirect('/login')

    username = user['username']
    cur = mysql.connection.cursor()
    cur.execute("SELECT id FROM users WHERE username = %s", [username])
    user = cur.fetchone()
    user_id = user[0]

    question = None
    correct_option = None
    selected_option = None
    question_number = 1

    # Списки GIF для правильных и неправильных ответов
    correct_gifs = [
        "https://media.giphy.com/media/111ebonMs90YLu/giphy.gif",
        "https://media.giphy.com/media/l0HlNaQ6gWfllcjDO/giphy.gif",
        "https://media.giphy.com/media/xT9IgIc0lryrxvqVGM/giphy.gif",
        "https://media.giphy.com/media/13HgwGsXF0aiGY/giphy.gif",
        "https://media.giphy.com/media/3oz8xBkRsgPTnbKQXS/giphy.gif",
        "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExbmFoanpkbGVhMGF4ampldDRxOHdpNXY1MGR6YjVncWFxY3M3bmtpdSZlcD12MV9naWZzX3NlYXJjaCZjdD1n/ZdUnQS4AXEl1AERdil/giphy.gif",
        "https://media.giphy.com/media/kBZBlLVlfECvOQAVno/giphy.gif?cid=790b7611nahjzdlea0axjjet4q8wi5v50dzb5gqaqcs7nkiu&ep=v1_gifs_search&rid=giphy.gif&ct=g",
        "https://media.giphy.com/media/xT77XWum9yH7zNkFW0/giphy.gif?cid=790b7611nahjzdlea0axjjet4q8wi5v50dzb5gqaqcs7nkiu&ep=v1_gifs_search&rid=giphy.gif&ct=g",
        "https://media.giphy.com/media/DLZDkJZfqUK0qSVB2I/giphy.gif?cid=ecf05e479ynubz3c7mzax4gkz6mnv2lry4qb6daqejhmwrhe&ep=v1_gifs_search&rid=giphy.gif&ct=g",
        "https://media.giphy.com/media/bBk9QHRrl9jia4PUtL/giphy.gif?cid=ecf05e47nqfbhod1bnnrux3jok2nu46ju5hjqherfm8rnf0k&ep=v1_gifs_search&rid=giphy.gif&ct=g",
        "https://media.giphy.com/media/ely3apij36BJhoZ234/giphy.gif?cid=790b7611ufjchoevn1w9raxlpcrjm9pvt3x2abrkckok4fv0&ep=v1_gifs_search&rid=giphy.gif&ct=g",
        "https://media.giphy.com/media/yyZRSvISN1vvW/giphy.gif?cid=790b7611ufjchoevn1w9raxlpcrjm9pvt3x2abrkckok4fv0&ep=v1_gifs_search&rid=giphy.gif&ct=g",
        "https://media.giphy.com/media/x8apGmpYGeFyM/giphy.gif?cid=790b7611ufjchoevn1w9raxlpcrjm9pvt3x2abrkckok4fv0&ep=v1_gifs_search&rid=giphy.gif&ct=g",
        "https://media.giphy.com/media/Hc8PMCBjo9BXa/giphy.gif?cid=790b7611ufjchoevn1w9raxlpcrjm9pvt3x2abrkckok4fv0&ep=v1_gifs_search&rid=giphy.gif&ct=g",
        "https://media.giphy.com/media/xWZcTvh1cuAaSi7HeI/giphy.gif?cid=ecf05e47kc6vhu3ep9z78h6pwoompva6txhmyo1dh6dyocb3&ep=v1_gifs_search&rid=giphy.gif&ct=g",
        "https://media.giphy.com/media/HzPtbOKyBoBFsK4hyc/giphy.gif?cid=ecf05e478dfjkk9jk6cf054xpwmy1oyn0jlf3unbhgchfjax&ep=v1_gifs_search&rid=giphy.gif&ct=g",
        "https://media.giphy.com/media/H75SVhmkdFHOM/giphy.gif?cid=ecf05e47xur9xdwltlkc8s0bpgdmwr278t3cfyxfj9cw2eqz&ep=v1_gifs_search&rid=giphy.gif&ct=g",
        "https://media.giphy.com/media/wijMRo7UZXSqA/giphy.gif?cid=ecf05e47hlps2229swx6b7hib987v3b18gm75w0p9prjea3i&ep=v1_gifs_search&rid=giphy.gif&ct=g",
    ]
    incorrect_gifs = [
        "https://media.giphy.com/media/14uQ3cOFteDaU/giphy.gif",
        "https://media.giphy.com/media/3oriO0OEd9QIDdllqo/giphy.gif",
        "https://media.giphy.com/media/3o7TKtnuHOHHUjR38Y/giphy.gif",
        "https://media.giphy.com/media/3oriO7A7bt1wsEP4cw/giphy.gif",
        "https://media.giphy.com/media/26AHONQ79FdWZhAI0/giphy.gif",
    ]

    # Если пользователь отправил ответ
    if request.method == 'POST':
        question_id = request.form['question_id']
        selected_option = request.form['option']

        cur.execute("SELECT correct_option FROM questions WHERE id = %s", [question_id])
        correct_option = cur.fetchone()[0]
        is_correct = (selected_option == correct_option)

        cur.execute("""
            INSERT INTO user_answers (user_id, question_id, selected_option, is_correct)
            VALUES (%s, %s, %s, %s)
        """, (user_id, question_id, selected_option, is_correct))
        mysql.connection.commit()

    cur.execute("SELECT COUNT(*) FROM user_answers WHERE user_id = %s", [user_id])
    answered_count = cur.fetchone()[0]
    question_number = answered_count + 1

    if not correct_option:
        cur.execute("""
            SELECT * FROM questions
            WHERE id NOT IN (SELECT question_id FROM user_answers WHERE user_id = %s)
            LIMIT 1
        """, [user_id])
        question = cur.fetchone()

    cur.close()
    
    if not question and not correct_option:
        return redirect(url_for('quiz_results'))

    return render_template(
        'quiz.html',
        question=question,
        correct_option=correct_option,
        selected_option=selected_option,
        question_number=question_number,
        random_correct_gif=random.choice(correct_gifs),
        random_incorrect_gif=random.choice(incorrect_gifs),
    )

@app.route('/reset_quiz', methods=['POST'])
def reset_quiz():
    user = get_current_user()
    if not user:
        flash('Necesitas iniciar sesión primero.', 'warning')
        return redirect('/login')

    username = user['username']
    cur = mysql.connection.cursor()
    cur.execute("SELECT id FROM users WHERE username = %s", [username])
    user = cur.fetchone()
    user_id = user[0]

    # Eliminar las respuestas del usuario
    cur.execute("DELETE FROM user_answers WHERE user_id = %s", [user_id])
    mysql.connection.commit()

    flash('Tus respuestas han sido reseteadas. Puedes comenzar de nuevo.', 'success')
    return redirect(url_for('quiz'))  # Redirigir al inicio del quiz

@app.route('/galaga')
def galaga():
    return send_from_directory('static/galaga', 'index.html')

@app.route('/quiz_all_results', methods=['GET', 'POST'])
def quiz_all_results():
    user = get_current_user()
    if not user:
        flash('Вам нужно войти в систему', 'warning')
        return redirect('/login')

    username = user['username']

    cur = mysql.connection.cursor()

    # Получение списка всех пользователей
    cur.execute("SELECT DISTINCT username FROM users ORDER BY username")
    users = cur.fetchall()

    selected_user = request.form.get('username')  # Получаем выбранного пользователя из формы

    # Фильтруем результаты по выбранному пользователю или показываем все
    if selected_user and selected_user != "Todos":
        cur.execute("""
            SELECT u.username, q.question, ua.selected_option, q.correct_option,
                   CASE 
                       WHEN ua.is_correct THEN 'Correcto' 
                       ELSE 'Incorrecto' 
                   END AS status,
                   q.option_a, q.option_b, q.option_c, q.option_d
            FROM user_answers ua
            JOIN users u ON ua.user_id = u.id
            JOIN questions q ON ua.question_id = q.id
            WHERE u.username = %s
            ORDER BY q.id
        """, [selected_user])
    else:
        cur.execute("""
            SELECT u.username, q.question, ua.selected_option, q.correct_option,
                   CASE 
                       WHEN ua.is_correct THEN 'Correcto' 
                       ELSE 'Incorrecto' 
                   END AS status,
                   q.option_a, q.option_b, q.option_c, q.option_d
            FROM user_answers ua
            JOIN users u ON ua.user_id = u.id
            JOIN questions q ON ua.question_id = q.id
            ORDER BY u.username, q.id
        """)

    results = cur.fetchall()
    cur.close()

    # Подготовка данных для отображения
    results_list = []
    for row in results:
        selected_option_text = row[5] if row[2] == 'A' else row[6] if row[2] == 'B' else row[7] if row[2] == 'C' else row[8]
        correct_option_text = row[5] if row[3] == 'A' else row[6] if row[3] == 'B' else row[7] if row[3] == 'C' else row[8]
        results_list.append({
            'username': row[0],
            'question': row[1],
            'selected_option': row[2],
            'selected_option_text': selected_option_text,
            'correct_option': row[3],
            'correct_option_text': correct_option_text,
            'status': row[4]
        })

    return render_template('quiz_all_results.html', results=results_list, users=users, selected_user=selected_user)


@app.route('/quiz_all_results_summary')
def quiz_all_results_summary():
    user = get_current_user()
    if not user:
        flash('Вам нужно войти в систему', 'warning')
        return redirect('/login')

    username = user['username']

    # Извлечение общего количества вопросов и правильных ответов каждого пользователя
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT u.username,
               COUNT(CASE WHEN ua.is_correct THEN 1 END) AS correct_answers,
               COUNT(*) AS total_answers,
               ROUND((COUNT(CASE WHEN ua.is_correct THEN 1 END) / COUNT(*)) * 100, 2) AS percentage
        FROM user_answers ua
        JOIN users u ON ua.user_id = u.id
        GROUP BY u.username
        ORDER BY percentage DESC
    """)
    results = cur.fetchall()
    cur.close()

    return render_template('quiz_summary.html', results=results)
from flask import Flask, send_from_directory

# Настраиваем маршрут для скачивания файла
@app.route('/download/<filename>')
def download_file(filename):
    # Указываем путь к папке, где находятся файлы
    return send_from_directory('uploads', filename, as_attachment=True)


# Страница с результатами квиза
@app.route('/quiz_results')
def quiz_results():
    user = get_current_user()
    if not user:
        flash('Вам нужно войти в систему', 'warning')
        return redirect('/login')

    username = user['username']

    # Получаем user_id из базы данных
    cur = mysql.connection.cursor()
    cur.execute("SELECT id FROM users WHERE username = %s", [username])
    user = cur.fetchone()
    user_id = user[0]

    # Получаем общее количество правильных ответов
    cur.execute("""
        SELECT COUNT(*) FROM user_answers
        WHERE user_id = %s AND is_correct = TRUE
    """, [user_id])
    correct_count = cur.fetchone()[0]

    # Получаем список неверных ответов
    cur.execute("""
        SELECT q.question, q.option_a, q.option_b, q.option_c, q.option_d, q.correct_option, ua.selected_option
        FROM user_answers ua
        JOIN questions q ON ua.question_id = q.id
        WHERE ua.user_id = %s AND ua.is_correct = FALSE
    """, [user_id])
    incorrect_answers = cur.fetchall()
    cur.close()

    return render_template('quiz_results.html', correct_count=correct_count, incorrect_answers=incorrect_answers)




@app.route('/logout')
def logout():
    session.clear()  # Очистка сессии (на случай её использования)
    response = redirect(url_for('login'))
    response.delete_cookie('auth_token')  # Удаление токена из куки
    flash('Вы вышли из системы', 'success')
    return response


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=80)
