# TODO

## Completed
- [x] Trace the macro callback flow to confirm that `CommunicationManager.transmit()` now emits `main_thread` callbacks immediately while completion is handled separately (`mc_desktop/communication.py`).
- [x] Add a dedicated completion signal that fires once `_update_motion_state()` determines the axis is stationary so macro sequencing can wait for the real completion event (`mc_desktop/communication.py`).
- [x] Update macro execution to queue steps until the new completion notification arrives instead of relying on the pre-completion callback (`mc_desktop/ui/controllers.py`).
- [x] Backstop the change with unit tests that simulate motion + idle responses to ensure macros only advance after the completion signal, and cover wait/loop commands (`tests/test_macro_runner.py`).
- [x] Document the updated macro execution flow for future maintenance (`README.md`).

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
- [ ] **Add input validation feedback**: Settings inputs (`set_stage_gh`, `set_kp`, etc.) silently fail on invalid input. Show user-facing error messages or highlight invalid fields.
- [ ] **Confirm before erasing configuration**: `erase_configuration()` in `main_window.py:507` executes immediately. Add a confirmation dialog to prevent accidental data loss.
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

- [ ] **Remove duplicate wrapper methods in MainWindow**: Methods like `set_kp()`, `set_ki()`, `get_stage_values()` at `main_window.py:540-598` are thin wrappers that just call `self.settings.*`. Remove them and connect signals directly to the controller.
- [ ] **Consolidate log_sent_messages and log_received_messages**: As noted in the TODO at `main_window.py:785`, these functions are nearly identical. Refactor into a single method with a "source" parameter.
- [ ] **Add type hints throughout**: `main_window.py` and some controller methods lack type annotations. Add comprehensive type hints for better IDE support and maintainability.
- [ ] **Extract magic strings to constants**: Commands like `"jog"`, `"abm"`, `"mva"` are scattered as string literals. Define them as constants in a dedicated module.
- [ ] **Improve error handling in serial communication**: `_process_serial_command()` catches exceptions but doesn't notify the UI. Emit an error signal to show users when commands fail.
- [ ] **Add connection timeout handling**: `_attempt_connection()` can hang if the port is busy. Add explicit timeout and user feedback.
- [ ] **Refactor callback chain to use signals**: The `callbacks` list pattern in `main_window.py:292,642-691` is fragile. Replace with proper Qt signals/slots or a state machine.
- [ ] **Add proper shutdown handling**: `closeEvent()` calls `serial.close()` but doesn't wait for the worker thread to finish. Use proper thread synchronization.
- [ ] **Validate node_id before operations**: Several methods assume `node_id` is valid. Add guards to prevent crashes when `current_node_id` is None.
- [ ] **Use dataclasses or Pydantic for command parsing**: Macro command parsing in `_dispatch_command()` at `controllers.py:255` uses manual string splitting. Consider structured parsing.
- [ ] **Add retry logic for failed commands**: When serial communication fails, consider automatic retry with exponential backoff.
- [ ] **Improve logging granularity**: Add DEBUG-level logs for serial transactions and WARNING for recoverable errors. Current logging is sparse in some areas.
- [ ] **Add configuration file support**: Allow users to save/load application preferences (baud rate, polling interval, etc.) to a config file.
- [ ] **Implement proper MVC separation**: `MainWindow` still contains significant business logic. Consider moving more logic to controllers.

## Testing Improvements

- [ ] **Add integration tests for serial communication**: Current tests use fakes. Add tests with mock serial device or loopback for realistic testing.
- [ ] **Add UI tests with pytest-qt**: Test button clicks, signal emissions, and UI state changes.
- [ ] **Increase test coverage for NodeSettingsController**: `update_*_values` methods and setters need more test coverage.
- [ ] **Add tests for update checker/downloader**: `updater.py` has no test coverage.
- [ ] **Add tests for edge cases**: Empty node list, invalid serial responses, malformed macro files.
- [ ] **Add performance benchmarks**: Measure and track serial polling latency and UI responsiveness.

## Documentation Improvements

- [x] **Add API documentation**: Document the serial command protocol for the MC-6 controller (`docs/API.md`).
- [x] **Add developer setup guide**: Include instructions for setting up a development environment and running tests (`docs/DEVELOPER.md`).
- [x] **Add architecture diagram**: Visual representation of the component interactions (`docs/ARCHITECTURE.md`).
- [x] **Document macro syntax**: Create a user-facing guide for macro commands (loop, end, sleep, etc.) (`docs/MACRO_SYNTAX.md`).
