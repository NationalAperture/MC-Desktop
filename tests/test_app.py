import logging
import tempfile
import unittest
from pathlib import Path

from mc_desktop.app import configure_logging


def _reset_logger(logger: logging.Logger) -> None:
    for handler in list(logger.handlers):
        logger.removeHandler(handler)
        handler.close()
    logger.setLevel(logging.NOTSET)


class ConfigureLoggingTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.logger = logging.getLogger("mc_desktop")
        _reset_logger(self.logger)

    def tearDown(self) -> None:
        _reset_logger(self.logger)

    def test_configure_logging_creates_handlers(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            log_dir = Path(tmp_dir)
            logger = configure_logging(log_dir)
            logger.info("smoke test")

            self.assertTrue(logger.handlers)
            self.assertTrue((log_dir / "info.log").exists())

    def test_configure_logging_is_idempotent(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            log_dir = Path(tmp_dir)
            first_logger = configure_logging(log_dir)
            first_handlers = list(first_logger.handlers)

            second_logger = configure_logging(log_dir)
            second_handlers = list(second_logger.handlers)

            self.assertEqual(first_logger, second_logger)
            self.assertEqual(first_handlers, second_handlers)


if __name__ == "__main__":
    unittest.main()
