import sys
import serial
import traceback
from dataclasses import dataclass
from datetime import datetime
from queue import Empty, Queue
from time import sleep
from typing import Optional, Union, Any

from PySide6.QtCore import QRunnable, Signal, Slot, QObject, QThreadPool
from PySide6.QtWidgets import QMessageBox

from .commands import CMD_POSITION, CMD_STATUS

class WorkerSignals(QObject):
    finished = Signal()
    error = Signal(tuple)
    result = Signal(object)
    msg = Signal(str)
    progress = Signal(object)

class MySignal(QObject):
    main_thread = Signal(str)
    log = Signal(str)
    poll = Signal(str, str)
    command_complete = Signal(object, object)
    connection_lost = Signal(str)
    command_status = Signal(str, str)

class Worker(QRunnable):
    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

    @Slot()
    def run(self):
        try:
            result = self.fn(*self.args, **self.kwargs)
        except Exception as e:
            self.signals.error.emit((type(e), e, traceback.format_exc()))
        else:
            self.signals.result.emit(result)
        finally:
            self.signals.finished.emit()


class SerialTransport:
    """Thin wrapper around ``serial.Serial`` to simplify testing and error handling."""

    def __init__(self, logger, serial_module=serial):
        self._logger = logger
        self._serial_module = serial_module
        self._connection: Optional[Any] = None

    @property
    def connection(self) -> Optional[Any]:
        return self._connection

    def open(self, port: str, baudrate: Union[int, str], timeout: float = 0.5) -> Any:
        self.close()
        connection = self._serial_module.Serial(
            port=port,
            baudrate=baudrate,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            timeout=timeout,
        )
        self._connection = connection
        return connection

    def close(self) -> None:
        if self._connection and self._connection.is_open:
            self._connection.close()
        self._connection = None

    def write(self, payload: str) -> int:
        if not self._connection:
            raise serial.SerialException("Serial connection is not open.")
        if not self._connection.is_open:
            raise serial.SerialException("Serial port was closed.")
        encoded = payload.encode()
        bytes_written = self._connection.write(encoded)
        if bytes_written != len(encoded):
            raise serial.SerialException(
                f"Incomplete write: {bytes_written}/{len(encoded)} bytes"
            )
        return bytes_written

    def read_line(self) -> str:
        if not self._connection:
            raise serial.SerialException("Serial connection is not open.")
        if not self._connection.is_open:
            raise serial.SerialException("Serial port was closed.")
        return self._connection.readline().decode(errors="ignore").strip()


@dataclass
class SerialCommand:
    node_id: str
    command: str
    param: Optional[Any] = None
    callback: bool = False
    await_completion: bool = False
    context: Optional[str] = None
    command_id: Optional[str] = None

    def to_wire(self) -> str:
        payload = f"{self.node_id} {self.command}".strip()
        if self.param is not None and str(self.param):
            payload = f"{payload} {self.param}"
        return f"{payload}\r\n"


@dataclass
class SleepCommand:
    duration: float

class CommunicationManager:
    IDLE_POLL_MIN_SECONDS = 0.5
    IDLE_POLL_MAX_SECONDS = 2.0
    IDLE_POLL_BACKOFF_FACTOR = 2.0
    MAX_CONSECUTIVE_FAILURES = 3

    def __init__(self, parent, logger):
        self.logger = logger
        self.threadpool: Optional[QThreadPool] = QThreadPool.globalInstance()
        self.port = None
        self.baudrate = None
        self.parent = parent
        self.connection = None
        self._alive = False
        self._command_queue: Queue = Queue()
        self._stop_token = object()
        self._transport = SerialTransport(self.logger)
        self.node_id = "0"
        self._worker: Optional[Worker] = None
        self.polling_callback = None
        self.logging_callback = None
        self.in_motion = False
        self.signals = MySignal()
        self._idle_poll_interval = self.IDLE_POLL_MIN_SECONDS
        self._idle_poll_idle_streak = 0
        self._consecutive_failures = 0
        self._connection_failure_notified = False
        self._polling_enabled = False
        self._worker_running = False
        self._command_counter = 0

    def setup_connection(self):
        while True:
            try:
                if self._attempt_connection():
                    if not self._alive:
                        self.setup_thread()
                    self._enqueue_sleep(0.5)
                    return True
            except Exception:  # pragma: no cover - unexpected failure
                self.logger.exception("Serial connection initialization encountered an unexpected error.")
                return False

            if not self._prompt_retry():
                self.logger.error("User chose not to retry serial connection; aborting.")
                return False

    def _attempt_connection(self) -> bool:
        if not self.port:
            self.logger.error("Serial port not specified.")
            return False

        try:
            connection = self._transport.open(port=self.port, baudrate=self.baudrate)
        except serial.SerialException as exc:
            self.logger.exception("Failed to connect to %s: %s", self.port, exc)
            return False

        self.connection = connection
        self._consecutive_failures = 0
        self._connection_failure_notified = False
        return True

    def _prompt_retry(self) -> bool:
        err = QMessageBox.warning(
            self.parent,
            "No connection",
            "Unable to connect to the controller. Try again?\n"
            "Selecting 'No' will exit the program.",
            QMessageBox.Yes | QMessageBox.No,
        )
        return err == QMessageBox.Yes

    def _enqueue_sleep(self, duration: float) -> None:
        """Queue a sleep command for the worker thread to absorb post-connect delays."""
        self._command_queue.put(SleepCommand(duration))

    def setup_thread(self):
        if self._alive:
            return
        if self.threadpool is None:
            self.threadpool = QThreadPool.globalInstance()
        worker_0 = Worker(self.transmit)
        worker_0.signals.finished.connect(self._on_worker_finished)
        # worker_1 = Worker(self.send_cmd)
        self._alive = True
        self._worker = worker_0
        self._worker_running = True
        self.threadpool.start(worker_0)
        # self.threadpool.start(worker_1)

    def close(self, *, wait: bool = True, timeout_ms: int = 2000) -> None:
        self._alive = False
        self._command_queue.put(self._stop_token)
        self._transport.close()
        self.connection = None
        self._consecutive_failures = 0
        self._polling_enabled = False
        self._worker_running = False
        if wait and self.threadpool and self._worker:
            if not self.threadpool.waitForDone(timeout_ms):
                self.logger.warning("Serial worker did not exit within %sms.", timeout_ms)
        self._worker = None

    def transmit_queue(
        self,
        node_id,
        cmd,
        param=None,
        *,
        callback=False,
        await_completion=False,
        context=None,
    ) -> Optional[str]:
        if not self.is_worker_alive():
            self.logger.error("Serial worker is not running; cannot queue command.")
            self._handle_connection_failure("Worker thread not running")
            return None
        if cmd is None:
            self.logger.error("Communication command not specified")
            return None
        command_text = str(cmd).strip()
        lower_text = command_text.lower()
        if lower_text.startswith("sleep"):
            duration = None
            if param is not None:
                duration = param
            else:
                parts = command_text.split()
                if len(parts) > 1:
                    duration = parts[1]
            try:
                duration_value = float(duration) if duration is not None else 0.0
            except (TypeError, ValueError):
                self.logger.warning("Invalid sleep command duration: %s", duration)
            else:
                self._command_queue.put(SleepCommand(duration_value))
            return None
        command_id = self._next_command_id()
        serial_command = SerialCommand(
            node_id=str(node_id),
            command=command_text,
            param=param if param is None else str(param),
            callback=callback,
            await_completion=await_completion,
            context=context,
            command_id=command_id,
        )
        self._command_queue.put(serial_command)
        return command_id

    def transmit(self):
        while True:
            try:
                item = self._command_queue.get(timeout=self._idle_poll_interval)
            except Empty:
                if not self._alive:
                    break
                self._poll_idle()
                continue

            if item is self._stop_token:
                break

            try:
                self._record_activity()
                if isinstance(item, SleepCommand):
                    sleep(max(0.0, item.duration))
                    continue
                if isinstance(item, SerialCommand):
                    response = self._process_serial_command(item)
                    if item.callback and not item.await_completion and response is not None:
                        self.signals.main_thread.emit(response)
            except serial.SerialException as exc:
                self.logger.exception("Serial communication failure: %s", exc)
                if isinstance(item, SerialCommand):
                    self._emit_command_status(item.command_id, "Failed")
                self._handle_connection_failure(str(exc))
            except Exception:
                self.logger.exception("Unexpected error while processing serial command.")
                if isinstance(item, SerialCommand):
                    self._emit_command_status(item.command_id, "Failed")
                self._handle_connection_failure("Unexpected serial error")

    def _on_worker_finished(self) -> None:
        if not self._alive:
            return
        self._alive = False
        self._worker = None
        self._worker_running = False
        self._handle_connection_failure("Worker thread died unexpectedly")

    def is_worker_alive(self) -> bool:
        return self._alive and self._worker is not None and self._worker_running

    def _record_failure(self, reason: str) -> None:
        self._consecutive_failures += 1
        if self._consecutive_failures >= self.MAX_CONSECUTIVE_FAILURES:
            self._handle_connection_failure(reason)

    def _reset_failures(self) -> None:
        self._consecutive_failures = 0

    def _drain_command_queue(self) -> int:
        dropped_count = 0
        preserved_stop = False
        while not self._command_queue.empty():
            try:
                item = self._command_queue.get_nowait()
            except Empty:
                break
            if item is self._stop_token:
                preserved_stop = True
                continue
            dropped_count += 1
        if preserved_stop:
            self._command_queue.put(self._stop_token)
        return dropped_count

    def _handle_connection_failure(self, reason: str) -> None:
        """Invalidate connection and notify UI of failure."""
        self.logger.error("Connection lost: %s", reason)
        self._transport.close()
        self.connection = None
        self._consecutive_failures = 0
        self._polling_enabled = False

        dropped_count = self._drain_command_queue()
        if dropped_count > 0:
            self.logger.warning("Dropped %d pending commands due to connection loss", dropped_count)

        if not self._connection_failure_notified:
            self.signals.connection_lost.emit(reason)
            self._connection_failure_notified = True

    def _emit_command_status(self, command_id: Optional[str], status: str) -> None:
        if command_id:
            self.signals.command_status.emit(command_id, status)

    def _next_command_id(self) -> str:
        self._command_counter += 1
        return str(self._command_counter)

    def _record_activity(self) -> None:
        self._idle_poll_idle_streak = 0
        self._idle_poll_interval = self.IDLE_POLL_MIN_SECONDS

    def _backoff_idle_poll(self) -> None:
        self._idle_poll_idle_streak += 1
        interval = self.IDLE_POLL_MIN_SECONDS * (self.IDLE_POLL_BACKOFF_FACTOR ** self._idle_poll_idle_streak)
        self._idle_poll_interval = min(self.IDLE_POLL_MAX_SECONDS, interval)

    def _process_serial_command(self, command: SerialCommand) -> Optional[str]:
        if not self.connection:
            self.logger.warning("Serial connection not available; skipping command %s", command.command)
            return None
        if not self.connection.is_open:
            self.logger.warning("Serial connection closed; skipping command %s", command.command)
            self._handle_connection_failure("Connection closed unexpectedly")
            return None
        self.node_id = command.node_id
        message = command.to_wire()
        try:
            self._transport.write(message)
            self._emit_command_status(command.command_id, "Sent")
            response = self._transport.read_line()
        except serial.SerialException as exc:
            self._record_failure(f"Serial error: {exc}")
            raise

        if response:
            self._reset_failures()
        else:
            self._record_failure("No response from device")

        if response:
            self.signals.log.emit(response)

        status = self._update_motion_state(command.await_completion)
        if command.await_completion:
            self.signals.command_complete.emit(command, status)
        if command.callback and command.await_completion and response is not None:
            self.signals.main_thread.emit(response)
        return response

    def _update_motion_state(self, await_completion: bool) -> Optional[str]:
        last_status: Optional[str] = None
        try:
            last_status = self.check_status()
            while self.in_motion:
                if not await_completion and not self._command_queue.empty():
                    break
                last_status = self.check_status()
                self.poll()
        except serial.SerialException as exc:
            self.logger.exception("Serial error while updating motion state: %s", exc)
        except Exception:
            self.logger.exception("Unexpected error while polling motion state.")
        finally:
            self.poll()
        return last_status

    def _poll_idle(self) -> None:
        if not self.connection or not self._polling_enabled:
            return
        if not self.connection.is_open:
            self._handle_connection_failure("Connection closed unexpectedly")
            return
        try:
            status = self.check_status()
            if not status:
                self._record_failure("Device not responding to status request")
                return
            self._reset_failures()
            if self.in_motion:
                self._record_activity()
            else:
                self._backoff_idle_poll()
        except serial.SerialException as exc:
            self.logger.exception("Serial error while polling idle status: %s", exc)

    def poll(self):
        if not self.connection or not self._polling_enabled:
            return
        if not self.connection.is_open:
            self._handle_connection_failure("Connection closed unexpectedly")
            return
        try:
            self._transport.write(f"{self.node_id} {CMD_POSITION}\r\n")
            pos = self._transport.read_line()
        except serial.SerialException as exc:
            self.logger.exception("Failed to poll node %s position: %s", self.node_id, exc)
            return

        if pos:
            self.signals.poll.emit(self.node_id, pos)

    def check_status(self) -> Optional[str]:
        if not self.connection:
            return None
        if not self.connection.is_open:
            self._handle_connection_failure("Connection closed unexpectedly")
            return None

        try:
            self._transport.write(f"{self.node_id} {CMD_STATUS}\r\n")
            status = self._transport.read_line()
        except serial.SerialException as exc:
            self.logger.exception("Failed to check status for node %s: %s", self.node_id, exc)
            return None

        if not status:
            self._record_failure("Device not responding to status request")
            return None
        self._reset_failures()

        try:
            ascii_value = ord(status[0])
            self.in_motion = bool(0x01 & ascii_value)
        except Exception:
            self.logger.exception("Unable to parse status response '%s' for node %s", status, self.node_id)
        return status

    def enable_polling(self) -> None:
        self._polling_enabled = True
