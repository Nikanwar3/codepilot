import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, DateTime, Enum, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from app.models.enums import RepositoryStatus

if TYPE_CHECKING:
    from app.models.file import File
    from app.models.task import Task
    from app.models.user import User


class Repository(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "repositories"
    __table_args__ = (UniqueConstraint("owner_id", "full_name", name="uq_repository_owner_name"),)

    owner_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    github_repo_id: Mapped[int | None] = mapped_column(BigInteger, unique=True, nullable=True)
    # e.g. "octocat/hello-world"
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    clone_url: Mapped[str] = mapped_column(Text, nullable=False)
    default_branch: Mapped[str] = mapped_column(String(255), default="main", nullable=False)
    status: Mapped[RepositoryStatus] = mapped_column(
        Enum(
            RepositoryStatus,
            name="repository_status",
            values_callable=lambda e: [m.value for m in e],
        ),
        default=RepositoryStatus.PENDING,
        nullable=False,
    )
    last_indexed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    last_indexed_commit_sha: Mapped[str | None] = mapped_column(String(40), nullable=True)

    owner: Mapped["User"] = relationship(back_populates="repositories")
    files: Mapped[list["File"]] = relationship(
        back_populates="repository", cascade="all, delete-orphan"
    )
    tasks: Mapped[list["Task"]] = relationship(
        back_populates="repository", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"Repository(id={self.id!r}, full_name={self.full_name!r})"
