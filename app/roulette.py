from flask import render_template, jsonify, request
from app import app
import random

# Список имен
NAMES = ["Juan Manuel", "Brayan Orlando", "Adriana Nicolle", "Santiago", "Orlando", "Consuelo", "Laila", "Jenifer Alexand", "Sergei", "Grethy Nelva", "Marwane"]
current_names = NAMES.copy()

@app.route('/roulette')
def roulette():
    return render_template('roulette.html')

@app.route('/roulette/spin', methods=['POST'])
def spin():
    global current_names
    if not current_names:
        return jsonify({"error": "No names left to choose from!"})

    selected_name = random.choice(current_names)
    current_names.remove(selected_name)
    return jsonify({"name": selected_name, "remaining": current_names})

@app.route('/roulette/reset', methods=['POST'])
def reset():
    global current_names
    current_names = NAMES.copy()
    return jsonify({"message": "List reset successfully!", "names": current_names})
