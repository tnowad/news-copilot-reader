from typing import TYPE_CHECKING, List

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, relationship

from app.extensions import db

if TYPE_CHECKING:
    from app.models.category import Category
    from app.models.user import User

articles_categories_association_table = db.Table(
    "articles_categories",
    db.Model.metadata,
    db.Column("article_id", db.Integer, db.ForeignKey("articles.id")),
    db.Column("category_id", db.Integer, db.ForeignKey("categories.id")),
)


class Article(db.Model):
    __tablename__ = "articles"
    id = db.Column(Integer, primary_key=True)
    title = db.Column(String(255), nullable=False)
    cover_image = db.Column(String(255))
    summary = db.Column(Text)
    content = db.Column(Text)
    slug = db.Column(String(255), unique=True)
    author_id = db.Column(Integer, ForeignKey("users.id"))
    author: Mapped["User"] = relationship("User", back_populates="articles")
    categories: Mapped[List["Category"]] = relationship(
        "Category", secondary=articles_categories_association_table
    )
    comments: Mapped[List["Comment"]] = relationship(
        "Comment", back_populates="article"
    )

    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(
        db.DateTime, server_default=db.func.now(), onupdate=db.func.now()
    )
    deleted_at = db.Column(db.DateTime)

    def __init__(self, title, cover_image=None, summary=None, slug=None, content=None):
        self.title = title
        self.cover_image = cover_image
        self.summary = summary
        self.slug = slug
        self.content = content

    def __repr__(self):
        return f"<Article {self.title}>"
