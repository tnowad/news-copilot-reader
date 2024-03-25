from typing import TYPE_CHECKING, List

from sqlalchemy.orm import Mapped, relationship

from app.extensions import db, bcrypt

if TYPE_CHECKING:
    from app.models.article import Article
    from app.models.role import Role

association_table = db.Table(
    "users_roles",
    db.Model.metadata,
    db.Column("user_id", db.Integer, db.ForeignKey("users.id")),
    db.Column("role_id", db.Integer, db.ForeignKey("roles.id")),
)


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), index=True, unique=True)
    display_name = db.Column(db.String(120))
    avatar_image = db.Column(db.String(120))
    password = db.Column(db.String(128))
    roles: Mapped[List["Role"]] = relationship(
        secondary=association_table, back_populates="users"
    )
    articles: Mapped[List["Article"]] = relationship("Article", back_populates="author")

    def __init__(self, email, display_name=None, avatar_image=None, password=None):
        self.email = email
        self.display_name = display_name
        self.avatar_image = avatar_image
        if password:
            self.set_password(password)

    def __repr__(self):
        return "<User {}>".format(self.email)

    def set_password(self, password):
        self.password = bcrypt.generate_password_hash(password).decode("utf-8")

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password, password)
