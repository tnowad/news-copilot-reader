from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer
from sqlalchemy.orm import Mapped, relationship

from app.extensions import db

if TYPE_CHECKING:
    from app.models.article import Article
    from app.models.user import User


class View(db.Model):
    __tablename__ = "views"
    id = db.Column(Integer, primary_key=True)
    user_id = db.Column(Integer, ForeignKey("users.id"))
    article_id = db.Column(Integer, ForeignKey("articles.id"))
    viewed_at = db.Column(DateTime, nullable=False)

    article: Mapped["Article"] = relationship("Article", back_populates="views")
    user: Mapped["User"] = relationship("User", back_populates="views")

    def __init__(self, article_id, user_id, viewed_at):
        self.article_id = article_id
        self.user_id = user_id
        self.viewed_at = viewed_at
