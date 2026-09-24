"""
Import every model module here so Base.metadata is fully populated as soon
as anything imports app.models — this is what makes Alembic autogenerate
(and Base.metadata.create_all in tests) see every table.
"""

from app.models.agent_run import AgentRun
from app.models.code_chunk import CodeChunk
from app.models.file import File
from app.models.finding import Finding
from app.models.patch import Patch
from app.models.repository import Repository
from app.models.task import Task
from app.models.test_run import TestRun
from app.models.tool_call import ToolCall
from app.models.user import User

__all__ = [
    "AgentRun",
    "CodeChunk",
    "File",
    "Finding",
    "Patch",
    "Repository",
    "Task",
    "TestRun",
    "ToolCall",
    "User",
]
