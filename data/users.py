import datetime
import sqlalchemy
from flask_login import UserMixin
from .db_session import SqlAlchemyBase
from sqlalchemy import orm
from pickle import dumps
from werkzeug.security import generate_password_hash, check_password_hash


class User(SqlAlchemyBase, UserMixin):
    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    type = sqlalchemy.Column(sqlalchemy.String, nullable=False,
                             default='student')
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    about = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    email = sqlalchemy.Column(sqlalchemy.String,
                              index=True, unique=True, nullable=True)
    hashed_password = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    created_date = sqlalchemy.Column(sqlalchemy.DateTime,
                                     default=datetime.datetime.now)
    tasks = orm.relation("Task", back_populates='user')
    container = sqlalchemy.Column(sqlalchemy.PickleType,
                                  nullable=True,
                                  default=dumps(list()))

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)