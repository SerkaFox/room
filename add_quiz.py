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

    raw_questions = re.split(r'\d+\.\s', content)

    for idx, raw_question in enumerate(raw_questions):
        if not raw_question.strip():
            continue

        lines = raw_question.strip().split('\n')
        answer_lines = [line for line in lines if re.match(r'[A-D]\)', line.strip())]

        if not answer_lines:
            continue

        question_text = "\n".join(lines[:lines.index(answer_lines[0])]).strip()
        options = [line[3:].strip() for line in answer_lines]

        if len(options) < 4:
            continue

        correct_answer_line = next((line for line in lines if line.strip().startswith("Correcta:")), None)
        if correct_answer_line:
            correct_option = correct_answer_line.split(":")[1].strip()
        else:
            continue

        questions.append({
            "question": question_text,
            "options": options,
            "correct_option": correct_option
        })

    return questions

def question_exists(question_text):
    """
    Проверяет, существует ли вопрос в базе данных.
    """
    with app.app_context():
        cur = mysql.connection.cursor()
        cur.execute("SELECT COUNT(*) FROM questions WHERE question = %s", [question_text])
        result = cur.fetchone()[0]
        cur.close()
        return result > 0

def insert_question_into_db(question, idx):
    """
    Вставка одного вопроса в базу данных, если он еще не существует.
    """
    if question_exists(question['question']):
        logging.info(f"Вопрос {idx} уже существует в базе данных, пропускаем.")
        return False

    with app.app_context():
        cur = mysql.connection.cursor()
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
            logging.info(f"Вопрос {idx} успешно добавлен в базу данных: {question['question']}")
            return True
        except Exception as e:
            logging.error(f"Ошибка при добавлении вопроса {idx}: {e}")
            return False
        finally:
            cur.close()

def insert_questions_into_db(questions):
    """
    Вставка новых вопросов в базу данных без удаления старых.
    """
    for idx, question in enumerate(questions, start=1):
        if not insert_question_into_db(question, idx):
            continue

    logging.info("Все новые вопросы успешно добавлены в базу данных.")

if __name__ == '__main__':
    file_path = 'QUIZ10.txt'

    try:
        questions = parse_txt_file(file_path)
        logging.info(f"Извлечено {len(questions)} вопросов из файла.")

        if questions:
            insert_questions_into_db(questions)
            logging.info("Добавление вопросов завершено.")
        else:
            logging.warning("Нет вопросов для добавления в базу данных.")
    except Exception as e:
        logging.error(f"Общая ошибка: {e}")
