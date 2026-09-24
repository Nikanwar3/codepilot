import uuid
from typing import TYPE_CHECKING

from pgvector.sqlalchemy import Vector
from sqlalchemy import Enum, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from app.models.enums import ChunkType

if TYPE_CHECKING:
    from app.models.file import File

# Matches OpenAI's text-embedding-3-small. Changing this requires a new
# migration AND a full re-embedding backfill job, since the column width is
# fixed — call that out explicitly rather than treating it as a free knob.
EMBEDDING_DIMENSIONS = 1536


class CodeChunk(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "code_chunks"

    file_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("files.id", ondelete="CASCADE"), nullable=False, index=True
    )
    # Denormalized from files.repository_id so retrieval can filter by repo
    # without a join on the hot path (every RAG query hits this column).
    repository_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("repositories.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)
    start_line: Mapped[int] = mapped_column(Integer, nullable=False)
    end_line: Mapped[int] = mapped_column(Integer, nullable=False)
    chunk_type: Mapped[ChunkType] = mapped_column(
        Enum(ChunkType, name="chunk_type", values_callable=lambda e: [m.value for m in e]),
        nullable=False,
    )
    symbol_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    token_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    embedding: Mapped[list[float] | None] = mapped_column(
        Vector(EMBEDDING_DIMENSIONS), nullable=True
    )

    file: Mapped["File"] = relationship(back_populates="code_chunks")

    def __repr__(self) -> str:
        return (
            f"CodeChunk(id={self.id!r}, file_id={self.file_id!r}, "
            f"lines={self.start_line}-{self.end_line})"
        )
