import sqlalchemy
from .db_session import SqlAlchemyBase


class Task_Kinds(SqlAlchemyBase):
    __tablename__ = 'task_kinds'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, unique=True, nullable=False)
    type = sqlalchemy.Column(sqlalchemy.PickleType, nullable=True)


def __str__(self):
    return f"{self.id} - {self.name}"


def __repr__(self):
    return f"{self.id} - {self.name}"
