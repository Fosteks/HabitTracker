from data import db_session
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, send_file
from data.users import User
from data.habits import Habit
from data.list_habits import ListHabit
from data.new_week_habits import NewWeekHabit
from forms.user import RegisterForm, LoginForm, AddHabitForm
from flask_login import LoginManager, login_user, current_user, logout_user, login_required
from flask_login.mixins import AnonymousUserMixin
import random
from docx import Document

app = Flask(__name__)
app.config['SECRET_KEY'] = 'habit_tracker_secret_key'

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


@app.route('/')
@app.route('/<group>', methods=['POST', 'GET'])
def index(group='Все привычки'):
    if request.method == 'GET':
        label = 'Зарегистрироваться'
        if current_user.is_authenticated:
            label = 'Профиль'
            habits = get_user_habits(current_user.id, 0)
        else:
            habits = []
        with open('data/advice', encoding='UTF-8') as f:
            lines = f.readlines()
            advice = random.choice(lines)
        if current_user.is_authenticated:
            db_sess = db_session.create_session()
            groups = db_sess.query(Habit.group).filter(Habit.user_id == current_user.id).all() + [('Все привычки',)]
            grps = [group]
            for gr in groups:
                if gr[0] not in grps and gr[0] and gr[0] != 'None':
                    grps.append(gr[0])
        else:
            grps = ['Все привычки']
        return render_template('index.html', habits=habits, label=label, advice=advice, groups=grps)
    elif request.method == 'POST':
        db_sess = db_session.create_session()
        for habit in db_sess.query(Habit).filter(Habit.user_id == current_user.id):
            if not habit.habit:
                id = habit.id
                hab = request.form.get(str(id))
                if hab:
                    habit.habit = hab
            if habit.group == group or group == 'Все привычки':
                if request.form.get(str(habit.id) + 'day1') == 'on':
                    habit.day1 = True
                else:
                    habit.day1 = False
                if request.form.get(str(habit.id) + 'day2') == 'on':
                    habit.day2 = True
                else:
                    habit.day2 = False
                if request.form.get(str(habit.id) + 'day3') == 'on':
                    habit.day3 = True
                else:
                    habit.day3 = False
                if request.form.get(str(habit.id) + 'day4') == 'on':
                    habit.day4 = True
                else:
                    habit.day4 = False
                if request.form.get(str(habit.id) + 'day5') == 'on':
                    habit.day5 = True
                else:
                    habit.day5 = False
                if request.form.get(str(habit.id) + 'day6') == 'on':
                    habit.day6 = True
                else:
                    habit.day6 = False
                if request.form.get(str(habit.id) + 'day7') == 'on':
                    habit.day7 = True
                else:
                    habit.day7 = False
        db_sess.commit()
        return redirect(f'/{group.strip()}')


@app.route('/add_habit')
@login_required
def add_new_habit():
    db_sess = db_session.create_session()
    groups = db_sess.query(ListHabit).all()
    groups = list(set([i.group for i in groups]))
    i = groups.index('Все привычки')
    groups.pop(i)
    habits = db_sess.query(ListHabit).all()
    return render_template('add_habit.html', groups=groups, group_habits=habits)


@app.route('/habit_add', methods=['POST'])
@login_required
def habit_add():
    db_sess = db_session.create_session()
    habit = request.form.get('dropdown_habit')
    new_habit = Habit()
    new_habit.habit = habit
    new_habit.user_id = current_user.id
    new_habit.group = request.form.get('dropdown_group')
    db_sess.add(new_habit)
    db_sess.commit()
    return redirect('/')


@app.route('/habit_group', methods=['POST'])
@login_required
def habit_group():
    db_sess = db_session.create_session()
    group = request.form.get('dropdown_group')
    gr_habits = db_sess.query(ListHabit).filter(ListHabit.group == group).all()
    groups = db_sess.query(ListHabit.group).all()
    groups_res = [group]
    for i in list(sorted(set(groups))):
        if i != group and i not in groups_res:
            groups_res.append(i[0])
    i = groups_res.index('Все привычки')
    groups_res.pop(i)
    return render_template('add_habit.html', groups=groups_res, group_habits=gr_habits)


@app.route('/group_of_habits', methods=['POST'])
@login_required
def group_of_habits():
    if current_user.is_authenticated:
        group = request.form.get('chosen_group')
        return redirect(f'/{group.strip()}')


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
        user = User(name=form.name.data, )
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
    with open('data/info', encoding='UTF-8') as f:
        check = f.read()
    n = current_user.ended_habits
    if n is None:
        n = 0
    return render_template('profile.html', created_date=created_date, n=n, check=check, user=current_user)


@app.route('/is_adding_to_new_week', methods=['POST'])
@login_required
def is_adding_to_new_week():
    with open('data/info', 'w', encoding='UTF-8') as f:
        if request.form.get('adding') == 'on':
            check = 'True'
        else:
            check = 'False'
        f.write(check)
    return redirect('/profile')


@app.route('/create_new_week')
@login_required
def create_new_week():
    db_sess = db_session.create_session()
    delete_habits = db_sess.query(Habit).filter(Habit.user_id == current_user.id).all()
    nw_habits = db_sess.query(NewWeekHabit).filter(NewWeekHabit.user_id == current_user.id).all()
    new_habits = []
    for habit in delete_habits:
        new_habits.append([habit.habit, habit.user_id, habit.group])
        db_sess.delete(habit)
    for habit in nw_habits:
        new_habits.append([habit.nw_habit, habit.user_id, habit.group])
        db_sess.delete(habit)
    for habit in new_habits:
        hbt = Habit()
        hbt.habit = habit[0]
        hbt.user_id = habit[1]
        hbt.group = habit[2]
        db_sess.add(hbt)
    db_sess.commit()
    return redirect('/')


@app.route('/rename_habit/<habit_id>')
def rename_habit(habit_id):
    db_sess = db_session.create_session()
    habit = db_sess.query(Habit).filter(Habit.id == habit_id).first()
    habit.habit = ''
    db_sess.commit()
    return redirect('/')


@app.route('/delete_habit/<habit_id>')
def delete_habit(habit_id):
    db_sess = db_session.create_session()
    habit = db_sess.query(Habit).filter(Habit.id == habit_id).first()
    db_sess.delete(habit)
    db_sess.commit()
    return redirect('/')


@app.route('/end_habit/<habit_id>')
def end_habit(habit_id):
    db_sess = db_session.create_session()
    end_habit = db_sess.query(Habit).filter(Habit.id == habit_id).first()
    with open('data/info', encoding='UTF-8') as f:
        check = f.read()
    if check == 'True':
        nw_habit = NewWeekHabit()
        nw_habit.user_id = end_habit.user_id
        nw_habit.nw_habit = end_habit.habit
        nw_habit.group = end_habit.group
        db_sess.add(nw_habit)
    db_sess.delete(end_habit)
    user = db_sess.query(User).filter(User.id == current_user.id).first()
    if user.ended_habits is None:
        user.ended_habits = 1
    else:
        user.ended_habits = user.ended_habits + 1
    db_sess.commit()
    return redirect('/')


@app.route('/habit_choose/<group>', methods=['POST'])
@login_required
def habit_choose(group):
    db_sess = db_session.create_session()
    habit = Habit()
    habit.group = group
    habit.habit = request.form.get('dropdown_habit')
    habit.user_id = current_user.id
    db_sess.add(habit)
    db_sess.commit()
    return redirect('/')


@app.route('/new_habit_add/<group>', methods=['POST'])
@login_required
def new_habit_add(group):
    db_sess = db_session.create_session()
    habit = Habit()
    habit.group = group
    habit.habit = request.form.get('new_habit')
    habit.user_id = current_user.id
    db_sess.add(habit)
    db_sess.commit()
    return redirect('/')


@app.route('/download_table')
def download_table():
    filename = f"habit_tracker_{datetime.now().strftime('%Y-%m-%d')}.docx"
    doc = Document()
    habits = get_user_habits(current_user.id, 0)
    table = doc.add_table(rows=len(habits) + 1, cols=8)
    table.style = 'Table Grid'
    row = table.rows[0]
    row.cells[0].text = 'Привычки'
    header = {1: 'Понедельник', 2: 'Вторник', 3: 'Среда', 4: 'Четверг', 5: 'Пятница', 6: 'Суббота', 7: 'Воскресенье'}
    for i in range(1, 8):
        row.cells[i].text = header[i]
    for i in range(1, len(habits) + 1):
        row = table.rows[i]
        row.cells[0].text = habits[i - 1].habit
        for k in range(1, 8):
            row.cells[k].text = '[ ]'
    doc.save(filename)
    return send_file(filename)


def main():
    db_session.global_init("db/habit_tracker.db")
    app.run(debug=True, port=8080, host='127.0.0.1')


if __name__ == '__main__':
    main()
