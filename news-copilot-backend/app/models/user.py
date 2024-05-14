from typing import TYPE_CHECKING, List

from sqlalchemy.orm import Mapped, relationship
from sqlalchemy.orm import validates

from app.extensions import bcrypt, db
from app.errors.validation_error import ValidationError

if TYPE_CHECKING:
    from app.models.article import Article
    from app.models.comment import Comment
    from app.models.role import Role
    from app.models.view import View
    from app.models.bookmark import Bookmark

users_roles_association_table = db.Table(
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
    birth_date = db.Column(db.Date)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    phone_number = db.Column(db.String(20))
    updated_at = db.Column(
        db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now()
    )
    deleted_at = db.Column(db.DateTime)
    bio = db.Column(db.Text)
    password = db.Column(db.String(128))
    roles: Mapped[List["Role"]] = relationship(
        secondary=users_roles_association_table, back_populates="users"
    )
    articles: Mapped[List["Article"]] = relationship("Article", back_populates="author")
    comments: Mapped[List["Comment"]] = relationship("Comment", back_populates="author")

    views: Mapped[List["View"]] = relationship("View", back_populates="user")
    bookmarks: Mapped[List["Bookmark"]] = relationship(
        "Bookmark", back_populates="user"
    )

    def __init__(
        self,
        email,
        display_name=None,
        avatar_image=None,
        password=None,
        phone_number=None,
        bio=None,
        birth_date=None,
    ):
        self.email = email
        self.display_name = display_name
        self.avatar_image = avatar_image
        self.phone_number = phone_number
        self.bio = bio
        self.birth_date = birth_date
        if password:
            self.set_password(password)

    def __repr__(self):
        return "<User {}>".format(self.email)

    def set_password(self, password):
        self.password = bcrypt.generate_password_hash(password).decode("utf-8")

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password, password)

    def has_role(self, role_name):
        return role_name in [role.name for role in self.roles]

    @validates("email")
    def validate_email(self, key, email):
        if not email:
            raise ValidationError(field="email", message="Email cannot be empty")
        return email

    @validates("display_name")
    def validate_display_name(self, key, display_name):
        if not display_name:
            raise ValidationError(
                field="display_name", message="Display name cannot be empty"
            )
        return display_name
