"""Structured logging setup for the crowd analysis pipeline.

Configures Python logging to output structured JSON lines to a file
and human-readable messages to the console.
"""

import json
import logging
import os
from datetime import datetime, timezone


class JSONLineFormatter(logging.Formatter):
    """Formats log records as single-line JSON objects."""

    def format(self, record: logging.LogRecord) -> str:
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "module": record.module,
            "message": record.getMessage(),
        }
        # Attach extra structured data if present
        if hasattr(record, "event_data"):
            entry["data"] = record.event_data
        return json.dumps(entry, default=str)


def setup_logger(
    name: str = "crowd_analysis",
    log_file: str | None = "logs/events.jsonl",
    console_level: int = logging.INFO,
) -> logging.Logger:
    """Create and configure a logger with console + optional file output.

    Args:
        name: Logger name.
        log_file: Path to JSONL log file (None to disable file logging).
        console_level: Minimum level for console output.

    Returns:
        Configured logging.Logger instance.
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # Avoid adding duplicate handlers on re-init
    if logger.handlers:
        return logger

    # --- Console handler (human-readable) ---
    console = logging.StreamHandler()
    console.setLevel(console_level)
    console.setFormatter(
        logging.Formatter("[%(asctime)s] %(levelname)-8s %(message)s", datefmt="%H:%M:%S")
    )
    logger.addHandler(console)

    # --- File handler (structured JSON lines) ---
    if log_file:
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        file_handler = logging.FileHandler(log_file, mode="a", encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(JSONLineFormatter())
        logger.addHandler(file_handler)

    return logger
