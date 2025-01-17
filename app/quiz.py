from flask import render_template, request, jsonify, redirect, url_for, flash, session
from app import app, mysql
import random
from app.auth import get_current_user


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
    result = None  # Переменная для хранения результата

    # Проверка на наличие вопроса в сессии
    if 'question_id' in session:
        # Вопрос уже был выбран ранее, извлекаем его из сессии
        question_id = session['question_id']
        cur.execute("SELECT * FROM questions WHERE id = %s", [question_id])
        question = cur.fetchone()
    else:
        # Если вопрос не был сохранен, выбираем новый случайный вопрос
        cur.execute("""
            SELECT * FROM questions
            WHERE id NOT IN (SELECT question_id FROM user_answers WHERE user_id = %s)
            ORDER BY RAND()
            LIMIT 1
        """, [user_id])
        question = cur.fetchone()
        # Сохраняем выбранный вопрос в сессии
        if question:
            session['question_id'] = question[0]

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

        # Сохраняем в переменную результат
        result = {
            'is_correct': is_correct,
            'selected_option': selected_option,
            'correct_option': correct_option
        }

        # Сохраняем ответ пользователя
        cur.execute("""
            INSERT INTO user_answers (user_id, question_id, selected_option, is_correct)
            VALUES (%s, %s, %s, %s)
        """, (user_id, question_id, selected_option, is_correct))
        mysql.connection.commit()

        # Очистить вопрос в сессии после отправки ответа
        session.pop('question_id', None)

    cur.execute("SELECT COUNT(*) FROM user_answers WHERE user_id = %s", [user_id])
    answered_count = cur.fetchone()[0]
    question_number = answered_count + 1

    cur.close()

    if not question and not result:
        session.clear()
        return redirect(url_for('quiz_results'))

    return render_template(
        'quiz.html',
        question=question,
        result=result,  # Передаем результат в шаблон
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

    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT u.username,
               COUNT(CASE WHEN ua.is_correct THEN 1 END) AS correct_answers,
               COUNT(*) AS total_answers,
               (SELECT COUNT(*) FROM questions) AS total_questions,
               ROUND((COUNT(CASE WHEN ua.is_correct THEN 1 END) / (SELECT COUNT(*) FROM questions)) * 100, 2) AS percentage,
               u.last_star_threshold
        FROM user_answers ua
        JOIN users u ON ua.user_id = u.id
        GROUP BY u.username
        ORDER BY percentage DESC
    """)
    results = cur.fetchall()
    cur.close()

    # Определяем пользователей, которые достигли новых порогов
    thresholds = [80, 90, 100]
    users_with_new_stars = []

    for row in results:
        username = row[0]
        percentage = row[4]
        last_threshold = row[5]

        for threshold in thresholds:
            if percentage >= threshold > last_threshold:
                users_with_new_stars.append({"username": username, "threshold": threshold})
                break

    return render_template(
        'quiz_summary.html',
        results=results,
        users_with_new_stars=users_with_new_stars
    )


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


@app.route('/quiz_results_combined', methods=['GET', 'POST'])
def quiz_results_combined():
    user = get_current_user()
    if not user:
        flash('Вам нужно войти в систему', 'warning')
        return redirect('/login')

    username = user['username']
    cur = mysql.connection.cursor()

    # 1. Получаем личные результаты
    cur.execute("SELECT id FROM users WHERE username = %s", [username])
    user_row = cur.fetchone()
    user_id = user_row[0]

    cur.execute("""
        SELECT COUNT(*) FROM user_answers
        WHERE user_id = %s AND is_correct = TRUE
    """, [user_id])
    correct_count = cur.fetchone()[0]

    cur.execute("""
        SELECT q.question, q.option_a, q.option_b, q.option_c, q.option_d, q.correct_option, ua.selected_option
        FROM user_answers ua
        JOIN questions q ON ua.question_id = q.id
        WHERE ua.user_id = %s AND ua.is_correct = FALSE
    """, [user_id])
    incorrect_answers = cur.fetchall()

    # 2. Получаем резюме
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
    summary_results = cur.fetchall()

    # 3. Получаем общие результаты с фильтрацией
    cur.execute("SELECT DISTINCT username FROM users ORDER BY username")
    users = cur.fetchall()

    selected_user = request.args.get('username', 'Todos')  # Получаем фильтр из строки запроса

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

    general_results = cur.fetchall()
    cur.close()

    # Формируем данные для шаблона
    return render_template(
        'results.html',
        username=username,
        correct_count=correct_count,
        incorrect_answers=incorrect_answers,
        summary_results=summary_results,
        general_results=general_results,
        users=users,
        selected_user=selected_user
    )
