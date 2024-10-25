"""
Description:
This module provides a logging configuration system that supports both traditional and structured logging with
JSON formatting, log rotation, log errors decorator, and flexible output options designed to be used for the AlForqan project.

Usage:
    >>> log_config = LogConfig(log_path="logs", environment="development", logger_source="my_app")
    >>> logger = log_config.get_logger()
    >>> logger.info("Something happened")

Authors:
    - M.Abdulrahman Alnaseer (GitHub: https://github.com/abdalrohman)

License:
    - MIT

Requirements:
    - structlog
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum
import functools
import logging
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path
import sys
import threading
import traceback
from typing import Any, TypeVar, cast

import structlog
from structlog.typing import Processor

# Type variables for generic type hints
T = TypeVar("T", bound=Callable[..., Any])


class LogLevel(str, Enum):
    """Valid logging levels."""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


@dataclass
class LogConfig:
    """
    Configuration class for setting up structured logging with rotation and filtering.

    :param log_path: Directory path where log files will be stored
    :param logger_source: Default source name for the logger
    :param log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    :param filters: List of strings to filter log messages
    :param log_filename: Name of the log file
    :param rotation_interval: When to rotate logs ('midnight', 'h', 'd', etc.)
    :param backup_count: Number of backup files to keep
    :param environment: Environment name ('development' or 'production')
    :param console_output: Whether to output logs to console

    Example:
            >>> log_config = LogConfig(
                log_path="logs",
                environment="development",
                logger_source="my_app"
            )
            ... logger = log_config.get_logger()
            ... logger.info("Something happened")
    """

    log_path: str | Path
    logger_source: str | None = None
    log_level: str = "INFO"
    filters: str | list[str] | None = None
    log_filename: str = "app.log"
    rotation_interval: str = "midnight"
    backup_count: int = 30
    environment: str = "production"
    console_output: bool | None = None

    # Internal state
    _configured: bool = field(default=False, init=False)
    _lock: threading.Lock = field(default_factory=threading.Lock, init=False)
    _loggers: dict[str, structlog.stdlib.BoundLogger] = field(default_factory=dict, init=False)

    def __post_init__(self) -> None:
        """Initialize derived attributes after instance creation."""
        self.log_path = Path(self.log_path)
        self.log_level = self._validate_log_level(self.log_level)
        self.environment = self.environment.lower()
        self.console_output = self.console_output if self.console_output is not None else (self.environment == "development")
        self.log_file_base = self.log_path / self.log_filename

        # Convert single filter to list
        if isinstance(self.filters, str):
            self.filters = [self.filters]

        # Initialize logging immediately
        self.configure_logging()

    @staticmethod
    def _validate_log_level(level: str) -> str:
        """Validate and normalize the log level."""
        try:
            return LogLevel[level.upper()].value
        except KeyError:
            raise ValueError(f"Invalid log level: {level}. Allowed values are: {', '.join(LogLevel.__members__)}")

    def _get_shared_processors(self) -> list[Processor]:
        """Get the list of shared log processors."""
        processors: list[Processor] = [
            structlog.contextvars.merge_contextvars,
            structlog.processors.TimeStamper(fmt="iso" if self.environment == "production" else "%H:%M:%S"),
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
        ]

        # Add custom filter if specified
        if self.filters:
            processors.append(self._create_filter())

        # Important: Add level filter after other processors
        # Commented out because it's cause conflect with other library used other logging system
        # processors.append(structlog.stdlib.filter_by_level)
        return processors

    def _create_file_handler(self) -> TimedRotatingFileHandler:
        """Create a rotating file handler for logging."""
        handler = TimedRotatingFileHandler(
            filename=str(self.log_file_base),
            when=self.rotation_interval,
            backupCount=self.backup_count,
            encoding="utf-8",
            delay=False,
            utc=True,
        )
        handler.setLevel(self.log_level)
        return handler

    def _create_filter(self) -> Processor:
        """Create a custom log filter processor."""

        def custom_filter(logger: Any, method_name: str, event_dict: dict) -> dict:
            message = str(event_dict.get("event", "")).lower()
            if not self.filters or not any(f.lower() in message for f in cast(list[str], self.filters)):
                return event_dict
            raise structlog.DropEvent

        return custom_filter

    def configure_logging(self) -> None:
        """Configure the logging system with the specified settings."""
        with self._lock:
            if self._configured:
                return

            # Ensure log directory exists
            self.log_path.mkdir(parents=True, exist_ok=True)

            # Reset logging configuration
            logging.root.handlers = []

            # Configure the root logger first
            root_logger = logging.getLogger()
            root_logger.setLevel(self.log_level)
            root_logger.handlers = []

            # Get shared processors
            shared_processors = self._get_shared_processors()

            # Create and configure handlers
            handlers = []

            # File handler with JSON formatting
            file_handler = self._create_file_handler()
            file_handler.setFormatter(
                structlog.stdlib.ProcessorFormatter(
                    processor=structlog.processors.JSONRenderer(),
                    foreign_pre_chain=shared_processors,
                )
            )
            handlers.append(file_handler)

            # Console handler if enabled
            if self.console_output:
                console_handler = logging.StreamHandler(sys.stdout)
                console_handler.setLevel(self.log_level)
                console_handler.setFormatter(
                    structlog.stdlib.ProcessorFormatter(
                        processor=structlog.dev.ConsoleRenderer(colors=True)
                        if self.environment == "development"
                        else structlog.processors.JSONRenderer(),
                        foreign_pre_chain=shared_processors,
                    )
                )
                handlers.append(console_handler)

            # Add all handlers to root logger
            for handler in handlers:
                root_logger.addHandler(handler)

            # Configure structlog
            structlog.configure(
                processors=[
                    *shared_processors,
                    structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
                ],
                context_class=dict,
                logger_factory=structlog.stdlib.LoggerFactory(),
                wrapper_class=structlog.stdlib.BoundLogger,
                cache_logger_on_first_use=True,
            )

            self._configured = True

    def get_logger(self, name: str | None = None) -> structlog.stdlib.BoundLogger:
        """Get a configured logger instance."""
        with self._lock:
            logger_name = name or self.logger_source or __name__

            if logger_name not in self._loggers:
                # Ensure logging is configured
                if not self._configured:
                    self.configure_logging()

                # Create and cache the logger
                logger = structlog.get_logger(logger_name)
                self._loggers[logger_name] = logger

            return self._loggers[logger_name]

    def log_errors(
        self,
        exclude: tuple[type[Exception], ...] | None = None,
        level: str = "ERROR",
    ) -> Callable[[T], T]:
        """
        Create an error logging decorator for the given function.

        :param exclude: Tuple of exception types to ignore
        :param level: Logging level to use for errors
        :return: Configured error logging decorator

        Example:
            >>> @log_config.log_errors()
            ... def risky_operation():
            ...     raise ValueError("Something went wrong")
        """
        logger = self.get_logger()

        def decorator(func: T) -> T:
            @functools.wraps(func)
            def wrapper(*args: Any, **kwargs: Any) -> Any:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if exclude and isinstance(e, exclude):
                        raise

                    # Get the full stack trace
                    exc_info = sys.exc_info()
                    stack_trace = "".join(traceback.format_exception(*exc_info)) if exc_info[0] is not None else ""

                    # Log the error using structured logging
                    log_method = getattr(logger, level.lower())
                    log_method(
                        "exception_occurred",
                        function=func.__qualname__,
                        module=func.__module__,
                        args=repr(args),
                        kwargs=repr(kwargs),
                        exception_type=e.__class__.__name__,
                        exception_message=str(e),
                        stack_trace=stack_trace,
                        exc_info=True,
                    )
                    raise

            return cast(T, wrapper)

        return decorator
