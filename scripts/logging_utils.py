"""Logging helpers for the offline pipeline."""

from __future__ import annotations

import logging
import os
import sys
from typing import Optional


def setup_logging(level: int = logging.INFO, log_file: Optional[str] = None) -> None:
    """Configure root logging with optional file output."""

    handlers = [logging.StreamHandler(sys.stdout)]
    if log_file is not None:
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        handlers.append(logging.FileHandler(log_file))

    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        handlers=handlers,
    )

