"""Tests for adaptive idle polling in CommunicationManager.

Purpose: verify idle polling backs off during inactivity and resets on activity.
Invariants: idle polling never exceeds configured max; motion resets to min.
Example: consecutive idle polls shift from 0.5s to 1.0s then 2.0s.
"""

import logging
from types import SimpleNamespace

from mc_desktop.communication import CommunicationManager


def test_idle_poll_interval_backoff():
    manager = CommunicationManager(parent=object(), logger=logging.getLogger("test_comm"))
    manager.connection = SimpleNamespace(is_open=True)
    manager.enable_polling()

    def fake_check_status():
        manager.in_motion = False
        return "0"

    manager.check_status = fake_check_status

    manager._idle_poll_interval = manager.IDLE_POLL_MIN_SECONDS
    manager._idle_poll_idle_streak = 0

    manager._poll_idle()
    assert manager._idle_poll_interval == manager.IDLE_POLL_MIN_SECONDS * manager.IDLE_POLL_BACKOFF_FACTOR

    manager._poll_idle()
    assert manager._idle_poll_interval == manager.IDLE_POLL_MAX_SECONDS


def test_idle_poll_interval_resets_on_motion():
    manager = CommunicationManager(parent=object(), logger=logging.getLogger("test_comm"))
    manager.connection = SimpleNamespace(is_open=True)
    manager.enable_polling()

    def fake_check_status():
        manager.in_motion = True
        return "1"

    manager.check_status = fake_check_status

    manager._idle_poll_interval = manager.IDLE_POLL_MAX_SECONDS
    manager._idle_poll_idle_streak = 2

    manager._poll_idle()
    assert manager._idle_poll_interval == manager.IDLE_POLL_MIN_SECONDS
    assert manager._idle_poll_idle_streak == 0


def test_worker_finished_marks_connection_lost():
    manager = CommunicationManager(parent=object(), logger=logging.getLogger("test_comm"))
    manager.connection = SimpleNamespace(is_open=True)
    manager._transport = SimpleNamespace(close=lambda: None)
    manager._alive = True
    manager._worker = object()

    manager._on_worker_finished()

    assert manager._alive is False
    assert manager._worker is None
    assert manager.connection is None
