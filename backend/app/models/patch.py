import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from app.models.enums import PatchStatus

if TYPE_CHECKING:
    from app.models.agent_run import AgentRun
    from app.models.finding import Finding
    from app.models.test_run import TestRun


class Patch(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """
    A generated code change, stored as a unified diff. Kept file-agnostic
    (a patch can span multiple files) rather than FK'd to a single File row.
    """

    __tablename__ = "patches"

    agent_run_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("agent_runs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    finding_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("findings.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    diff: Mapped[str] = mapped_column(Text, nullable=False)  # unified git diff format
    files_changed: Mapped[list[str]] = mapped_column(JSONB, nullable=False)
    commit_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[PatchStatus] = mapped_column(
        Enum(PatchStatus, name="patch_status", values_callable=lambda e: [m.value for m in e]),
        default=PatchStatus.PROPOSED,
        nullable=False,
    )
    applied_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    agent_run: Mapped["AgentRun"] = relationship(back_populates="patches")
    finding: Mapped["Finding | None"] = relationship(back_populates="patches")
    test_runs: Mapped[list["TestRun"]] = relationship(back_populates="patch")

    def __repr__(self) -> str:
        return (
            f"Patch(id={self.id!r}, status={self.status!r}, "
            f"files_changed={self.files_changed!r})"
        )
