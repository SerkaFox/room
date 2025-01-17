from flask import render_template, request, redirect, url_for, flash, make_response, session, jsonify
from app import app, mysql, bcrypt
from wtforms import Form, StringField, PasswordField, validators
import jwt
from datetime import datetime, timezone

# Форма регистрации
class RegistrationForm(Form):
    username = StringField('Username', [validators.Length(min=4, max=50), validators.DataRequired()])
    email = StringField('Email', [validators.Length(min=6, max=100), validators.Email(), validators.DataRequired()])
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
    form = LoginForm(request.form)  # Создаем форму
    if user:  # Если пользователь авторизован
        return redirect(url_for('cuenta'))
    return render_template('index.html', form=form)  # Передаем форму в шаблон

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        username = form.username.data
        password_candidate = form.password.data

        cur = mysql.connection.cursor()
        result = cur.execute("SELECT * FROM users WHERE username = %s", [username])

        # Если пользователь найден в базе
        if result > 0:
            data = cur.fetchone()
            user_id = data[0]
            password_hash = data[2]  # Извлекаем хеш пароля из базы данных

            # Сравниваем введенный пароль с хешем в базе данных
            if bcrypt.check_password_hash(password_hash, password_candidate):
                # Генерация токена
                token = jwt.encode({
                    'user_id': user_id,
                    'username': username,
                    'exp': datetime.now(timezone.utc) + app.config['JWT_EXPIRATION_DELTA']
                }, app.config['JWT_SECRET_KEY'], algorithm='HS256')

                # Сохранение токена в куки
                response = redirect(url_for('cuenta'))
                response.set_cookie('auth_token', token, httponly=True, samesite='Lax')

                flash('¡Has iniciado sesión exitosamente!', 'success')
                return response
            else:
                flash('Contraseña incorrecta, por favor intentalo de nuevo.', 'danger')
        else:
            flash('Usuario no encontrado.', 'danger')

        cur.close()

    return render_template('index.html', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm(request.form)
    if request.method == 'POST' and form.validate():
        username = form.username.data
        email = form.email.data
        password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')

        # Проверяем, существует ли уже пользователь с таким именем или email
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE username = %s OR email = %s", (username, email))
        existing_user = cur.fetchone()

        if existing_user:
            flash('El nombre de usuario o correo electrónico ya está registrado.', 'danger')
        else:
            # Сохраняем нового пользователя в базу данных
            cur.execute("INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s)", (username, email, password))
            mysql.connection.commit()
            flash('¡Te has registrado exitosamente!', 'success')
            return redirect(url_for('login'))

        cur.close()

    return render_template('index.html', form=form)


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

    return render_template('index.html')

@app.route('/cuenta')
def cuenta():
    user = get_current_user()
    if not user:
        flash('Вам нужно войти в систему', 'warning')
        return redirect('/login')

    username = user['username']

    # Получение результатов Pacman
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT u.username, MAX(r.score) AS score, MAX(r.created_at) AS created_at, u.estrellas
        FROM game_results r
        JOIN users u ON r.user_id = u.id
        GROUP BY u.username, u.estrellas
        ORDER BY score DESC
        LIMIT 10
    """)
    pacman_results = cur.fetchall()

    # Получение результатов Galaga
    cur.execute("""
        SELECT u.username, MAX(r.score) AS score, MAX(r.created_at) AS created_at, u.estrellas
        FROM galaga_results r
        JOIN users u ON r.user_id = u.id
        GROUP BY u.username, u.estrellas
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


def refresh_token(user):
    token = jwt.encode({
        'user_id': user['user_id'],
        'username': user['username'],
        'exp': datetime.now(timezone.utc) + app.config['JWT_EXPIRATION_DELTA']
    }, app.config['JWT_SECRET_KEY'], algorithm='HS256')
    return token



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
        
@app.route('/logout')
def logout():
    session.clear()  # Очистка сессии
    response = redirect(url_for('login'))  # Переадресация на страницу логина
    response.delete_cookie('auth_token')  # Удаление токена из куки
    flash('Вы вышли из системы', 'success')
    return response

