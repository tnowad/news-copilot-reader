from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.db import db


class Article(db.Model):
    __tablename__ = "articles"
    id = db.Column(Integer, primary_key=True)
    title = db.Column(String(255), nullable=False)
    cover_image = db.Column(String(255))
    summary = db.Column(Text)
    author_id = db.Column(Integer, ForeignKey("users.id"))
    author = relationship("User", back_populates="articles")

    def __init__(self, title, cover_image=None, summary=None, author=None):
        self.title = title
        self.cover_image = cover_image
        self.summary = summary
        self.author = author

    def __repr__(self):
        return f"<Article {self.title}>"
