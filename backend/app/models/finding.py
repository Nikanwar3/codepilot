import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Enum, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from app.models.enums import FindingCategory, FindingSeverity, FindingStatus

if TYPE_CHECKING:
    from app.models.agent_run import AgentRun
    from app.models.file import File
    from app.models.patch import Patch


class Finding(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """A bug, vulnerability, or code-quality issue surfaced by an agent."""

    __tablename__ = "findings"

    agent_run_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("agent_runs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    # Nullable: some findings (e.g. a vulnerable dependency) aren't scoped to
    # one file.
    file_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("files.id", ondelete="SET NULL"), nullable=True, index=True
    )
    severity: Mapped[FindingSeverity] = mapped_column(
        Enum(
            FindingSeverity,
            name="finding_severity",
            values_callable=lambda e: [m.value for m in e],
        ),
        nullable=False,
    )
    category: Mapped[FindingCategory] = mapped_column(
        Enum(
            FindingCategory,
            name="finding_category",
            values_callable=lambda e: [m.value for m in e],
        ),
        nullable=False,
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    line_start: Mapped[int | None] = mapped_column(Integer, nullable=True)
    line_end: Mapped[int | None] = mapped_column(Integer, nullable=True)
    cwe_id: Mapped[str | None] = mapped_column(String(20), nullable=True)
    status: Mapped[FindingStatus] = mapped_column(
        Enum(
            FindingStatus, name="finding_status", values_callable=lambda e: [m.value for m in e]
        ),
        default=FindingStatus.OPEN,
        nullable=False,
    )

    agent_run: Mapped["AgentRun"] = relationship(back_populates="findings")
    file: Mapped["File | None"] = relationship(back_populates="findings")
    patches: Mapped[list["Patch"]] = relationship(back_populates="finding")

    def __repr__(self) -> str:
        return f"Finding(id={self.id!r}, severity={self.severity!r}, title={self.title!r})"
