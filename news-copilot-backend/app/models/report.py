from typing import TYPE_CHECKING
from sqlalchemy import ForeignKey, Integer, String, Text, DateTime
from sqlalchemy.orm import Mapped, relationship

from app.extensions import db

# 3 types : article , comment , user


class Report(db.Model):
    __tablename__ = "report"
    title = db.Column(String, nullable=False)
    id = db.Column(Integer, primary_key=True)
    content = db.Column(Text, nullable=False)
    object_type = db.Column(Text, nullable=False)
    object_id = db.Column(Integer, nullable=False)
    created_at = db.Column(DateTime, server_default=db.func.now())

    def __init__(self, id, content, object_id, object_type, created_at=0):
        self.content = content
        self.created_at = created_at
        self.id = id
        self.object_id = object_id
        self.object_type = object_type
