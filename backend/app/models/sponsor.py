"""Sponsor data models."""
import re
import uuid
from datetime import datetime
from typing import Optional, TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy import String, Integer, ForeignKey, CheckConstraint, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates

from app.db.base import Base
from app.db.types import GUID

if TYPE_CHECKING:
    from app.models.team import TeamEra


class SponsorMaster(Base):
    """Master sponsor entity representing the legal parent company."""
    
    __tablename__ = "sponsor_master"
    
    master_id: Mapped[uuid.UUID] = mapped_column(
        GUID(as_uuid=True), 
        primary_key=True,
        default=uuid.uuid4
    )
    legal_name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    industry_sector: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow,
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow,
        nullable=False
    )
    
    # Relationships
    brands: Mapped[list["SponsorBrand"]] = relationship(
        "SponsorBrand",
        back_populates="master",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        return f"<SponsorMaster(id={self.master_id}, name='{self.legal_name}')>"


class SponsorBrand(Base):
    """Brand name under a sponsor master, with default jersey color."""
    
    __tablename__ = "sponsor_brand"
    
    brand_id: Mapped[uuid.UUID] = mapped_column(
        GUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    master_id: Mapped[uuid.UUID] = mapped_column(
        GUID(as_uuid=True),
        ForeignKey("sponsor_master.master_id", ondelete="CASCADE"),
        nullable=False
    )
    brand_name: Mapped[str] = mapped_column(String(255), nullable=False)
    default_hex_color: Mapped[str] = mapped_column(String(7), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow,
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow,
        nullable=False
    )
    
    # Relationships
    master: Mapped["SponsorMaster"] = relationship(
        "SponsorMaster",
        back_populates="brands"
    )
    team_links: Mapped[list["TeamSponsorLink"]] = relationship(
        "TeamSponsorLink",
        back_populates="brand",
        cascade="all, delete-orphan"
    )
    
    # Constraints
    __table_args__ = (
        UniqueConstraint("master_id", "brand_name", name="uq_master_brand"),
        # Note: Hex color validation is enforced via @validates decorator
        # for cross-database compatibility (PostgreSQL ~ operator not in SQLite)
    )
    
    @validates("default_hex_color")
    def validate_hex_color(self, key: str, value: str) -> str:
        """Validate hex color format."""
        if not re.match(r'^#[0-9A-Fa-f]{6}$', value):
            raise ValueError(
                f"Invalid hex color format: {value}. Must be #RRGGBB format."
            )
        return value
    
    def __repr__(self) -> str:
        return f"<SponsorBrand(id={self.brand_id}, name='{self.brand_name}', color='{self.default_hex_color}')>"


class TeamSponsorLink(Base):
    """Link between a team era and a sponsor brand with prominence information."""
    
    __tablename__ = "team_sponsor_link"
    
    link_id: Mapped[uuid.UUID] = mapped_column(
        GUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    era_id: Mapped[uuid.UUID] = mapped_column(
        GUID(as_uuid=True),
        ForeignKey("team_era.era_id", ondelete="CASCADE"),
        nullable=False
    )
    brand_id: Mapped[uuid.UUID] = mapped_column(
        GUID(as_uuid=True),
        ForeignKey("sponsor_brand.brand_id", ondelete="RESTRICT"),
        nullable=False
    )
    rank_order: Mapped[int] = mapped_column(Integer, nullable=False)
    prominence_percent: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow,
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow,
        nullable=False
    )
    
    # Relationships
    era: Mapped["TeamEra"] = relationship(
        "TeamEra",
        back_populates="sponsor_links"
    )
    brand: Mapped["SponsorBrand"] = relationship(
        "SponsorBrand",
        back_populates="team_links"
    )
    
    # Constraints
    __table_args__ = (
        UniqueConstraint("era_id", "brand_id", name="uq_era_brand"),
        UniqueConstraint("era_id", "rank_order", name="uq_era_rank"),
        CheckConstraint("rank_order >= 1", name="check_rank_order_positive"),
        CheckConstraint(
            "prominence_percent > 0 AND prominence_percent <= 100",
            name="check_prominence_range"
        ),
    )
    
    @validates("rank_order")
    def validate_rank_order(self, key: str, value: int) -> int:
        """Validate rank order is positive."""
        if value < 1:
            raise ValueError("rank_order must be >= 1")
        return value
    
    @validates("prominence_percent")
    def validate_prominence(self, key: str, value: int) -> int:
        """Validate prominence percentage is in valid range."""
        if value <= 0 or value > 100:
            raise ValueError("prominence_percent must be between 1 and 100")
        return value
    
    def __repr__(self) -> str:
        return f"<TeamSponsorLink(era={self.era_id}, brand={self.brand_id}, rank={self.rank_order}, prominence={self.prominence_percent}%)>"
