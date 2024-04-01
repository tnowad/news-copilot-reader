from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer
from sqlalchemy.orm import Mapped, relationship

from app.extensions import db

if TYPE_CHECKING:
    from app.models.article import Article
    from app.models.user import User


class Bookmark(db.Model):
    __tablename__ = "bookmarks"
    id = db.Column(Integer, primary_key=True)
    user_id = db.Column(Integer, ForeignKey("users.id"))
    article_id = db.Column(Integer, ForeignKey("articles.id"))
    created_at = db.Column(DateTime, nullable=False)

    article: Mapped["Article"] = relationship("Article", back_populates="bookmarks")
    user: Mapped["User"] = relationship("User", back_populates="bookmarks")

    def __init__(self, article_id, user_id, created_at):
        self.article_id = article_id
        self.user_id = user_id
        self.created_at = created_at
