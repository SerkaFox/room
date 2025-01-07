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

import re
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


import re
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def parse_txt_file(file_path):
    """
    Чтение TXT-файла и извлечение вопросов, вариантов ответов и правильных ответов.
    """
    questions = []

    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    # Разделение на вопросы. Вопросы начинаются с цифры и точки, варианты ответов с букв (A, B, C, D)
    raw_questions = re.split(r'\d+\.\s', content)

    logging.info(f"Raw questions (total {len(raw_questions)}): {raw_questions[:5]}")  # Логирование первых 5 вопросов для проверки

    for idx, raw_question in enumerate(raw_questions):
        if not raw_question.strip():
            continue
        
        # Разделение вопроса и ответов
        lines = raw_question.strip().split('\n')

        logging.info(f"Вопрос {idx + 1}: {lines}")  # Логируем все строки вопроса для отладки

        # Найдем строки, где начинаются варианты ответов (A), B), C), D))
        answer_lines = [line for line in lines if re.match(r'[A-D]\)', line.strip())]

        if not answer_lines:
            logging.warning(f"Вопрос {idx + 1} не содержит вариантов ответов. Пропускаем.")
            continue
        
        # Вопрос состоит из всех строк до вариантов
        question_text = "\n".join(lines[:lines.index(answer_lines[0])]).strip()

        # Все ответы находятся после строки с вопросом
        options = [line[3:].strip() for line in answer_lines]

        logging.info(f"Вопрос: {question_text}")  # Логируем сам вопрос

        if len(options) < 4:
            logging.warning(f"Вопрос {idx + 1} не содержит всех вариантов ответов. Пропускаем.")
            continue

        # Извлекаем правильный ответ с учетом "Correcta: "
        correct_answer_line = next((line for line in lines if line.strip().startswith("Correcta:")), None)
        if correct_answer_line:
            correct_option = correct_answer_line.split(":")[1].strip()
        else:
            logging.warning(f"Вопрос {idx + 1} не содержит правильного ответа. Пропускаем.")
            continue

        # Логируем все варианты ответов и правильный ответ
        for i, option in enumerate(options, start=1):
            logging.info(f"Вариант {chr(64 + i)}): {option}")
        logging.info(f"Правильный ответ: {correct_option}")

        questions.append({
            "question": question_text,
            "options": options,
            "correct_option": correct_option
        })

    return questions



def insert_question_into_db(question, idx):
    """
    Вставка одного вопроса в базу данных.
    """
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
            if not insert_question_into_db(question, idx):
                logging.warning(f"Не удалось добавить вопрос {idx}. Пропускаем его.")
                continue

        logging.info("Все изменения сохранены в базе данных.")

if __name__ == '__main__':
    # Укажите путь к вашему TXT-файлу
    file_path = 'QUIZ10.txt'

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
