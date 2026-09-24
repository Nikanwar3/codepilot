import uuid
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.code_chunk import CodeChunk
    from app.models.finding import Finding
    from app.models.repository import Repository


class File(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "files"
    __table_args__ = (UniqueConstraint("repository_id", "path", name="uq_file_repository_path"),)

    repository_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("repositories.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    path: Mapped[str] = mapped_column(Text, nullable=False)  # relative to repo root
    language: Mapped[str | None] = mapped_column(String(50), nullable=True)
    size_bytes: Mapped[int] = mapped_column(BigInteger, nullable=False)
    # sha256 of file content — lets the ingestion job skip re-chunking/re-embedding
    # a file whose content hasn't changed since the last index run.
    content_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    last_commit_sha: Mapped[str | None] = mapped_column(String(40), nullable=True)

    repository: Mapped["Repository"] = relationship(back_populates="files")
    code_chunks: Mapped[list["CodeChunk"]] = relationship(
        back_populates="file", cascade="all, delete-orphan"
    )
    findings: Mapped[list["Finding"]] = relationship(back_populates="file")

    def __repr__(self) -> str:
        return f"File(id={self.id!r}, path={self.path!r})"
