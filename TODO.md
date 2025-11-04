# TODO

## mc_desktop/communication.py
- Replace the busy-loop in `transmit` with a blocking queue read (e.g., `Queue.get(timeout=...)`) so the worker thread sleeps while idle and you can send a sentinel for shutdown.
- Short-circuit `_attempt_connection` on `SerialException` instead of continuing with `self.connection` unset; let the caller decide about retries before spawning worker threads.
- Route all error/diagnostic messages through the logger or Qt signals—remove ad-hoc `print` calls from the worker path to keep telemetry consistent.
- Move the post-open `sleep(.5)` off the UI thread (e.g., into the worker via `QThread.msleep` or a single-shot timer) to avoid blocking the interface.
- Extract the serial transport concerns into a dedicated adapter class; this allows characterization testing of protocol handling without pulling in Qt.
