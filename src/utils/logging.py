"""Enhanced logging configuration with Logfire integration.

This module sets up structured logging with Logfire integration for
comprehensive monitoring and debugging of the multi-cloud agent.
"""

import logging
import uuid
from contextvars import ContextVar
from datetime import datetime
from typing import Any

import logfire
from logfire import span

# Initialize Logfire with automatic instrumentation
logfire.configure(
    service_name="multi-cloud-agent",
    service_version="1.0.0",
    environment="production",
    send_to_logfire="if-token-present",
)

# Instrument libraries
logfire.instrument_openai()
logfire.instrument_httpx()
logfire.instrument_asyncpg()

# Context variables for request tracking
request_id: ContextVar[str] = ContextVar("request_id", default="")
correlation_id: ContextVar[str] = ContextVar("correlation_id", default="")


class CloudAgentLogger:
    """Enhanced logger with Logfire integration.

    Attributes:
        logger: Base Python logger instance.
        default_extras: Default fields to include in all log messages.
    """

    def __init__(self, name: str, level: str = "INFO") -> None:
        """Initialize the logger with Logfire integration.

        Args:
            name: Logger name, typically __name__ of the calling module.
            level: Logging level (default: INFO).
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)

        # Add Logfire handler
        if not self.logger.handlers:
            handler = logfire.LogfireHandler()
            formatter = logfire.LogfireFormatter()
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

        self.default_extras = {
            "service": "multi-cloud-agent",
            "timestamp": datetime.utcnow().isoformat(),
        }

    def _log(self, level: int, message: str, **kwargs: Any) -> None:
        """Internal logging method with Logfire context injection.

        Args:
            level: Logging level.
            message: Log message.
            **kwargs: Additional context to include in the log.
        """
        with logfire.span(message) as span:
            extras = {
                **self.default_extras,
                **kwargs,
                "correlation_id": correlation_id.get(),
                "request_id": request_id.get(),
                "span_id": span.span_id,
                "trace_id": span.trace_id,
            }
            self.logger.log(level, message, extra=extras)

    @span("info_log")
    def info(self, message: str, **kwargs: Any) -> None:
        """Log an info message with Logfire tracing.

        Args:
            message: Log message.
            **kwargs: Additional context to include in the log.
        """
        self._log(logging.INFO, message, **kwargs)

    @span("error_log")
    def error(
        self, message: str, error: Exception | None = None, **kwargs: Any
    ) -> None:
        """Log an error message with Logfire tracing.

        Args:
            message: Log message.
            error: Optional exception to include in the log.
            **kwargs: Additional context to include in the log.
        """
        if error:
            kwargs["error_type"] = type(error).__name__
            kwargs["error_message"] = str(error)
            kwargs["exception"] = error
        self._log(logging.ERROR, message, **kwargs)


def with_logging(func):
    """Decorator to add Logfire tracing to functions.

    Args:
        func: Function to wrap with logging.

    Returns:
        Wrapped function with Logfire tracing.
    """

    @logfire.span(func.__name__)
    async def wrapper(*args, **kwargs):
        req_id = str(uuid.uuid4())
        request_id.set(req_id)

        logger = CloudAgentLogger(__name__)
        logger.info(f"Starting {func.__name__}", request_id=req_id)

        try:
            result = await func(*args, **kwargs)
            logger.info(f"Completed {func.__name__}", request_id=req_id)
            return result
        except Exception as e:
            logger.error(f"Error in {func.__name__}", error=e, request_id=req_id)
            raise

    return wrapper


# Global logger instance
logger = CloudAgentLogger(__name__)
