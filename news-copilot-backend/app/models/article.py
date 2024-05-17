from typing import TYPE_CHECKING, List

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, relationship, validates

from app.extensions import db
from app.errors.validation_error import ValidationError

if TYPE_CHECKING:
    from app.models.category import Category
    from app.models.comment import Comment
    from app.models.user import User
    from app.models.view import View
    from app.models.bookmark import Bookmark

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
        "Category",
        secondary=articles_categories_association_table,
        overlaps="categories",
    )
    comments: Mapped[List["Comment"]] = relationship(
        "Comment", back_populates="article"
    )
    views: Mapped[List["View"]] = relationship("View", back_populates="article")
    bookmarks: Mapped[List["Bookmark"]] = relationship(
        "Bookmark", back_populates="article"
    )

    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(
        db.DateTime, server_default=db.func.now(), onupdate=db.func.now()
    )
    deleted_at = db.Column(db.DateTime)

    def __init__(
        self,
        title,
        cover_image=None,
        summary=None,
        slug=None,
        content=None,
        created_at=None,
        updated_at=None,
        deleted_at=None,
    ):
        self.title = title
        self.cover_image = cover_image
        self.summary = summary
        self.slug = slug
        self.content = content
        self.created_at = created_at
        self.updated_at = updated_at
        self.deleted_at = deleted_at

    def __repr__(self):
        return f"<Article {self.title}>"

    @validates("title")
    def validate_title(self, key, title):
        if not title:
            raise ValidationError(field="title", message="Title cannot be empty")
        return title

    @validates("slug")
    def validate_slug(self, key, slug):
        if not slug:
            raise ValidationError(field="slug", message="Slug cannot be empty")
        return slug

    @validates("content")
    def validate_content(self, key, content):
        if not content:
            raise ValidationError(field="content", message="Content cannot be empty")
        return content

    @validates("summary")
    def validate_summary(self, key, summary):
        if summary and len(summary) > 2000:
            raise ValidationError(field="summary", message="Summary is too long")
        return summary
