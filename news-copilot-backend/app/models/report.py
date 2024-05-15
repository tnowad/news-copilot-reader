from typing import TYPE_CHECKING
from sqlalchemy import Integer, String, Text, DateTime
from sqlalchemy.orm import Mapped, validates
from app.extensions import db
from app.errors.validation_error import ValidationError

if TYPE_CHECKING:
    from app.models.article import Article
    from app.models.comment import Comment
    from app.models.user import User


class Report(db.Model):
    __tablename__ = "reports"
    id = db.Column(Integer, primary_key=True)
    content = db.Column(Text, nullable=False)
    object_type = db.Column(String(50), nullable=False)
    object_id = db.Column(Integer, nullable=False)
    created_at = db.Column(DateTime, server_default=db.func.now())

    def __init__(self, content, object_id, object_type):
        self.content = content
        self.object_id = object_id
        self.object_type = object_type

    def __repr__(self):
        return f"<Report {self.id}>"

    @validates("content")
    def validate_content(self, key, content):
        if not content:
            raise ValidationError(field="content", message="Content cannot be empty")
        if len(content) > 1000:
            raise ValidationError(field="content", message="Content is too long")
        return content

    @validates("object_type")
    def validate_object_type(self, key, object_type):
        if object_type not in ["Article", "Comment", "User"]:
            raise ValidationError(field="object_type", message="Invalid object type")
        return object_type

    @validates("object_id")
    def validate_object_id(self, key, object_id):
        if self.object_type == "article":
            if not db.session.query(Article).filter_by(id=object_id).first():
                raise ValidationError(
                    field="object_id", message="Article ID does not exist"
                )
        elif self.object_type == "comment":
            if not db.session.query(Comment).filter_by(id=object_id).first():
                raise ValidationError(
                    field="object_id", message="Comment ID does not exist"
                )
        elif self.object_type == "user":
            if not db.session.query(User).filter_by(id=object_id).first():
                raise ValidationError(
                    field="object_id", message="User ID does not exist"
                )
        return object_id
