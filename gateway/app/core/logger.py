import structlog
import logging
import sys
from app.core.config import settings

def setup_logger():
    """
    Configures structlog to output JSON for production and pretty console logs for development.
    Structlog bridges the gap between standard Python logging and structured JSON.
    """
    logging.basicConfig(format="%(message)s", stream=sys.stdout, level=logging.INFO)

    # Processors are executed in order.
    processors = [
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]

    if settings.ENVIRONMENT.lower() == "development":
        # Pretty console rendering for local dev
        processors.append(structlog.dev.ConsoleRenderer(colors=True))
    else:
        # JSON formatting for Elasticsearch/Datadog in production
        processors.append(structlog.processors.JSONRenderer())

    structlog.configure(
        processors=processors,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

logger = structlog.get_logger()
