from sqlalchemy import Column, String, Text, TIMESTAMP, Enum, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.db.base import Base, utc_now
from app.db.types import GUID
import enum
import uuid


class EditType(str, enum.Enum):
    METADATA = "METADATA"
    MERGE = "MERGE"
    SPLIT = "SPLIT"
    DISSOLVE = "DISSOLVE"


class EditStatus(str, enum.Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class Edit(Base):
    __tablename__ = "edits"
    
    edit_id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID(), ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False)
    edit_type = Column(Enum(EditType, native_enum=False), nullable=False)
    target_era_id = Column(GUID(), ForeignKey('team_era.era_id', ondelete='CASCADE'), nullable=True)
    target_node_id = Column(GUID(), ForeignKey('team_node.node_id', ondelete='CASCADE'), nullable=True)
    changes = Column(JSON, nullable=False)
    reason = Column(Text, nullable=False)
    status = Column(Enum(EditStatus, native_enum=False), default=EditStatus.PENDING)
    reviewed_by = Column(GUID(), ForeignKey('users.user_id', ondelete='SET NULL'), nullable=True)
    reviewed_at = Column(TIMESTAMP, nullable=True)
    review_notes = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP, default=utc_now)
    updated_at = Column(TIMESTAMP, default=utc_now, onupdate=utc_now)
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id])
    reviewer = relationship("User", foreign_keys=[reviewed_by])
    era = relationship("TeamEra", foreign_keys=[target_era_id])
    node = relationship("TeamNode", foreign_keys=[target_node_id])
