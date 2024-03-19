from app.db import db
from enum import Enum


class RoleEnum(Enum):
    USER = "USER"
    WRITER = "WRITER"
    ADMIN = "ADMIN"


class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Enum(RoleEnum), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return "<Role {}>".format(self.name)
