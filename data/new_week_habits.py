import sqlalchemy
from .db_session import SqlAlchemyBase
from sqlalchemy import orm


class NewWeekHabit(SqlAlchemyBase):
    __tablename__ = 'new_week_habits'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey("users.id"))
    user = orm.relationship('User')

    nw_habit = sqlalchemy.Column(sqlalchemy.String, default="")
    group = sqlalchemy.Column(sqlalchemy.String, default="")