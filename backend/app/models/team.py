"""
Team-related database models.
"""
import uuid
from typing import Optional
from sqlalchemy import Integer, UUID, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, validates
from app.db.base import Base, TimestampMixin


class TeamNode(Base, TimestampMixin):
    """
    Represents a managerial node - the persistent legal entity that survives name changes.
    This is the core concept that tracks team continuity through rebrands, mergers, and splits.
    """
    
    __tablename__ = "team_node"
    
    node_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4
    )
    founding_year: Mapped[int] = mapped_column(Integer, nullable=False)
    dissolution_year: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    __table_args__ = (
        CheckConstraint('founding_year >= 1900', name='check_founding_year_minimum'),
    )
    
    @validates('founding_year')
    def validate_founding_year(self, key, value):
        """Validate that founding_year is at least 1900."""
        if value < 1900:
            raise ValueError(f"founding_year must be >= 1900, got {value}")
        return value
    
    def __repr__(self) -> str:
        """Generate a helpful string representation."""
        dissolution = f", dissolution_year={self.dissolution_year}" if self.dissolution_year else ""
        return f"<TeamNode(node_id={self.node_id}, founding_year={self.founding_year}{dissolution})>"
