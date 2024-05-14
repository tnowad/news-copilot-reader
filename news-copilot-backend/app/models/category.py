from typing import TYPE_CHECKING, List

from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import Mapped, relationship, validates
from app.extensions import db
from app.errors.validation_error import ValidationError
import re

if TYPE_CHECKING:
    from app.models.article import Article


class Category(db.Model):
    __tablename__ = "categories"
    id = db.Column(Integer, primary_key=True)
    description = db.Column(Text, nullable=True)
    title = db.Column(String(255), nullable=False)
    slug = db.Column(String(255), nullable=False, unique=True)
    articles: Mapped[List["Article"]] = relationship(
        "Article", secondary="articles_categories", overlaps="categories"
    )

    def __init__(self, title, slug=None, description=None):
        self.title = title
        self.slug = slug
        self.description = description

    def __repr__(self):
        return f"<Category {self.title}>"

    @validates("title")
    def validate_title(self, key, title):
        if not title:
            raise ValidationError(field="title", message="Title cannot be empty")
        return title

    @validates("slug")
    def validate_slug(self, key, slug):
        if not slug:
            raise ValidationError(field="slug", message="Slug cannot be empty")
        if not re.match(r"^[a-z0-9-]+$", slug):
            raise ValidationError(
                field="slug",
                message="Slug can only contain lowercase letters, numbers, and hyphens",
            )
        return slug

    @validates("description")
    def validate_description(self, key, description):
        if description and len(description) > 1000:
            raise ValidationError(
                field="description", message="Description is too long"
            )
        return description
