from datetime import datetime, timezone
from sqlalchemy import ForeignKey, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column
from database import Model, TimestampMixin




class MarkOrm(TimestampMixin, Model):
    __tablename__ = 'marks'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    text: Mapped[str]
    tags: Mapped[list[str]] = mapped_column(JSON)
    latitude: Mapped[float]
    longitude: Mapped[float]