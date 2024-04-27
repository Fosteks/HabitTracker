from data import db_session
import csv
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, send_file
from data.users import User
from data.habits import Habit
from data.list_habits import ListHabit
from forms.user import RegisterForm, LoginForm, AddHabitForm
from flask_login import LoginManager, login_user, current_user, logout_user, login_required
from flask_login.mixins import AnonymousUserMixin
import time
import random


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
        with open('data/advice') as f:
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
                    print(request.form.get(str(habit.id) + 'day1'))
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
        return redirect(f'/{group}')


@app.route('/add_habit')
def add_new_habit():
    db_sess = db_session.create_session()
    groups = db_sess.query(ListHabit).all()
    groups = list(set([i.group for i in groups]))
    i = groups.index('Все привычки')
    groups.pop(i)
    habits = db_sess.query(ListHabit).all()
    return render_template('add_habit.html', groups=groups, group_habits=habits)


@app.route('/habit_add', methods=['POST'])
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
def habit_group():
    db_sess = db_session.create_session()
    group = request.form.get('dropdown_group')
    gr_habits = db_sess.query(ListHabit).filter(ListHabit.group == group).all()
    groups = db_sess.query(ListHabit.group).all()
    groups_res = [group]
    for i in list(sorted(set(groups))):
        if i != group:
            groups_res.append(i[0])
    i = groups_res.index('Все привычки')
    groups.pop(i)
    return render_template('add_habit.html', groups=groups_res, group_habits=gr_habits)


@app.route('/group_of_habits', methods=['POST'])
def group_of_habits():
    if current_user.is_authenticated:
        group = request.form.get('chosen_group')
        return redirect(f'/{group}')


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
    with open('data/info') as f:
        lines = f.readlines()
        n = lines[-2]
        check = lines[-1]
    return render_template('profile.html', created_date=created_date, n=n, check=check, user=current_user)


@app.route('/is_adding_to_new_week', methods=['POST'])
def is_adding_to_new_week():
    with open('data/info') as f:
        lines = f.readlines()
    with open('data/info', 'w') as f:
        f.writelines(lines[:-1])
        if request.form.get('adding') == 'on':
            f.write('True')
        else:
            f.write('False')
    return redirect('/profile')


@app.route('/start_new_week')
def start_new_week():
    global habits
    habits = {habit: [False] * 7 for habit in habits}
    return redirect(url_for('index'))


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


@app.route('/habit_choose/<group>', methods=['POST'])
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
    # Create a new Word document.
    doc = aw.Document()

    # Create document builder.
    builder = aw.DocumentBuilder(doc)

    # Start the table.
    table = builder.start_table()

    # Insert cell.
    builder.insert_cell()

    # Table wide formatting must be applied after at least one row is present in the table.
    table.left_indent = 20.0

    # Set height and define the height rule for the header row.
    builder.row_format.height = 40.0
    builder.row_format.height_rule = aw.HeightRule.AT_LEAST

    # Set alignment and font settings.
    builder.paragraph_format.alignment = aw.ParagraphAlignment.CENTER
    builder.font.size = 16
    builder.font.name = "Arial"
    builder.font.bold = True

    builder.cell_format.width = 100.0
    builder.write("Header Row,\n Cell 1")

    # We don't need to specify this cell's width because it's inherited from the previous cell.
    builder.insert_cell()
    builder.write("Header Row,\n Cell 2")

    builder.insert_cell()
    builder.cell_format.width = 200.0
    builder.write("Header Row,\n Cell 3")
    builder.end_row()

    builder.cell_format.width = 100.0
    builder.cell_format.vertical_alignment = aw.tables.CellVerticalAlignment.CENTER

    # Reset height and define a different height rule for table body.
    builder.row_format.height = 30.0
    builder.row_format.height_rule = aw.HeightRule.AUTO
    builder.insert_cell()

    # Reset font formatting.
    builder.font.size = 12
    builder.font.bold = False

    builder.write("Row 1, Cell 1 Content")
    builder.insert_cell()
    builder.write("Row 1, Cell 2 Content")

    builder.insert_cell()
    builder.cell_format.width = 200.0
    builder.write("Row 1, Cell 3 Content")
    builder.end_row()

    builder.insert_cell()
    builder.cell_format.width = 100.0
    builder.write("Row 2, Cell 1 Content")

    builder.insert_cell()
    builder.write("Row 2, Cell 2 Content")

    builder.insert_cell()
    builder.cell_format.width = 200.0
    builder.write("Row 2, Cell 3 Content.")
    builder.end_row()

    # End table.
    builder.end_table()

    # Save the document.
    doc.save("table_formatted.docx")
    return send_file(filename, as_attachment=True)


def main():
    db_session.global_init("db/habit_tracker.db")
    app.run(debug=True, port=8080, host='127.0.0.1')


if __name__ == '__main__':
    main()