from data import db_session
import csv
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, send_file
from data.users import User
from data.habits import Habit
from forms.user import RegisterForm, LoginForm, AddHabitForm
from flask_login import LoginManager, login_user, current_user, logout_user, login_required
from flask_login.mixins import AnonymousUserMixin
import time

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


def get_user_habits(user_id, arg=1):
    db_sess = db_session.create_session()
    habits = db_sess.query(Habit).filter(Habit.user_id == user_id).all()
    db_sess.close()
    if arg:
        res = []
        for habit in habits:
            res.append(habit.habit)
        return res
    return db_sess.query(User).filter(User.id == user_id).first().habits


@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'GET':
        label = 'Зарегистрироваться'
        if current_user.is_authenticated:
            label = 'Профиль'
            habits = get_user_habits(current_user.id, 0)
        else:
            habits = []
        return render_template('index.html', habits=habits, label=label)
    elif request.method == 'POST':
        db_sess = db_session.create_session()
        for habit in db_sess.query(Habit).filter(Habit.user_id == current_user.id):
            if not habit.habit:
                id = habit.id
                hab = request.form.get(str(id))
                if hab:
                    print(request.form.get(str(id) + str(1)))
                    habit.habit = hab
        db_sess.commit()
        return redirect('/')


@app.route('/add_habit')
def add_new_habit():
    db_sess = db_session.create_session()
    habit = Habit()
    habit.user_id = current_user.id
    db_sess.add(habit)
    db_sess.commit()
    db_sess.close()
    return redirect('/')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.name == form.name.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.name == form.name.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(name=form.name.data,)
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/profile')
def profile():
    if isinstance(current_user, AnonymousUserMixin):
        return redirect('/register')
    created_date = str(current_user.created_date).split()[0]
    return render_template('profile.html', created_date=created_date, login=current_user.name)


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


def main():
    db_session.global_init("db/habit_tracker.db")
    app.run(debug=True, port=8080, host='127.0.0.1')


if __name__ == '__main__':
    main()