from typing import TYPE_CHECKING, List

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, relationship

from app.extensions import db

if TYPE_CHECKING:
    from app.models.article import Article


class Category(db.Model):
    __tablename__ = "categories"
    id = db.Column(Integer, primary_key=True)
    title = db.Column(String(255), nullable=False)
    slug = db.Column(String(255), nullable=False, unique=True)
    articles: Mapped[List["Article"]] = relationship(
        "Article", secondary="articles_categories"
    )

    def __init__(
        self,
        title,
        slug=None,
    ):
        self.title = title
        self.slug = slug

    def __repr__(self):
        return f"<Article {self.title}>"
