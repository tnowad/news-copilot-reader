from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, relationship

from app.extensions import db
from app.models.user import User


class Article(db.Model):
    __tablename__ = "articles"
    id = db.Column(Integer, primary_key=True)
    title = db.Column(String(255), nullable=False)
    cover_image = db.Column(String(255))
    summary = db.Column(Text)
    author_id = db.Column(Integer, ForeignKey("users.id"))
    author: Mapped["User"] = relationship("User", back_populates="articles")

    def __init__(self, title, cover_image=None, summary=None):
        self.title = title
        self.cover_image = cover_image
        self.summary = summary

    def __repr__(self):
        return f"<Article {self.title}>"
