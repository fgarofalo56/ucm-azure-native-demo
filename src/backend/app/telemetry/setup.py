"""OpenTelemetry + Azure Monitor telemetry configuration."""

import logging

import structlog
from app.config import settings


def _get_log_level(level_name: str) -> int:
    """Convert a log level name to its numeric value."""
    return getattr(logging, level_name.upper(), logging.INFO)


def configure_telemetry() -> None:
    """Configure OpenTelemetry with Azure Monitor exporter."""
    # Configure structlog
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.dev.set_exc_info,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer() if settings.is_production else structlog.dev.ConsoleRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(
            _get_log_level(settings.log_level)
        ),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # Configure Azure Monitor OpenTelemetry (if connection string available)
    connection_string = settings.applicationinsights_connection_string
    if connection_string:
        try:
            from azure.monitor.opentelemetry import configure_azure_monitor

            configure_azure_monitor(
                connection_string=connection_string,
                enable_live_metrics=settings.is_production,
            )
            structlog.get_logger().info("azure_monitor_configured")
        except ImportError:
            structlog.get_logger().warning("azure_monitor_sdk_not_installed")
