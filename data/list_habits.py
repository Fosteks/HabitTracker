import sqlalchemy
from .db_session import SqlAlchemyBase
from sqlalchemy import orm


class ListHabit(SqlAlchemyBase):
    __tablename__ = 'list_habits'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    habit = sqlalchemy.Column(sqlalchemy.String, default="")
    group = sqlalchemy.Column(sqlalchemy.String, default="")