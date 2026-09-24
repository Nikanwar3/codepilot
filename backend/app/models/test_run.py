import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Enum, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from app.models.enums import TestRunStatus

if TYPE_CHECKING:
    from app.models.agent_run import AgentRun
    from app.models.patch import Patch


class TestRun(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """
    One execution of the test suite inside the Docker sandbox. patch_id is
    null for a baseline run (establishing the pre-patch test state) and set
    for a verification run after a patch is applied. attempt_number tracks
    the bounded retry loop (max 3) in the autonomous debugging flow.
    """

    __tablename__ = "test_runs"

    agent_run_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("agent_runs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    patch_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("patches.id", ondelete="SET NULL"), nullable=True, index=True
    )
    attempt_number: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    status: Mapped[TestRunStatus] = mapped_column(
        Enum(TestRunStatus, name="test_run_status", values_callable=lambda e: [m.value for m in e]),
        default=TestRunStatus.PENDING,
        nullable=False,
    )
    exit_code: Mapped[int | None] = mapped_column(Integer, nullable=True)
    stdout: Mapped[str | None] = mapped_column(Text, nullable=True)
    stderr: Mapped[str | None] = mapped_column(Text, nullable=True)
    duration_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    sandbox_container_id: Mapped[str | None] = mapped_column(String(64), nullable=True)

    agent_run: Mapped["AgentRun"] = relationship(back_populates="test_runs")
    patch: Mapped["Patch | None"] = relationship(back_populates="test_runs")

    def __repr__(self) -> str:
        return f"TestRun(id={self.id!r}, status={self.status!r}, attempt={self.attempt_number})"
