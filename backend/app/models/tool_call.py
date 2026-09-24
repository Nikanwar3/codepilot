import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Enum, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from app.models.enums import ToolCallStatus

if TYPE_CHECKING:
    from app.models.agent_run import AgentRun


class ToolCall(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """
    Audit log of every tool invocation an agent makes — read_file, search_code,
    list_files, run_tests, run_linter, git_diff, apply_patch, dependency_scan.
    This is what makes an agent run debuggable and explainable after the fact.
    """

    __tablename__ = "tool_calls"

    agent_run_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("agent_runs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    agent_name: Mapped[str] = mapped_column(String(50), nullable=False)
    tool_name: Mapped[str] = mapped_column(String(100), nullable=False)
    input_args: Mapped[dict] = mapped_column(JSONB, nullable=False)
    output: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    status: Mapped[ToolCallStatus] = mapped_column(
        Enum(
            ToolCallStatus,
            name="tool_call_status",
            values_callable=lambda e: [m.value for m in e],
        ),
        default=ToolCallStatus.PENDING,
        nullable=False,
    )
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    duration_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)

    agent_run: Mapped["AgentRun"] = relationship(back_populates="tool_calls")

    def __repr__(self) -> str:
        return f"ToolCall(id={self.id!r}, tool_name={self.tool_name!r}, status={self.status!r})"
