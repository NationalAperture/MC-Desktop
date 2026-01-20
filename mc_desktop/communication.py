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

    def write(self, payload: str) -> None:
        if not self._connection:
            raise serial.SerialException("Serial connection is not open.")
        self._connection.write(payload.encode())

    def read_line(self) -> str:
        if not self._connection:
            raise serial.SerialException("Serial connection is not open.")
        return self._connection.readline().decode(errors="ignore").strip()


@dataclass
class SerialCommand:
    node_id: str
    command: str
    param: Optional[Any] = None
    callback: bool = False
    await_completion: bool = False
    context: Optional[str] = None

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
        # worker_1 = Worker(self.send_cmd)
        self._alive = True
        self._worker = worker_0
        self.threadpool.start(worker_0)
        # self.threadpool.start(worker_1)

    def close(self, *, wait: bool = True, timeout_ms: int = 2000) -> None:
        self._alive = False
        self._command_queue.put(self._stop_token)
        self._transport.close()
        self.connection = None
        if wait and self.threadpool and self._worker:
            if not self.threadpool.waitForDone(timeout_ms):
                self.logger.warning("Serial worker did not exit within %sms.", timeout_ms)

    def transmit_queue(self, node_id, cmd, param=None, *, callback=False, await_completion=False, context=None):
        if cmd is None:
            self.logger.error("Communication command not specified")
            return
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
            return

        serial_command = SerialCommand(
            node_id=str(node_id),
            command=command_text,
            param=param if param is None else str(param),
            callback=callback,
            await_completion=await_completion,
            context=context,
        )
        self._command_queue.put(serial_command)

    def send_cmd(self, cmd):
        try:
            self._transport.write(cmd)
        except Exception as e:
            self.logger.exception("Error sending raw command: %s", e)

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
            except Exception:
                self.logger.exception("Unexpected error while processing serial command.")

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
        self.node_id = command.node_id
        message = command.to_wire()
        self._transport.write(message)
        response = self._transport.read_line()

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
        if not self.connection:
            return
        try:
            status = self.check_status()
            if not status:
                return
            if self.in_motion:
                self._record_activity()
            else:
                self._backoff_idle_poll()
        except serial.SerialException as exc:
            self.logger.exception("Serial error while polling idle status: %s", exc)

    def poll(self):
        if not self.connection:
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

        try:
            self._transport.write(f"{self.node_id} {CMD_STATUS}\r\n")
            status = self._transport.read_line()
        except serial.SerialException as exc:
            self.logger.exception("Failed to check status for node %s: %s", self.node_id, exc)
            return None

        if not status:
            return None

        try:
            ascii_value = ord(status[0])
            self.in_motion = bool(0x01 & ascii_value)
        except Exception:
            self.logger.exception("Unable to parse status response '%s' for node %s", status, self.node_id)
        return status
