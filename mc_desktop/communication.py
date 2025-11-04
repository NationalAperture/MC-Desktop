import sys
import serial
import traceback
from datetime import datetime
from queue import Queue
from PySide6.QtCore import QRunnable, Signal, Slot, QObject, QThreadPool
from PySide6.QtWidgets import QMessageBox
from time import sleep


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

class CommunicationManager:
    def __init__(self, parent, logger):
        self.logger = logger
        self.threadpool = None
        self.port = None
        self.baudrate = None
        # self.stack = LifoQueue()
        self.parent = parent
        self.connection = None
        self.callback = False
        self._alive = False
        self.send_queue = Queue()
        self.node_id = "0"
        self.polling_callback = None
        self.logging_callback = None
        self.in_motion = False
        self.signals = MySignal()

    def setup_connection(self):
        try:
            self._attempt_connection()
            if not self._alive:
                self.setup_thread()
                self._alive = True

            return True
        except Exception as e:
            self.logger.exception("Serial connection initialization failed: %s", e)
            return False

    def _attempt_connection(self):
        try:
            self.connection = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                bytesize=serial.EIGHTBITS,
                timeout=0.5,
            )
            sleep(.5)
        except serial.SerialException as e:
            self.logger.exception("Failed to connect: %s. Time: %s", e, datetime.now())
            if "Errno 13" in str(e):
                print("bad")

        if not self.connection:
            self._show_connection_error()

    def _show_connection_error(self):
        while not self.connection:
            err = QMessageBox.warning(
                self.parent,
                "No connection",
                "Unable to connect to the controller. Try again?\n"
                "Selecting 'No' will exit the program.",
                QMessageBox.Yes | QMessageBox.No,
            )
            if err == QMessageBox.Yes:
                self._attempt_connection()
            else:
                self.logger.error("Exiting due to failed connection.")
                sys.exit()

    def setup_thread(self):
        self.threadpool = QThreadPool()
        worker_0 = Worker(self.transmit)
        # worker_1 = Worker(self.send_cmd)
        self.threadpool.start(worker_0)
        # self.threadpool.start(worker_1)

    def close(self):
        self._alive = False
        if self.connection:
            self.connection.close()

    def transmit_queue(self, node_id, cmd, param=None, callback=False):
        if cmd is None:
            self.logger.error("Communication command not specified")
            return
        # print(f"nodeId: {nodeId}, cmd: {cmd}, param: {param}, callback: {callback}")
        self.node_id = node_id
        self.callback = callback
        if param is not None:
            # Check if this command needs the param to be converted from mm, inches, etc to encoder counts.
            full_msg = f"{node_id} {cmd} {param}\r\n"
        else:
            full_msg = f"{node_id} {cmd}\r\n"

        self.send_queue.put(full_msg)

    def send_cmd(self, cmd):
        try:
            self.connection.write(cmd.encode())
        except Exception as e:
            print(f"Error in sending message: {e}")

    # ToDo: Fix issue with checking in_motion. If the user sends another command it needs
    def transmit(self):
        while self._alive:
            if self.send_queue.empty():
                # self.poll()
                # self.check_status()
                pass
            else:
                try:
                    recv_msg = ""
                    send_msg = self.send_queue.get()
                    if "sleep" in send_msg:
                        seconds = send_msg.split(" ")[1]
                        sleep(float(seconds))
                    else:
                        self.connection.write(send_msg.encode())
                        recv_msg = self.connection.readline()
                        try:
                            recv_msg = recv_msg.decode().strip()
                        except Exception as e:
                            print(f"Error in receiving message: {e}")
                        #self.connection.readline()
                        self.signals.log.emit(recv_msg)
                        self.check_status()
                        while self.in_motion:
                            if not self.send_queue.empty():
                                break
                            self.check_status()
                            self.poll()

                        self.poll()
                    if self.callback:
                        try:
                            self.signals.main_thread.emit(recv_msg)
                        except Exception as e:
                            print(f"Error in dispatching message: {e}")

                except (serial.SerialException, UnicodeDecodeError) as e:
                    print(f"error unicode: {e}")
                    self.logger.exception("Error sending message: %s", e)
                except serial.Timeout as timeOut:
                    self.logger.exception("Error sending message: %s", timeOut)
                    print(f"Error timeout: {timeOut}")
                except Exception as e:
                    print(f"Error: {e}")
                    self.logger.exception("Error: %s", e)

    def poll(self):
        msg = f"{self.node_id} pos\r\n"
        self.connection.write(msg.encode())
        recv = self.connection.readline().decode().strip()
        # self.connection.readline()
        pos = recv
        if pos:
            self.signals.poll.emit(self.node_id, pos)

    def check_status(self):
        recv_msg = None
        decode_msg = None
        try:
            msg = f"{self.node_id} sts\r\n"
            self.connection.write(msg.encode())
            recv_msg = self.connection.readline()
            decode_msg = recv_msg.decode().strip()
            # self.connection.readline()
        except serial.SerialException as e:
            print(f"Received: {recv_msg}")
            print(f"Error: {e}")
        except UnicodeDecodeError as e:
            print(f"Error unicode: {e}")
            print(f"Message: {recv_msg}")
        if decode_msg == "":
            return
        try:
            ascii_value = ord(decode_msg[0])
            # print(f"Value: {ascii_value}")
            motion = 0x01 & ascii_value
            self.in_motion = motion
        except Exception as e:
            print(f"Error in checking status: {e}")
            print(f"Message: {recv_msg}")