from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Column, DateTime, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, relationship

from app.extensions import db

if TYPE_CHECKING:
    from app.models.article import Article
    from app.models.user import User


class Comment(db.Model):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    deleted_at = Column(DateTime, default=None, nullable=True)

    author_id = db.Column(Integer, ForeignKey("users.id"))
    author: Mapped["User"] = relationship("User", back_populates="comments")

    article_id = db.Column(Integer, ForeignKey("articles.id"))
    article: Mapped["Article"] = relationship("Article", back_populates="comments")

    parent_id = Column(Integer, ForeignKey("comments.id"))
    parent_comment: Mapped["Comment"] = relationship(
        "Comment", remote_side=[id], back_populates="child_comments"
    )

    child_comments: Mapped["Comment"] = relationship(
        "Comment", back_populates="parent_comment"
    )

    def __init__(self, content, author_id, article_id, parent_id=None):
        self.content = content
        self.author_id = author_id
        self.article_id = article_id
        self.parent_id = parent_id

    def __repr__(self):
        return f"<Comment {self.id}>"
