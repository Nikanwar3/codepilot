"""
Enums shared across models, materialized as native Postgres ENUM types
(rather than plain strings + a CHECK constraint) so invalid states are
rejected by the database itself, not just by application code.
"""

import enum


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    DEVELOPER = "developer"
    VIEWER = "viewer"


class RepositoryStatus(str, enum.Enum):
    PENDING = "pending"
    CLONING = "cloning"
    INDEXING = "indexing"
    READY = "ready"
    FAILED = "failed"


class ChunkType(str, enum.Enum):
    MODULE = "module"
    CLASS = "class"
    FUNCTION = "function"
    BLOCK = "block"


class TaskType(str, enum.Enum):
    EXPLAIN_ARCHITECTURE = "explain_architecture"
    FIND_BUGS = "find_bugs"
    SECURITY_SCAN = "security_scan"
    FIX_BUG = "fix_bug"
    GENERATE_PATCH = "generate_patch"
    CUSTOM = "custom"


class RunStatus(str, enum.Enum):
    """Shared by tasks and agent_runs — both progress through the same lifecycle."""

    PENDING = "pending"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ToolCallStatus(str, enum.Enum):
    PENDING = "pending"
    SUCCESS = "success"
    ERROR = "error"


class FindingSeverity(str, enum.Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class FindingCategory(str, enum.Enum):
    SECURITY = "security"
    BUG = "bug"
    CODE_SMELL = "code_smell"
    PERFORMANCE = "performance"
    STYLE = "style"


class FindingStatus(str, enum.Enum):
    OPEN = "open"
    ACKNOWLEDGED = "acknowledged"
    FIXED = "fixed"
    WONT_FIX = "wont_fix"
    FALSE_POSITIVE = "false_positive"


class PatchStatus(str, enum.Enum):
    PROPOSED = "proposed"
    APPLIED = "applied"
    REVERTED = "reverted"
    REJECTED = "rejected"


class TestRunStatus(str, enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    ERROR = "error"
    TIMEOUT = "timeout"
