from data import db_session
import csv
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, send_file

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

# Хранилище пользователей (здесь предполагается простота, реальное приложение должно использовать базу данных)
users = {}

# Хранилище привычек (опять же, это просто для примера)
habits = {
    "Exercise": [False] * 7,
    "Reading": [False] * 7
}


@app.route('/')
def index():
    return render_template('index.html', habits=habits)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in users and users[username] == password:
            return redirect(url_for('profile'))
        else:
            return render_template('login.html', error=True)
    return render_template('login.html', error=False)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username not in users:
            users[username] = password
            return redirect(url_for('login'))
        else:
            return render_template('register.html', error=True)
    return render_template('register.html', error=False)


@app.route('/profile')
def profile():
    return render_template('profile.html')


@app.route('/start_new_week')
def start_new_week():
    global habits
    habits = {habit: [False] * 7 for habit in habits}
    return redirect(url_for('index'))


@app.route('/download_table')
def download_table():
    filename = f"habit_tracker_{datetime.now().strftime('%Y-%m-%d')}.csv"
    with open(filename, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Привычка", "Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"])
        for habit, progress in habits.items():
            writer.writerow([habit] + progress)
    return send_file(filename, as_attachment=True)


@app.route('/add_habit', methods=['POST'])
def add_new_habit():
    habit_name = request.form['habit_name']
    habits[habit_name] = [False] * 7
    return redirect(url_for('index'))


def main():
    db_session.global_init("db/habit_tracker.db")
    app.run(debug=True, port=8080, host='127.0.0.1')


if __name__ == '__main__':
    main()