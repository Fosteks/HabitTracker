import sqlalchemy
from .db_session import SqlAlchemyBase
from sqlalchemy import orm


class Habit(SqlAlchemyBase):
    __tablename__ = 'habits'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey("users.id"))
    user = orm.relationship('User')

    habit = sqlalchemy.Column(sqlalchemy.String, default="")

    day1 = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    day2 = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    day3 = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    day4 = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    day5 = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    day6 = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    day7 = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
