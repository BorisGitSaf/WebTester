from flask import Flask, render_template, redirect, request, url_for, make_response, session
from flask_login import LoginManager, login_user, current_user, login_required, logout_user
from datetime import timedelta
from data import db_session
from data.loginform import LoginForm
from data.registrateionform import RegistrateForm
from data.users import User
from data.tasks import Task
from data.task_kinds import Task_Kinds
from pickle import loads, dumps
from random import shuffle, sample, randint
from werkzeug.security import generate_password_hash, check_password_hash

HOME = 'Домой'
CREATE = 'Создать'
DONE = 'Сдать!'
AGREED = 'Ясно'
HERE = "сюда!"
AUTHORIZE = 'Авторизация'
PROOF_CODE = 0

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
        return render_template('index.html', title='home', autho=AUTHORIZE, **kwargs)
    elif request.method == 'POST':
        if request.form['submit_button'] == HOME:
            return redirect(url_for("index"))
        if request.form['submit_button'] == AUTHORIZE:
            if AUTHORIZE == 'Профиль':
                return redirect(url_for("profile"))
            elif AUTHORIZE == 'Авторизация':
                return redirect(url_for("login"))
        if request.form['submit_button'] == HERE:
            return redirect(url_for("testBuild"))

@app.route('/base', methods=['POST', 'GET'])
def base():
    if request.method == 'POST':
       if request.form['submit_button'] == HOME:
           return redirect(url_for("index"))
       if request.form['submit_button'] == AUTHORIZE:
           if AUTHORIZE == 'Профиль':
               return redirect(url_for("profile"))
           elif AUTHORIZE == 'Авторизация':
               return redirect(url_for("login"))
    elif request.method == 'GET':
        return render_template('base.html', autho=AUTHORIZE, title='base')

@app.route('/testBuild',  methods=['POST', 'GET'])
def testBuild():
    joj = {}
    db_sess = db_session.create_session()
    for i in db_sess.query(Task_Kinds).all():
        joj[i.name] = list(map(lambda x: (x, db_sess.query(Task).filter(Task.type == x).count()), loads(i.type)))

    if request.method == 'POST':
        if request.form['submit_button'] == HOME:
            return redirect(url_for("index"))
        if request.form['submit_button'] == AUTHORIZE:
            if AUTHORIZE == 'Профиль':
                return redirect(url_for("profile"))
            elif AUTHORIZE == 'Авторизация':
                return redirect(url_for("login"))
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
                                TaskTypes=joj, autho=AUTHORIZE, create=CREATE)
    elif request.method == 'GET':
        return render_template('testBuild.html', title='Составить тест', autho=AUTHORIZE,
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
        return render_template('test.html', autho=AUTHORIZE, title='Тест', done=DONE,
                                enumerate_tasks=enumerate(tasks))
    elif request.method == 'POST':
        if request.form['submit_button'] == HOME:
            return redirect(url_for("index"))
        if request.form['submit_button'] == AUTHORIZE:
            if AUTHORIZE == 'Профиль':
                return redirect(url_for("profile"))
            elif AUTHORIZE == 'Авторизация':
                return redirect(url_for("login"))
        right = 0
        if request.form['submit_button'] == DONE:
            for i in range(len(tasks)):
                db_sess = db_session.create_session()
                task = db_sess.query(Task).filter(Task.id == tasks[i].id).first()
                tasks[i] = (i, task, request.form[str(i)], loads(task.answers))
                if request.form[str(i)] in loads(task.answers):
                    right += 1
            return render_template('testDone.html', title='Результаты', autho=AUTHORIZE, agreed=AGREED,
                        done_tasks=tasks, result=round(right * 100 / len(tasks), 1))
        if request.form['submit_button'] == AGREED:
            return redirect(url_for("index"))

@app.route('/login', methods=['GET', 'POST'])
def login():
    global AUTHORIZE

    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            AUTHORIZE = 'Профиль'
            return redirect("/profile")
        return render_template('login.html', autho=AUTHORIZE, title='Результаты',
                               message="Неправильный логин или пароль",
                               form=form)
    if request.method == 'POST':
        if request.form['submit_button'] == HOME:
            return redirect(url_for("index"))
        if request.form['submit_button'] == AUTHORIZE:
            if AUTHORIZE == 'Профиль':
                return redirect(url_for("profile"))
            elif AUTHORIZE == 'Авторизация':
                return redirect(url_for("login"))
    return render_template('login.html', autho=AUTHORIZE, title='Авторизация', form=form)

@app.route('/registrate', methods=['GET', 'POST'])
def registrate():
    global AUTHORIZE

    form = RegistrateForm()
    with open('config/open pass.txt') as f:
        open_email = f.readline()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user:
            return render_template('register.html', autho=AUTHORIZE, title='Регистрация', type='Ученик',
                                   message='Пользователь уже существует',
                                   form=form)
        if form.password1.data != form.password2.data:
            return render_template('register.html', autho=AUTHORIZE, title='Регистрация', type='Ученик',
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
        elif form.type.data == 'Администратор' or form.type.data == 'Учитель':
            translate = {'Администратор': 'admin', 'Учитель': 'teacher'}
            if form.key.data:
                with open('config/admin passes.txt', 'r') as passes:
                    admins = passes.read().split('\n')
                    for admin in admins:
                        type, email, keyHash = admin.split()
                        if type != translate[form.type.data]:
                            continue
                        if email == form.email.data:
                            break
                if check_password_hash(keyHash, form.key.data):
                    user = User(name=form.username.data,
                                about=form.about.data,
                                email=form.email.data,
                                type=translate[form.type.data])
                    user.set_password(form.password1.data)
                    db_sess = db_session.create_session()
                    db_sess.add(user)
                    db_sess.commit()
                else:
                    return render_template('register.html', autho=AUTHORIZE, title='Регистрация', type=form.type.data,
                                            open_email=open_email, form=form)
            else:
                return render_template('register.html', autho=AUTHORIZE, title='Регистрация', type=form.type.data,
                                       open_email=open_email, form=form)
        login_user(user, remember=True)
        AUTHORIZE = 'Профиль'
        return redirect("profile")
    elif request.method == 'POST':
        if request.form['submit_button'] == HOME:
            return redirect(url_for("index"))
        if request.form['submit_button'] == AUTHORIZE:
            if AUTHORIZE == 'Профиль':
                return redirect(url_for("profile"))
            elif AUTHORIZE == 'Авторизация':
                return redirect(url_for("login"))
    return render_template('register.html', autho=AUTHORIZE, title='Регистрация', type='Ученик', open_email=open_email,
                           form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    global PROOF_CODE, AUTHORIZE

    if request.method == "GET":
        return render_template("profile.html", autho=AUTHORIZE, user=current_user)
    elif request.method == "POST":
        if request.form['submit_button'] == HOME:
            return redirect(url_for("index"))
        if request.form['submit_button'] == AUTHORIZE:
            if AUTHORIZE == 'Профиль':
                return redirect(url_for("profile"))
            elif AUTHORIZE == 'Авторизация':
                return redirect(url_for("login"))
        if request.form['submit_button'] == "Генерировать ключ":
            if request.form.getlist('type') and request.form.getlist('email')[0]:
                db_sess = db_session.create_session()
                if any(map(lambda x: x.email == request.form['email'], db_sess.query(User).all())):
                    return render_template("profile.html", autho=AUTHORIZE, user=current_user,
                                           gener_message='Такой пользователь уже существует')
                key = ''.join(sample([chr(i) for i in range(48, 123) if chr(i) not in ['`', '%', '^', '<', '>',
                                                                                       '[', ']', "/", '=',
                                                                                       chr(92), ':', ';']],
                                     randint(10, 16)))
                with open('config/admin passes.txt', mode='w+', encoding='utf-8')as passes:
                    passes.write(f"{request.form['type']} {request.form['email']} {generate_password_hash(key)}")
                return render_template("profile.html", autho=AUTHORIZE, key=key, user=current_user)
            else:
                return render_template("profile.html", autho=AUTHORIZE, user=current_user,
                                       gener_message='Поля не заполнены')
            return render_template("profile.html", autho=AUTHORIZE, user=current_user)
        if request.form['submit_button'] == "Удалить":
            if not(request.form.getlist('deleteEmail')[0]):
                PROOF_CODE = 0
                return render_template("profile.html", autho=AUTHORIZE, user=current_user,
                                       message='Чтобы удалить кого-то, надо ввести почту',)
            else:
                print(PROOF_CODE)
                if PROOF_CODE:
                    if request.form['proof'] == str(PROOF_CODE) and request.form['deleteEmail'] != current_user.email:
                        db_sess = db_session.create_session()
                        if any(map(lambda x: x.email == request.form['deleteEmail'], db_sess.query(User).all())):
                            db_sess.query(User).filter(User.email == request.form['deleteEmail']).delete()
                            db_sess.commit()
                            PROOF_CODE = 0
                            return render_template("profile.html", autho=AUTHORIZE, user=current_user,
                                                   message='Пользователь успешно удалён',
                                                   proofCode='', deleted='')
                        else:
                            PROOF_CODE = 0
                            return render_template("profile.html", autho=AUTHORIZE, user=current_user,
                                                    message='Пользователя с такой почтой не существует')
                    PROOF_CODE = 0
                    return render_template("profile.html", autho=AUTHORIZE, user=current_user,
                                           message='Неправильно введены поля',
                                           proofCode='', deleted='')

                else:
                    db_sess = db_session.create_session()
                    if request.form['deleteEmail'] == current_user.email:
                        return render_template("profile.html", autho=AUTHORIZE, user=current_user,
                                               message='Нельзя удалять себя. Это жестоко')
                    if all(map(lambda x: x.email != request.form['deleteEmail'],
                               db_sess.query(User).filter(User.email != current_user.email))):
                        return render_template("profile.html", autho=AUTHORIZE, user=current_user,
                                               message='Пользователя с такой почтой не существует')
                    PROOF_CODE = randint(1000, 10000)
                    return render_template("profile.html", autho=AUTHORIZE, user=current_user,
                                           proofCode=PROOF_CODE, deleted=request.form['deleteEmail'])
        if request.form['submit_button'] == "Выйти":
            AUTHORIZE = 'Авторизация'
            return redirect(url_for('logout'))
    return render_template("profile.html", autho=AUTHORIZE, user=current_user)

if __name__ == '__main__':
    db_session.global_init("db/blogs.db")
    app.run(port=8000, host='127.0.0.1')
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(
        days=14
    )