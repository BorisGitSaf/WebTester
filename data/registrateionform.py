from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, SubmitField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired


class RegistrateForm(FlaskForm):
    username = StringField('Имя', validators=[DataRequired()])
    email = EmailField('Почта', validators=[DataRequired()])
    about = StringField('Немного о себе')
    type = SelectField('Вид пользователя',
                       choices=['Ученик', 'Учитель', 'Администратор'])
    key = StringField('Ключ')
    password1 = PasswordField('Пароль', validators=[DataRequired()])
    password2 = PasswordField('Повторите пароль',
                              validators=[DataRequired()])
    submit = SubmitField('Зарегистрироваться')
