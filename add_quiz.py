import re
from flask import Flask
from flask_mysqldb import MySQL
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Flask и MySQL настройки
app = Flask(__name__)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'alumno'
app.config['MYSQL_PASSWORD'] = 'alumno'
app.config['MYSQL_DB'] = 'flask_auth'

mysql = MySQL(app)

def parse_txt_file(file_path):
    """
    Чтение TXT-файла и извлечение вопросов, вариантов ответов и правильных ответов.
    """
    questions = []

    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    # Разделение по вопросам, учитывая возможные различия в разделителях
    raw_questions = re.split(r'\n\s*\d+\.\s', content)

    for idx, raw_question in enumerate(raw_questions):
        if not raw_question.strip():
            continue
        lines = raw_question.strip().split('\n')
        if len(lines) >= 6:
            question_text = lines[0].strip()
            option_a = lines[1][2:].strip()
            option_b = lines[2][2:].strip()
            option_c = lines[3][2:].strip()
            option_d = lines[4][2:].strip()
            correct_option = lines[5].split(':')[1].strip()

            questions.append({
                "question": question_text,
                "options": [option_a, option_b, option_c, option_d],
                "correct_option": correct_option
            })
            logging.info(f"Добавлен вопрос: {question_text}")
        else:
            logging.warning(f"Вопрос {idx + 1} не распознан: {raw_question}")

    return questions


def insert_questions_into_db(questions):
    """
    Очистка таблицы и вставка новых вопросов в базу данных.
    """
    with app.app_context():
        cur = mysql.connection.cursor()

        try:
            # Очистка таблиц
            cur.execute("DELETE FROM user_answers")
            cur.execute("DELETE FROM questions")
            mysql.connection.commit()
            logging.info("Таблицы 'questions' и 'user_answers' очищены.")
        except Exception as e:
            logging.error(f"Ошибка при очистке таблиц: {e}")
            return

        for idx, question in enumerate(questions, start=1):
            try:
                options = question['options']
                cur.execute("""
                    INSERT INTO questions (question, option_a, option_b, option_c, option_d, correct_option)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (
                    question['question'],
                    options[0],
                    options[1],
                    options[2],
                    options[3],
                    question['correct_option']
                ))
                mysql.connection.commit()
                logging.info(f"Вопрос {idx} добавлен в базу данных: {question['question']}")
            except Exception as e:
                logging.error(f"Ошибка при добавлении вопроса {idx}: {e}")
                continue

        cur.close()
        logging.info("Все изменения сохранены в базе данных.")

if __name__ == '__main__':
    # Укажите путь к вашему TXT-файлу
    file_path = 'QUIZ.txt'

    try:
        # Извлечение вопросов из файла
        questions = parse_txt_file(file_path)
        logging.info(f"Извлечено {len(questions)} вопросов из файла.")

        # Вставка вопросов в базу данных
        if questions:
            insert_questions_into_db(questions)
            logging.info("Все вопросы успешно добавлены в базу данных!")
        else:
            logging.warning("Нет вопросов для добавления в базу данных.")
    except Exception as e:
        logging.error(f"Общая ошибка: {e}")
