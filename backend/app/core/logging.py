"""
Structured (JSON-capable) logging setup using structlog.

Why structlog instead of stdlib logging with a string format: every log line
in a distributed system (FastAPI request -> Celery task -> LangGraph agent
step -> tool call) needs to carry correlation fields (request_id, user_id,
repo_id, task_id) so they can be filtered in Grafana/Loki or any log
aggregator. structlog makes "bind a field, it shows up on every subsequent
log call in this context" cheap, which plain logging does not.

In local dev we render human-readable console output; in staging/production
we render single-line JSON so log shippers can parse it without regex.
"""

import logging
import sys

import structlog

from app.core.config import settings


def configure_logging() -> None:
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=settings.LOG_LEVEL,
    )

    shared_processors: list[structlog.types.Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]

    if settings.ENVIRONMENT == "local":
        renderer: structlog.types.Processor = structlog.dev.ConsoleRenderer()
    else:
        renderer = structlog.processors.JSONRenderer()

    structlog.configure(
        processors=[*shared_processors, renderer],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    return structlog.get_logger(name)
