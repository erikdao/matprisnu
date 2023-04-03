"""Logger utility module Configures the default logging to be routed to loguru
and adds Sentry."""
import logging
import os

import sentry_sdk
from dotenv import load_dotenv
from loguru import logger
from sentry_sdk.integrations.logging import (BreadcrumbHandler, EventHandler,
                                             LoggingIntegration)

load_dotenv(os.path.join(os.getcwd(), ".env"))


class InterceptHandler(logging.Handler):
    """Intercept built-in logging messages and route them to loguru Copied from
    https://github.com/getsentry/sentry-
    python/issues/653#issuecomment-788854865."""

    def emit(self, record):
        # Get corresponding loguru level if exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find the caller originates the logged message
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


# Enable interceptor
logging.basicConfig(handlers=[InterceptHandler()], level=0)

logger.add(BreadcrumbHandler(level=logging.DEBUG), level=logging.DEBUG)
logger.add(EventHandler(level=logging.ERROR), level=logging.ERROR)

sentry_sdk.init(
    dsn=os.getenv("SENTRY_DSN"),
    integrations=[
        LoggingIntegration(level=None, event_level=None),
    ],
    traces_sample_rate=1.0,
    environment=os.getenv("ENVIRONMENT"),
)

sentry_logger = logger
