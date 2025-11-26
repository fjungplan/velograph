"""Team-related database models.

Defines the persistent managerial node (TeamNode) and the yearly snapshots
of a team (TeamEra). TeamEra captures season-specific metadata while TeamNode
represents the enduring legal/managerial entity across rebrands.
"""
import uuid
from typing import Optional, List, TYPE_CHECKING
from sqlalchemy import (
    Integer,
    CheckConstraint,
    String,
    Boolean,
    ForeignKey,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, validates, relationship
from app.db.base import Base, TimestampMixin
from app.db.types import GUID

if TYPE_CHECKING:
    from app.models.sponsor import TeamSponsorLink


class TeamNode(Base, TimestampMixin):
    """
    Represents a managerial node - the persistent legal entity that survives name changes.
    This is the core concept that tracks team continuity through rebrands, mergers, and splits.
    """
    
    __tablename__ = "team_node"
    
    node_id: Mapped[uuid.UUID] = mapped_column(
        GUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    founding_year: Mapped[int] = mapped_column(Integer, nullable=False)
    dissolution_year: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Relationship to yearly eras (season snapshots)
    eras: Mapped[List["TeamEra"]] = relationship(
        "TeamEra",
        back_populates="node",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    # Lineage event relationships
    outgoing_events: Mapped[List["LineageEvent"]] = relationship(
        "LineageEvent",
        foreign_keys="LineageEvent.previous_node_id",
        back_populates="previous_node",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    incoming_events: Mapped[List["LineageEvent"]] = relationship(
        "LineageEvent",
        foreign_keys="LineageEvent.next_node_id",
        back_populates="next_node",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    def get_predecessors(self) -> list:
        """Return all predecessor TeamNodes via incoming lineage events."""
        return [event.previous_node for event in self.incoming_events if event.previous_node]

    def get_successors(self) -> list:
        """Return all successor TeamNodes via outgoing lineage events."""
        return [event.next_node for event in self.outgoing_events if event.next_node]
    
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


class TeamEra(Base, TimestampMixin):
    """Represents a team's state for a specific season year.

    Each era stores the registered name, optional UCI code, tier level, and
    source of origin (scraper or manual). A manual override flag prevents
    automated scrapers from altering curated data.
    """

    __tablename__ = "team_era"

    era_id: Mapped[uuid.UUID] = mapped_column(
        GUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    node_id: Mapped[uuid.UUID] = mapped_column(
        GUID(as_uuid=True), ForeignKey("team_node.node_id", ondelete="CASCADE"), nullable=False
    )
    season_year: Mapped[int] = mapped_column(Integer, nullable=False)
    registered_name: Mapped[str] = mapped_column(String(255), nullable=False)
    uci_code: Mapped[Optional[str]] = mapped_column(String(3), nullable=True)
    tier_level: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    source_origin: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    is_manual_override: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    # Relationships
    node: Mapped[TeamNode] = relationship("TeamNode", back_populates="eras")
    sponsor_links: Mapped[List["TeamSponsorLink"]] = relationship(
        "TeamSponsorLink",
        back_populates="era",
        cascade="all, delete-orphan",
        order_by="TeamSponsorLink.rank_order"
    )

    __table_args__ = (
        UniqueConstraint("node_id", "season_year", name="uq_node_year"),
        CheckConstraint(
            "season_year >= 1900 AND season_year <= 2100",
            name="check_season_year_range",
        ),
        CheckConstraint(
            "tier_level IN (1, 2, 3)", name="check_tier_level_values"
        ),
    )

    @validates("uci_code")
    def validate_uci_code(self, key, value):  # noqa: D401 - short validation
        if value is None:
            return value
        if len(value) != 3 or not value.isalpha() or not value.isupper():
            raise ValueError(
                f"uci_code must be exactly 3 uppercase letters, got {value!r}"
            )
        return value

    @validates("registered_name")
    def validate_registered_name(self, key, value):
        if value is None or value.strip() == "":
            raise ValueError("registered_name cannot be empty")
        return value.strip()

    @validates("tier_level")
    def validate_tier_level(self, key, value):
        if value is None:
            return value
        if value not in (1, 2, 3):
            raise ValueError(f"tier_level must be 1, 2, or 3; got {value}")
        return value

    def is_active(self, year: int) -> bool:
        """Return True if this era corresponds to the provided year."""
        return self.season_year == year

    @property
    def display_name(self) -> str:
        """Formatted display name for UI consumption."""
        return f"{self.registered_name} ({self.uci_code})" if self.uci_code else self.registered_name

    @property
    def sponsors_ordered(self) -> List["TeamSponsorLink"]:
        """Return sponsor links sorted by rank_order."""
        return sorted(self.sponsor_links, key=lambda link: link.rank_order)

    def validate_sponsor_total(self) -> bool:
        """Check if the sum of sponsor prominence percentages is <= 100.
        
        Returns:
            True if total is valid (<= 100%), False otherwise.
        """
        total = sum(link.prominence_percent for link in self.sponsor_links)
        return total <= 100

    def __repr__(self) -> str:  # pragma: no cover - debugging helper
        return (
            f"<TeamEra(era_id={self.era_id}, node_id={self.node_id}, season_year={self.season_year}, "
            f"registered_name={self.registered_name}, uci_code={self.uci_code}, tier_level={self.tier_level})>"
        )
