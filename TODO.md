# TODO

## Completed
- [x] Trace the macro callback flow to confirm that `CommunicationManager.transmit()` now emits `main_thread` callbacks immediately while completion is handled separately (`mc_desktop/communication.py`).
- [x] Add a dedicated completion signal that fires once `_update_motion_state()` determines the axis is stationary so macro sequencing can wait for the real completion event (`mc_desktop/communication.py`).
- [x] Update macro execution to queue steps until the new completion notification arrives instead of relying on the pre-completion callback (`mc_desktop/ui/controllers.py`).
- [x] Backstop the change with unit tests that simulate motion + idle responses to ensure macros only advance after the completion signal, and cover wait/loop commands (`tests/test_macro_runner.py`).
- [x] Document the updated macro execution flow for future maintenance (`README.md`).

---

## Bug Fixes (High Priority)

- [x] **Defer idle polling until a node is added**: After opening the serial port, `_poll_idle()` is called within 0.5s using the default `node_id="0"`, but no node has been added yet. This causes status polling to fail immediately on connection.

  **Root Cause**: `setup_connection()` starts the worker thread which begins the `transmit()` loop. After the first queue timeout (0.5s), `_poll_idle()` calls `check_status()` with `node_id="0"` - a node that doesn't exist on the device.

  **Proposed Fix**:
  1. Add `_polling_enabled: bool = False` flag to `CommunicationManager.__init__()`
  2. In `_poll_idle()` and `poll()`, return early if `not self._polling_enabled`
  3. Add `enable_polling()` method that sets `_polling_enabled = True`
  4. Call `serial.enable_polling()` from `MainWindow.add_node()` when the first node is added

  **Alternative**: Check `self.parent.node_manager.has_nodes()` in `_poll_idle()` before polling, but this adds coupling between CommunicationManager and NodeManager.

  **Files**: `mc_desktop/communication.py` (lines 137, 380-398), `mc_desktop/ui/main_window.py` (line 763)

- [x] **Lazy restart worker thread on demand**: The worker thread dies after extended inactivity (QThreadPool expiry). Allow this to happen silently and restart the thread when a new command is queued.

  **Symptoms**: Commands appear in communication table but never transmit after long idle period.

  **Implementation Steps**:
  1. Add `_worker_running: bool = False` flag to `CommunicationManager.__init__()`
  2. Connect `worker.signals.finished` to `_on_worker_finished()` in `setup_thread()`
  3. In `_on_worker_finished()`:
     - Set `_worker_running = False`
     - Log at DEBUG level: "Worker thread exited (idle timeout)"
     - Do NOT emit error signals (this is expected behavior)
  4. In `transmit_queue()`, before adding to queue:
     - Check `if not self._worker_running and self.connection:`
     - If worker is dead but connection exists, call `_restart_worker()`
  5. Add `_restart_worker()` method:
     - Create new Worker with `transmit` function
     - Set `_worker_running = True`
     - Start worker via `threadpool.start()`
     - Log: "Worker thread restarted"
  6. Update `setup_thread()` to set `_worker_running = True`
  7. Update `close()` to set `_worker_running = False`

  **Files**: `mc_desktop/communication.py` (lines 126-147, 195-206, 218-248)

- [ ] **Log commands after transmission, not before**: Commands are logged to the communication table in controllers BEFORE being queued, so failed/discarded commands still appear as "sent".

  **Proposed Fix**:
  1. Add a `command_sent` signal that fires after successful `_transport.write()`
  2. Move `log_sent_messages()` calls to respond to this signal
  3. Or add a "Status" column to the table showing Queued/Sent/Failed

  **Files**: `mc_desktop/ui/controllers.py` (lines 188, 344), `mc_desktop/communication.py`

---

## Bug Fixes: Updater

- [ ] **Windows updater closes and reopens but does not apply update**: The batch script update mechanism fails to replace the executable, causing the old version to restart.

  **Root Cause Analysis**:
  The Windows update uses a batch script (`_build_windows_update_script`) that:
  1. Waits for the process to exit via `tasklist`
  2. Waits only 1 second after process disappears
  3. Attempts `move /y` to replace the executable
  4. If move succeeds, starts the new exe; if it fails, exits silently

  **Likely Failure Points**:
  1. **Insufficient wait time**: Windows often holds file locks for several seconds after a process exits. The 1-second wait is not enough.
  2. **Silent failure**: When `move` fails, the script exits without any user feedback or logging.
  3. **No retry mechanism**: If the move fails due to a temporary lock, there's no retry logic.
  4. **Permission issues**: If installed in Program Files, `move` requires elevation (UAC).
  5. **Antivirus interference**: AV software may hold locks on the downloaded file or block the move operation.
  6. **No verification**: The script doesn't verify the move actually succeeded before restarting.

  **Implementation Steps**:
  1. **Increase wait time and add retry loop** in `_build_windows_update_script()`:
     - After detecting process exit, wait 2-3 seconds instead of 1
     - Add a retry loop (3-5 attempts) with increasing delays for the `move` command
     - Example: try move, if fails wait 2 seconds, retry up to 5 times

  2. **Add move verification**:
     - After `move`, check if the file exists at the destination
     - Compare file sizes or use `fc` to verify the new file is in place

  3. **Add logging to batch script**:
     - Write status messages to a log file in temp directory (e.g., `%TEMP%\nai_mover_update.log`)
     - Log each step: waiting for exit, attempting move, move result, starting app
     - On failure, log the error before exiting

  4. **Add user feedback on failure**:
     - If all move retries fail, show a message box using `msg` command or create an error file
     - Consider emitting a signal from Python to show dialog if update fails

  5. **Handle UAC/permissions**:
     - Detect if running from protected directory (Program Files)
     - If so, either request elevation or warn user before attempting update
     - Alternative: download to user-writable location and update from there

  6. **Updated batch script template**:
     ```batch
     @echo off
     set LOGFILE=%TEMP%\nai_mover_update.log
     echo [%DATE% %TIME%] Update script started >> "%LOGFILE%"

     :wait_loop
     tasklist /fi "imagename eq {exe_name}" 2>nul | find /i "{exe_name}" >nul
     if not errorlevel 1 (
         timeout /t 1 /nobreak >nul
         goto wait_loop
     )
     echo [%DATE% %TIME%] Process exited >> "%LOGFILE%"
     timeout /t 3 /nobreak >nul

     set RETRIES=0
     :move_retry
     echo [%DATE% %TIME%] Move attempt %RETRIES% >> "%LOGFILE%"
     move /y "{download_path}" "{current_exe}" >> "%LOGFILE%" 2>&1
     if errorlevel 1 (
         set /a RETRIES+=1
         if %RETRIES% lss 5 (
             echo [%DATE% %TIME%] Move failed, retrying... >> "%LOGFILE%"
             timeout /t 2 /nobreak >nul
             goto move_retry
         )
         echo [%DATE% %TIME%] Move failed after 5 attempts >> "%LOGFILE%"
         exit /b 1
     )

     echo [%DATE% %TIME%] Move succeeded, starting app >> "%LOGFILE%"
     start "" "{current_exe}"
     del "%~f0"
     ```

  7. **Add Python-side verification** (optional enhancement):
     - On app startup, check for update log file
     - If log shows failure, notify user that update failed
     - Clean up log file after reading

  **Files**: `mc_desktop/updater.py` (lines 254-299, `_install_windows` and `_build_windows_update_script`)

---

## Performance Improvements

- [x] **Reduce serial polling frequency**: The `_poll_idle()` method in `communication.py:288` polls status every 0.5s during idle. Consider making this configurable or adaptive based on activity.
- [ ] **Batch status and position queries**: `check_status()` and `poll()` make separate serial calls. Combine into a single request if the device protocol supports it to reduce serial traffic.
- [x] **Lazy-load UI forms**: `Connection`, `MotorStats`, `RecordBus` import their UI forms inside `__init__`. Move imports to module level for faster subsequent instantiation.
- [x] **Throttle position updates**: `update_node_motor_values()` in `main_window.py:694` updates the UI on every poll. Add a debounce/throttle to reduce unnecessary repaints during rapid motion.
- [x] **Use QThreadPool max thread count**: `CommunicationManager` creates its own `QThreadPool` but doesn't configure thread limits. Consider reusing `QThreadPool.globalInstance()` or setting appropriate limits.
- [x] **Cache stylesheet**: `_apply_stylesheet()` in `app.py:47` reads the QSS file on every launch. Consider caching or embedding the stylesheet as a Python string constant.
- [x] **Limit com_bus_table row count**: `log_sent_messages()` and `log_received_messages()` insert rows indefinitely into the table widget. Add a max row limit to prevent memory growth during long sessions.

## UI/UX Improvements

- [x] **Add keyboard shortcuts for jog controls**: The TODO comment at `main_window.py:267` mentions arrow key bindings for jog. Implement left/right arrow keys for backward/forward jogging.
- [ ] **Add emergency stop keyboard shortcut**: Bind Escape or Space to the stop command for quick access during operation.
- [x] **Show connection status indicator**: Add a visual indicator (LED icon or status bar text) showing whether the serial connection is active.
- [x] **Add input validation feedback**: Settings inputs (`set_stage_gh`, `set_kp`, etc.) silently fail on invalid input. Show user-facing error messages or highlight invalid fields.
- [x] **Confirm before erasing configuration**: `erase_configuration()` in `main_window.py:507` executes immediately. Add a confirmation dialog to prevent accidental data loss.
- [ ] **Improve macro editor UX**: Add line numbers, syntax highlighting for commands, and error indicators for malformed macro lines.
- [x] **Add macro execution progress indicator**: Show which step is currently executing and overall progress (e.g., "Step 3/10" or a progress bar).
- [x] **Add macro pause/resume functionality**: Allow users to pause a running macro and resume later instead of only stop.
- [ ] **Disable controls during macro execution**: Prevent conflicting manual commands while a macro is running by disabling jog/move buttons.
- [ ] **Remember last used serial port**: Store the last successfully connected port in QSettings and pre-select it on next launch.
- [ ] **Add "Refresh All" button for settings**: Instead of separate refresh buttons for Stage/PID/Motion/Advanced, add a single button to refresh all node parameters.
- [x] **Improve update dialog**: Add "What's New" section expandable/collapsible, and show download size before starting.
- [ ] **Add dark/light theme toggle**: Currently uses a fixed gold theme. Allow users to switch themes or follow system preference.
- [ ] **Add position history graph**: Display a real-time graph of position over time for visual motion monitoring.
- [ ] **Improve port list display**: Show device descriptions in the port list (e.g., "COM3 - USB Serial Device") instead of just port names.

## Code Implementation Improvements

- [x] **Remove duplicate wrapper methods in MainWindow**: Methods like `set_kp()`, `set_ki()`, `get_stage_values()` at `main_window.py:540-598` are thin wrappers that just call `self.settings.*`. Remove them and connect signals directly to the controller.
- [ ] **Consolidate log_sent_messages and log_received_messages**: As noted in the TODO at `main_window.py:785`, these functions are nearly identical. Refactor into a single method with a "source" parameter.
- [x] **Add type hints throughout**: `main_window.py` and some controller methods lack type annotations. Add comprehensive type hints for better IDE support and maintainability.
- [x] **Extract magic strings to constants**: Commands like `"jog"`, `"abm"`, `"mva"` are scattered as string literals. Define them as constants in a dedicated module.
- [ ] **Improve error handling in serial communication**: `_process_serial_command()` catches exceptions but doesn't notify the UI. Emit an error signal to show users when commands fail.
- [ ] **Add connection timeout handling**: `_attempt_connection()` can hang if the port is busy. Add explicit timeout and user feedback.
- [ ] **Refactor callback chain to use signals**: The `callbacks` list pattern in `main_window.py:292,642-691` is fragile. Replace with proper Qt signals/slots or a state machine.
- [x] **Add proper shutdown handling**: `closeEvent()` calls `serial.close()` but doesn't wait for the worker thread to finish. Use proper thread synchronization.
- [x] **Validate node_id before operations**: Several methods assume `node_id` is valid. Add guards to prevent crashes when `current_node_id` is None.
- [x] **Use dataclasses or Pydantic for command parsing**: Macro command parsing in `_dispatch_command()` at `controllers.py:255` uses manual string splitting. Consider structured parsing.
- [ ] **Add retry logic for failed commands**: When serial communication fails, consider automatic retry with exponential backoff.
- [ ] **Improve logging granularity**: Add DEBUG-level logs for serial transactions and WARNING for recoverable errors. Current logging is sparse in some areas.
- [ ] **Add configuration file support**: Allow users to save/load application preferences (baud rate, polling interval, etc.) to a config file.
- [ ] **Implement proper MVC separation**: `MainWindow` still contains significant business logic. Consider moving more logic to controllers.

## Testing Improvements

- [x] **Add integration tests for serial communication**: Current tests use fakes. Add tests with mock serial device or loopback for realistic testing.
- [x] **Add UI tests with pytest-qt**: Test button clicks, signal emissions, and UI state changes.
- [x] **Increase test coverage for NodeSettingsController**: `update_*_values` methods and setters need more test coverage.
- [x] **Add tests for update checker/downloader**: `updater.py` has no test coverage.
- [x] **Add tests for edge cases**: Empty node list, invalid serial responses, malformed macro files.
- [x] **Add performance benchmarks**: Measure and track serial polling latency and UI responsiveness.

## Documentation Improvements

- [x] **Add API documentation**: Document the serial command protocol for the MC-6 controller (`docs/API.md`).
- [x] **Add developer setup guide**: Include instructions for setting up a development environment and running tests (`docs/DEVELOPER.md`).
- [x] **Add architecture diagram**: Visual representation of the component interactions (`docs/ARCHITECTURE.md`).
- [x] **Document macro syntax**: Create a user-facing guide for macro commands (loop, end, sleep, etc.) (`docs/MACRO_SYNTAX.md`).
