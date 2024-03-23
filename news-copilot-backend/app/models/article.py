from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.db import db


class Article(db.Model):
    __tablename__ = "articles"
    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    cover_image = Column(String(255))
    summary = Column(Text)
    author_id = Column(Integer, ForeignKey("users.id"))
    author = relationship("User", back_populates="articles")

    def __init__(self, title, cover_image=None, summary=None, author=None):
        self.title = title
        self.cover_image = cover_image
        self.summary = summary
        self.author = author

    def __repr__(self):
        return f"<Article {self.title}>"
