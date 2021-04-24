from flask import Flask, render_template, redirect, request, url_for, make_response, session
from flask_login import LoginManager, login_user
from datetime import timedelta
from data import db_session
from data.loginform import LoginForm
from data.registrateionform import RegistrateForm
from data.users import User
from data.tasks import Task
from data.task_kinds import Task_Kinds
from pickle import loads, dumps
from random import shuffle, randint
from werkzeug.security import generate_password_hash, check_password_hash

HOME = 'Домой'
CREATE = 'Создать'
DONE = 'Сдать!'
AGREED = 'Ясно'
HERE = "сюда!"

app = Flask(__name__)

login_manager = LoginManager()
login_manager.init_app(app)

with open('config/key.txt', 'r') as key:
    app.config['SECRET_KEY'] = key.readline()

@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)

@app.route('/')
@app.route('/index',  methods=['POST', 'GET'])
def index():
    visits_count = session.get('visits_count', 0)
    session['visits_count'] = visits_count + 1
    kwargs = {}
    with open("config/open pass.txt") as f:
        kwargs['open_email'] = 'mailto:' + f.readline()
    kwargs['after1'] = "Если Вы хотите создать задания или предложить какие-либо улучшения сайта"
    kwargs['after2'] = "Почта админа"
    if visits_count == 1:
        kwargs['first_frase'] = "Приветствуем"
        kwargs['about1'] = "Этот сайт существует для создания и решений тестов"
        kwargs['about2'] = "Если Вы хотите пройти один из тестов, то кликните"
    else:
        kwargs['first_frase'] = "Получается?"
        kwargs['about1'] = "Если продолжать усердствовать, старания окупаются"
        kwargs['about2'] = "Хотите пройти тест? Кликните"
    if request.method == 'GET':
        print(0)
        return render_template('index.html', title='home', **kwargs)
    elif request.method == 'POST':
        print(1)
        if request.form['submit_button'] == HOME:
            return redirect(url_for("index"))
        if request.form['submit_button'] == HERE:
            return redirect(url_for("testBuild"))

@app.route('/base', methods=['POST', 'GET'])
def base():
    if request.method == 'POST':
       if request.form['submit_button'] == HOME:
           return redirect(url_for("index"))
    elif request.method == 'GET':
        return render_template('base.html', title='base')

@app.route('/register',  methods=['POST', 'GET'])
def register():
    return render_template('register.html', title='Регистрация')

@app.route('/testBuild',  methods=['POST', 'GET'])
def testBuild():
    joj = {}
    db_sess = db_session.create_session()
    for i in db_sess.query(Task_Kinds).all():
        joj[i.name] = list(map(lambda x: (x, db_sess.query(Task).filter(Task.type == x).count()), loads(i.type)))

    if request.method == 'POST':
        if request.form['submit_button'] == HOME:
            return redirect(url_for("index"))
        if request.form['submit_button'] == CREATE:
            ojo = {}
            fase='test'
            f = False
            for kind in joj.keys():
                for s in joj[kind]:
                    ojo[s[0]] = request.form[s[0]]
                    if request.form[s[0]] != '0':
                        f = True
            if f:
                return redirect(url_for("test", ojo=ojo, fase=fase))
        return render_template('testBuild.html', title='Составить тест',
                                TaskTypes=joj, create=CREATE)
    elif request.method == 'GET':
        return render_template('testBuild.html', title='Составить тест',
                           TaskTypes=joj, create=CREATE)

@app.route('/test/<ojo>/<fase>', methods=['POST', 'GET'])
def test(ojo, fase):
    tasks = []
    ojo = eval(ojo)
    for task_type in ojo:
        ojo[task_type] = int(ojo[task_type])
        if ojo[task_type]:
            task_of_type = []
            db_sess = db_session.create_session()
            for task in db_sess.query(Task).filter(Task.type == task_type):
                task_of_type.append(task)
            task_of_type = task_of_type[:int(ojo[task_type])]
            shuffle(task_of_type)
            tasks.extend(task_of_type)
    if request.method == 'GET':
        return render_template('test.html', title='Тест', done=DONE,
                        enumerate_tasks=enumerate(tasks))
    elif request.method == 'POST':
        if request.form['submit_button'] == HOME:
            return redirect(url_for("index"))
        right = 0
        if request.form['submit_button'] == DONE:
            for i in range(len(tasks)):
                db_sess = db_session.create_session()
                task = db_sess.query(Task).filter(Task.id == tasks[i].id).first()
                tasks[i] = (i, task, request.form[str(i)], loads(task.answers))
                if request.form[str(i)] in loads(task.answers):
                    right += 1
            return render_template('testDone.html', title='Результаты', agreed=AGREED,
                        done_tasks=tasks, result=round(right * 100 / len(tasks), 1))
        if request.form['submit_button'] == AGREED:
            return redirect(url_for("index"))

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)

@app.route('/registrate', methods=['GET', 'POST'])
def registrate():
    form = RegistrateForm()
    with open('config/open pass.txt') as f:
        open_email = f.readline()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user:
            return render_template('register.html', title='Регистрация', type='Ученик',
                                   message='Пользователь уже существует',
                                   form=form)
        if form.password1.data != form.password2.data:
            return render_template('register.html', title='Регистрация', type='Ученик',
                                   message='Пароли различны',
                                   form=form)
        if form.type.data == 'Ученик':
            user = User()
            user.name = form.username.data
            user.about = form.about.data
            user.email = form.email.data
            user.set_password(form.password1.data)
            db_sess = db_session.create_session()
            db_sess.add(user)
            db_sess.commit()
            return form.username.data
        elif form.type.data == 'Учитель':
            if form.key.data:
                pass
            else:
                return render_template('register.html', title='Регистрация', type='Учитель', open_email=open_email,
                                        form=form)
        elif form.type.data == 'Администратор':
            if form.key.data:
                with open('config/admin passes.txt', 'r') as passes:
                    admins = passes.read().split('\n')
                    for admin in admins:
                        email, keyHash = admin.split()
                        if email == form.email.data:
                            break
                if check_password_hash(keyHash, form.key.data):
                    user = User(name=form.username.data,
                                about=form.about.data,
                                email=form.email.data,
                                type='admin')
                    user.set_password(form.password1.data)
                    db_sess = db_session.create_session()
                    db_sess.add(user)
                    db_sess.commit()
            else:
                return render_template('register.html', title='Регистрация', type='Администратор',
                                       open_email=open_email, form=form)

        return form.username.data
    return render_template('register.html', title='Регистрация', type='Ученик', open_email=open_email,
                           form=form)


if __name__ == '__main__':
    db_session.global_init("db/blogs.db")
    app.run(port=8000, host='127.0.0.1')
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(
        days=14
    )