# Serial Communication Silent Failure - Diagnosis and Fixes

## Problem Description

After an extended period of operation, serial communication stops working silently:
- Commands still appear in the communication table (UI shows them as queued)
- No errors are reported to the user
- Device removal doesn't trigger any error notifications
- The system appears functional but commands never reach the device

## Root Cause Analysis

### Primary Cause: Stale Connection Reference

When serial communication fails (device disconnected, USB removed, timeout), the exception is caught and logged but **the connection state is never updated**. The UI continues to believe the connection is valid.

**File:** `mc_desktop/communication.py`, lines 259-262

```python
except serial.SerialException as exc:
    self.logger.exception("Serial communication failure: %s", exc)
except Exception:
    self.logger.exception("Unexpected error while processing serial command.")
# BUG: Loop continues, self.connection remains non-None
# UI has no idea communication failed
```

### Contributing Factors

| Issue | Location | Impact |
|-------|----------|--------|
| Connection object not invalidated on error | `transmit()` lines 259-262 | Stale reference persists |
| No error signal emitted to UI | `transmit()` lines 259-262 | UI unaware of failure |
| Only checks `if not self.connection` | `_process_serial_command()` line 274 | Doesn't verify `is_open` |
| No device removal detection | Throughout | USB unplug goes unnoticed |
| All exception handlers are silent | Multiple locations | Errors logged but not escalated |
| `error` signal defined but never used | `WorkerSignals` line 17 | Error pathway exists but unused |

### Flow of Silent Failure

```
1. Device disconnects (USB unplugged, cable issue, device crash)
       ↓
2. Next serial write/read throws SerialException
       ↓
3. Exception caught in transmit() → logged to file
       ↓
4. self.connection remains non-None (STALE)
       ↓
5. Worker loop continues running
       ↓
6. UI keeps queuing commands (line 274 check passes)
       ↓
7. Each command hits 0.5s timeout waiting for response
       ↓
8. User sees commands in table, no errors, nothing works
```

## Evidence from Code

### 1. Connection Never Invalidated After Error

```python
# communication.py lines 250-262
try:
    self._record_activity()
    if isinstance(item, SleepCommand):
        sleep(max(0.0, item.duration))
        continue
    if isinstance(item, SerialCommand):
        response = self._process_serial_command(item)
        # ...
except serial.SerialException as exc:
    self.logger.exception("Serial communication failure: %s", exc)
    # MISSING: self.connection = None
    # MISSING: self._transport.close()
    # MISSING: self.signals.error.emit(...)
```

### 2. Connection Check Only Tests Object Existence

```python
# communication.py line 274
if not self.connection:  # Only checks if object exists
    self.logger.warning("Serial connection not available...")
    return None
# MISSING: Check self.connection.is_open
```

### 3. Error Signal Exists But Is Never Used

```python
# communication.py line 17
class WorkerSignals(QObject):
    error = Signal(tuple)  # Defined but never emitted in transmit()
```

### 4. Silent Exception Handlers Throughout

```python
# _update_motion_state() lines 301-304
except serial.SerialException as exc:
    self.logger.exception("Serial error while updating motion state: %s", exc)
    # Returns None, caller doesn't know there was an error

# _poll_idle() lines 320-321
except serial.SerialException as exc:
    self.logger.exception("Serial error while polling idle status: %s", exc)
    # Silently returns, no UI notification

# poll() lines 329-331
except serial.SerialException as exc:
    self.logger.exception("Failed to poll node %s position: %s", self.node_id, exc)
    return  # Silent failure

# check_status() lines 343-345
except serial.SerialException as exc:
    self.logger.exception("Failed to check status for node %s: %s", self.node_id, exc)
    return None  # Caller can't distinguish "no status" from "error"
```

## Suggested Fixes

### Fix 1: Add Connection Error Signal and Handler (HIGH PRIORITY)

Add a new signal to notify the UI when communication fails.

**In `MySignal` class (line 22):**
```python
class MySignal(QObject):
    main_thread = Signal(str)
    log = Signal(str)
    poll = Signal(str, str)
    command_complete = Signal(object, object)
    connection_lost = Signal(str)  # NEW: reason for disconnection
```

**In `transmit()` (lines 259-262):**
```python
except serial.SerialException as exc:
    self.logger.exception("Serial communication failure: %s", exc)
    self._handle_connection_failure(str(exc))
except Exception as exc:
    self.logger.exception("Unexpected error while processing serial command.")
    self._handle_connection_failure(str(exc))
```

**Add new method:**
```python
def _handle_connection_failure(self, reason: str) -> None:
    """Invalidate connection and notify UI of failure."""
    self.logger.error("Connection lost: %s", reason)
    self._transport.close()
    self.connection = None
    self.signals.connection_lost.emit(reason)
```

**In MainWindow, connect the signal:**
```python
self.serial.signals.connection_lost.connect(self._on_connection_lost)

def _on_connection_lost(self, reason: str):
    QMessageBox.warning(
        self,
        "Connection Lost",
        f"Serial communication failed: {reason}\n\nPlease reconnect.",
    )
    # Update UI to show disconnected state
    self.connection_widget.set_disconnected()
```

### Fix 2: Add `is_open` Verification (HIGH PRIORITY)

Check that the port is actually open before attempting communication.

**In `_process_serial_command()` (line 274):**
```python
def _process_serial_command(self, command: SerialCommand) -> Optional[str]:
    if not self.connection or not self.connection.is_open:
        self.logger.warning("Serial connection not available; skipping command %s", command.command)
        self._handle_connection_failure("Connection closed unexpectedly")
        return None
    # ... rest of method
```

**In `poll()` (line 324):**
```python
def poll(self):
    if not self.connection or not self.connection.is_open:
        return
    # ... rest of method
```

**In `check_status()` (line 337):**
```python
def check_status(self) -> Optional[str]:
    if not self.connection or not self.connection.is_open:
        return None
    # ... rest of method
```

### Fix 3: Add Connection Health Watchdog (MEDIUM PRIORITY)

Implement periodic connection health checks that run independently of command queue.

```python
def __init__(self, parent, logger):
    # ... existing code ...
    self._consecutive_failures = 0
    self._max_consecutive_failures = 3

def _process_serial_command(self, command: SerialCommand) -> Optional[str]:
    if not self.connection or not self.connection.is_open:
        self._handle_connection_failure("Connection closed")
        return None

    try:
        self.node_id = command.node_id
        message = command.to_wire()
        self._transport.write(message)
        response = self._transport.read_line()
        self._consecutive_failures = 0  # Reset on success
        # ... rest of method
    except serial.SerialException as exc:
        self._consecutive_failures += 1
        if self._consecutive_failures >= self._max_consecutive_failures:
            self._handle_connection_failure(f"Multiple failures: {exc}")
        raise  # Re-raise to be caught by outer handler

def _poll_idle(self) -> None:
    if not self.connection or not self.connection.is_open:
        return
    try:
        status = self.check_status()
        if status is None and self._consecutive_failures > 0:
            self._consecutive_failures += 1
            if self._consecutive_failures >= self._max_consecutive_failures:
                self._handle_connection_failure("Device not responding")
                return
        # ... rest of method
```

### Fix 4: Add Write Verification (MEDIUM PRIORITY)

Verify that bytes were actually written to the serial port.

**In `SerialTransport.write()` (line 78):**
```python
def write(self, payload: str) -> int:
    if not self._connection:
        raise serial.SerialException("Serial connection is not open.")
    if not self._connection.is_open:
        raise serial.SerialException("Serial port was closed.")
    bytes_written = self._connection.write(payload.encode())
    if bytes_written != len(payload.encode()):
        raise serial.SerialException(
            f"Incomplete write: {bytes_written}/{len(payload.encode())} bytes"
        )
    return bytes_written
```

### Fix 5: Queue Drain on Disconnect (LOW PRIORITY)

When connection is lost, drain the queue and notify about failed commands.

```python
def _handle_connection_failure(self, reason: str) -> None:
    """Invalidate connection and notify UI of failure."""
    self.logger.error("Connection lost: %s", reason)
    self._transport.close()
    self.connection = None

    # Drain pending commands
    dropped_count = 0
    while not self._command_queue.empty():
        try:
            item = self._command_queue.get_nowait()
            if item is not self._stop_token:
                dropped_count += 1
        except Empty:
            break

    if dropped_count > 0:
        self.logger.warning("Dropped %d pending commands due to connection loss", dropped_count)

    self.signals.connection_lost.emit(reason)
```

### Fix 6: Device Presence Check (LOW PRIORITY)

On Linux, check if the device file still exists before operations.

```python
import os

def _device_exists(self) -> bool:
    """Check if the serial device file exists (Linux/macOS)."""
    if self.port and os.path.exists(self.port):
        return True
    return False

def _process_serial_command(self, command: SerialCommand) -> Optional[str]:
    if not self._device_exists():
        self._handle_connection_failure(f"Device {self.port} no longer exists")
        return None
    # ... rest of method
```

## Implementation Priority

1. **Fix 1 + Fix 2** - Immediate: Add error signal and `is_open` checks
2. **Fix 3** - Short-term: Add watchdog for consecutive failures
3. **Fix 4 + Fix 5** - Medium-term: Write verification and queue drain
4. **Fix 6** - Optional: Device presence check (Linux-specific)

## Testing the Fix

After implementing fixes, test these scenarios:

1. **USB Disconnect During Operation**
   - Start sending commands
   - Unplug USB device
   - Verify: Error dialog appears, UI shows disconnected state

2. **Device Power Cycle**
   - Connect and send commands
   - Power off the device
   - Verify: Error detected within 3 failed attempts

3. **Long Idle Period**
   - Connect device
   - Wait 10+ minutes without activity
   - Send a command
   - Verify: Either command succeeds or error is properly reported

4. **Rapid Command Queue**
   - Queue 50+ commands
   - Disconnect during processing
   - Verify: Remaining commands are dropped, error shown

---

## Macro-Specific Issue: Infinite Loop on No Response

### Problem Description

The macro system can hang indefinitely if the device stops responding during a motion command. This is separate from (but related to) the connection failure issue.

### Root Cause

In `_update_motion_state()` (lines 292-307):

```python
def _update_motion_state(self, await_completion: bool) -> Optional[str]:
    last_status: Optional[str] = None
    try:
        last_status = self.check_status()
        while self.in_motion:  # <-- Can loop forever!
            if not await_completion and not self._command_queue.empty():
                break
            last_status = self.check_status()
            self.poll()
    # ...
```

And in `check_status()` (lines 336-355):

```python
if not status:
    return None  # Returns None, but in_motion is NOT changed!

# in_motion is only updated when a response IS received:
self.in_motion = bool(0x01 & ascii_value)
```

**The bug:** If `in_motion` is `True` and the device stops responding:
1. `check_status()` times out and returns `None`
2. `self.in_motion` stays `True` (never updated)
3. The `while self.in_motion:` loop continues
4. Each iteration times out (0.5s)
5. Macro hangs forever - `command_complete` signal never emitted

### Impact on Macro Loop

When running a macro with `await_completion=True`:
1. Command is sent, device starts motion
2. `in_motion` is set to `True` from first status check
3. Device becomes unresponsive (USB disconnect, power loss, etc.)
4. `_update_motion_state()` loops infinitely
5. `command_complete` signal is never emitted
6. `MacroRunner.on_command_complete()` is never called
7. Macro appears frozen - no error shown

### Fix for Macro Hang Issue

**Add timeout/retry limit to `_update_motion_state()`:**

```python
def _update_motion_state(self, await_completion: bool) -> Optional[str]:
    MAX_CONSECUTIVE_TIMEOUTS = 5
    consecutive_timeouts = 0
    last_status: Optional[str] = None

    try:
        last_status = self.check_status()
        if last_status is None:
            consecutive_timeouts += 1
        else:
            consecutive_timeouts = 0

        while self.in_motion:
            if not await_completion and not self._command_queue.empty():
                break

            last_status = self.check_status()

            if last_status is None:
                consecutive_timeouts += 1
                if consecutive_timeouts >= MAX_CONSECUTIVE_TIMEOUTS:
                    self.logger.error(
                        "Device not responding after %d attempts, aborting motion wait",
                        MAX_CONSECUTIVE_TIMEOUTS
                    )
                    self.in_motion = False  # Force exit
                    self._handle_connection_failure("Device stopped responding")
                    break
            else:
                consecutive_timeouts = 0

            self.poll()
    except serial.SerialException as exc:
        self.logger.exception("Serial error while updating motion state: %s", exc)
        self.in_motion = False  # Ensure we exit the loop
    except Exception:
        self.logger.exception("Unexpected error while polling motion state.")
        self.in_motion = False  # Ensure we exit the loop
    finally:
        self.poll()
    return last_status
```

**Alternative: Add overall timeout:**

```python
import time

def _update_motion_state(self, await_completion: bool) -> Optional[str]:
    MOTION_TIMEOUT_SECONDS = 300  # 5 minute max wait
    start_time = time.time()
    last_status: Optional[str] = None

    try:
        last_status = self.check_status()
        while self.in_motion:
            if time.time() - start_time > MOTION_TIMEOUT_SECONDS:
                self.logger.error("Motion timeout after %d seconds", MOTION_TIMEOUT_SECONDS)
                self.in_motion = False
                break

            if not await_completion and not self._command_queue.empty():
                break
            last_status = self.check_status()
            self.poll()
    # ... rest of method
```

---

## Additional Recommendations

1. **Add connection status indicator to UI** - Show green/red indicator for connection state

2. **Add reconnect button** - Allow user to attempt reconnection without restarting app

3. **Log rotation** - Ensure exception logs don't fill disk during repeated failures

4. **Timeout configuration** - Consider making the 0.5s timeout configurable for slower devices

5. **Macro abort mechanism** - Ensure users can cancel a stuck macro (the pause button may not work if stuck in `_update_motion_state()`)
