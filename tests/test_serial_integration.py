import logging

import pytest

from mc_desktop.communication import CommunicationManager, SerialCommand, SerialTransport

serial = pytest.importorskip("serial")


class LoopSerialModule:
    """Provide a loopback serial connection for integration-style tests."""

    def Serial(self, port, baudrate, parity, stopbits, bytesize, timeout):
        return serial.serial_for_url("loop://", baudrate=baudrate, timeout=timeout)


def _build_loopback_transport():
    return SerialTransport(logging.getLogger("test_serial"), serial_module=LoopSerialModule())


def test_serial_transport_loopback_roundtrip():
    transport = _build_loopback_transport()
    transport.open("loop://", 9600, timeout=0.1)

    transport.write("ping\r\n")
    assert transport.read_line() == "ping"

    transport.close()


def test_communication_manager_processes_loopback_command():
    manager = CommunicationManager(parent=object(), logger=logging.getLogger("test_comm"))
    manager._transport = _build_loopback_transport()
    manager.connection = manager._transport.open("loop://", 9600, timeout=0.1)

    response = manager._process_serial_command(
        SerialCommand(node_id="0", command="mov", param="10", callback=True, await_completion=False)
    )

    assert response is not None
    assert "0 mov 10" in response
