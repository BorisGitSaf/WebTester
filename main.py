from flask import Flask, render_template, redirect, request, url_for, make_response, session
from flask_login import LoginManager
from datetime import timedelta
from data import db_session
from data.users import User
from data.tasks import Task
from data.task_kinds import Task_Kinds
from pickle import loads, dumps
from random import shuffle, randint

app = Flask(__name__)
with open('config/key.txt', 'r') as key:
    app.config['SECRET_KEY'] = key.readline()

@app.route('/')
@app.route('/index',  methods=['POST', 'GET'])
def index():
    return render_template('index.html', title='home')

@app.route('/base', methods=['POST', 'GET'])
def base():
    if request.method == 'POST':
       if request.form['submit_button'] == 'Go Home':
           return redirect(url_for("index"))
    elif request.method == 'GET':
        return render_template('base.html', title='base')

@app.route('/register',  methods=['POST', 'GET'])
def register():
    return render_template('register.html', title='Регистрация')

@app.route('/testBuild',  methods=['POST', 'GET'])
def testBuild():
    """TaskTypes = {'Пунктуация': {'Сложные предложения': [['Расставьте запятые',
                                                        'В заключение(1) хочется сказать(2) что я не злой(3) а добрый.',
                                                        ['23', '32']],
                                                        ['Расставьте запятые',
                                                         'Думая об этом(1) хочется сказать(2) что я не злой(3) а добрый.',
                                                         ['123', '321', '231', '132', '312', '213']]],
                                'Прямая речь': [['Есть ли прямая речь',
                                                 'В заключение автор сказал, что он не злой, а добрый.',
                                                 ['НЕТ', 'Нет']],
                                                ['Есть ли прямая речь',
                                                 'В заключение автор сказал что: "я не злой, а добрый".',
                                                 ['ДА', 'Да']]],
                                'Двоеточие и тире': [['Поставьте знак',
                                                     'Я увидел(..) летит птица',
                                                     [':', 'Двоеточие']]]},
                 'Орфография': {'Приставка': [['В каких словах пропущена буква "Е"?',
                                               'пр..обрести; пр..красный; пр..слушаться; пр..школьный',
                                               ['Прекрасный', 'прекрасный']]]}}
    user = User()
    user.name = "Адам"
    user.about = "Первый учитель"
    user.email = "email@email.ru"
    user.type = "teacher"
    db_sess = db_session.create_session()
    db_sess.add(user)
    db_sess.commit()

    task_type = Task_Kinds()
    task_type.name = 'Пунктуация'
    task_type.type = dumps(['Сложные предложения', 'Прямая речь', 'Двоеточие и тире'])
    db_sess = db_session.create_session()
    db_sess.add(task_type)
    db_sess.commit()
    task_type = Task_Kinds()
    task_type.name = 'Орфография'
    task_type.type = dumps(['Приставка'])
    db_sess = db_session.create_session()
    db_sess.add(task_type)
    db_sess.commit()
    for kind in TaskTypes.keys():
        for typ in TaskTypes[kind].keys():
            for exer in TaskTypes[kind][typ]:

                task = Task()
                task.kind = kind
                task.type = typ
                task.question = exer[0]
                task.text = exer[1]
                task.answers = dumps(exer[2])
                task.user_id = 1
                db_sess = db_session.create_session()
                task.user = db_sess.query(User).filter(User.id == 1).first()
                db_sess.add(task)
                db_sess.commit()"""
    joj = {}
    db_sess = db_session.create_session()
    for i in db_sess.query(Task_Kinds).all():
        joj[i.name] = list(map(lambda x: (x, db_sess.query(Task).filter(Task.type == x).count()), loads(i.type)))

    if request.method == 'POST':
        if request.form['submit_button'] == 'Go Home':
            return redirect(url_for("index"))
        if request.form['submit_button'] == 'Create':
            ojo = {}
            fase='test'
            for kind in joj.keys():
                for s in joj[kind]:
                    ojo[s[0]] = request.form[s[0]]
            return redirect(url_for("test", ojo=ojo, fase=fase))
    elif request.method == 'GET':
        return render_template('testBuild.html', title='Составить тест',
                           TaskTypes=joj)

@app.route("/cookie_test")
def cookie_test():
    visits_count = int(request.cookies.get("visits_count", 0))
    if visits_count:
        res = make_response(
            f"Вы пришли на эту страницу {visits_count + 1} раз")
        res.set_cookie("visits_count", str(visits_count + 1),
                       max_age=60 * 60 * 24 * 365 * 2)
    else:
        res = make_response(
            "Вы пришли на эту страницу в первый раз за последние 2 года")
        res.set_cookie("visits_count", '1',
                       max_age=60 * 60 * 24 * 365 * 2)
    return res

@app.route("/session_test")
def session_test():
    visits_count = session.get('visits_count', 0)
    session['visits_count'] = visits_count + 1
    return make_response(
        f"Вы пришли на эту страницу {visits_count + 1} раз")

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
        return render_template('test.html', title='Тест',
                        enumerate_tasks=enumerate(tasks))
    elif request.method == 'POST':
        if request.form['submit_button'] == 'Go Home':
            return redirect(url_for("index"))
        right = 0
        if request.form['submit_button'] == 'Сдать!':
            for i in range(len(tasks)):
                db_sess = db_session.create_session()
                task = db_sess.query(Task).filter(Task.id == tasks[i].id).first()
                tasks[i] = (i, task, request.form[str(i)], loads(task.answers))
                if request.form[str(i)] in loads(task.answers):
                    right += 1
            return render_template('testDone.html', title='Результаты',
                        done_tasks=tasks, result=round(right * 100 / len(tasks), 1))

a = ''
if __name__ == '__main__':
    db_session.global_init("db/blogs.db")
    app.run(port=8000, host='127.0.0.1')
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(
        days=365
    )