from enum import Enum
from typing import TYPE_CHECKING, List

from sqlalchemy.orm import Mapped, relationship

from app.extensions import db

if TYPE_CHECKING:
    from app.models.user import User


class RoleEnum(Enum):
    USER = "USER"
    WRITER = "WRITER"
    ADMIN = "ADMIN"

    def __str__(self):
        return self.value


class Role(db.Model):
    __tablename__ = "roles"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Enum(RoleEnum), unique=True, nullable=False)
    users: Mapped[List["User"]] = relationship("User", secondary="users_roles")

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return "<Role {}>".format(self.name)
