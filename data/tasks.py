import datetime
import sqlalchemy
from sqlalchemy import orm

from .db_session import SqlAlchemyBase


class Task(SqlAlchemyBase):
    __tablename__ = 'tasks'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    kind = sqlalchemy.Column(sqlalchemy.String,
                             sqlalchemy.ForeignKey("task_kinds.name"),
                             nullable=False)
    type = sqlalchemy.Column(sqlalchemy.String,
                             sqlalchemy.ForeignKey("task_kinds.type"),
                             nullable=False)

    question = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    text = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    answers = sqlalchemy.Column(sqlalchemy.PickleType, nullable=False)
    answer_type = sqlalchemy.Column(sqlalchemy.String, nullable=False,
                                    default='text')

    created_date = sqlalchemy.Column(sqlalchemy.DateTime,
                                     default=datetime.datetime.now)
    user_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey("users.id"))
    user = orm.relation('User')
