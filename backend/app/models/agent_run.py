import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from app.models.enums import RunStatus

if TYPE_CHECKING:
    from app.models.finding import Finding
    from app.models.patch import Patch
    from app.models.task import Task
    from app.models.test_run import TestRun
    from app.models.tool_call import ToolCall


class AgentRun(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """
    One execution of the LangGraph agent graph for a task. A task can have
    multiple agent_runs if the user re-triggers it; each run owns its own
    tool_calls/findings/patches/test_runs so results from different attempts
    never mix.
    """

    __tablename__ = "agent_runs"

    task_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tasks.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    status: Mapped[RunStatus] = mapped_column(
        Enum(RunStatus, name="run_status", values_callable=lambda e: [m.value for m in e]),
        default=RunStatus.PENDING,
        nullable=False,
    )
    # Which LangGraph node is currently executing — supervisor, code_analysis,
    # security, test_debug, review. Surfaced to the frontend over SSE.
    current_agent: Mapped[str | None] = mapped_column(String(50), nullable=True)
    retry_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    max_retries: Mapped[int] = mapped_column(Integer, default=3, nullable=False)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    task: Mapped["Task"] = relationship(back_populates="agent_runs")
    tool_calls: Mapped[list["ToolCall"]] = relationship(
        back_populates="agent_run", cascade="all, delete-orphan"
    )
    findings: Mapped[list["Finding"]] = relationship(
        back_populates="agent_run", cascade="all, delete-orphan"
    )
    patches: Mapped[list["Patch"]] = relationship(
        back_populates="agent_run", cascade="all, delete-orphan"
    )
    test_runs: Mapped[list["TestRun"]] = relationship(
        back_populates="agent_run", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"AgentRun(id={self.id!r}, task_id={self.task_id!r}, status={self.status!r})"
