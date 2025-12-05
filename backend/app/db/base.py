"""
Base database models and mixins for SQLAlchemy.
"""
from datetime import datetime, timezone
from sqlalchemy import DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


def utc_now():
    """Return current UTC timestamp for database defaults (naive, for TIMESTAMP columns)."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


class Base(DeclarativeBase):
    """Base class for all database models."""
    
    def __repr__(self) -> str:
        """Generate a helpful string representation for debugging."""
        columns = ", ".join(
            [f"{k}={repr(v)}" for k, v in self.__dict__.items() if not k.startswith("_")]
        )
        return f"<{self.__class__.__name__}({columns})>"


class TimestampMixin:
    """Mixin to add created_at and updated_at timestamp columns."""
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime, 
        default=datetime.utcnow, 
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, 
        default=datetime.utcnow, 
        onupdate=datetime.utcnow, 
        nullable=False
    )
