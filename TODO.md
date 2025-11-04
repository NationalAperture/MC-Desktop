# TODO

## mc_desktop/communication.py
- Replace the busy-loop in `transmit` with a blocking queue read (e.g., `Queue.get(timeout=...)`) so the worker thread sleeps while idle and you can send a sentinel for shutdown.
- Short-circuit `_attempt_connection` on `SerialException` instead of continuing with `self.connection` unset; let the caller decide about retries before spawning worker threads.
- Route all error/diagnostic messages through the logger or Qt signals—remove ad-hoc `print` calls from the worker path to keep telemetry consistent.
- Move the post-open `sleep(.5)` off the UI thread (e.g., into the worker via `QThread.msleep` or a single-shot timer) to avoid blocking the interface.
- Extract the serial transport concerns into a dedicated adapter class; this allows characterization testing of protocol handling without pulling in Qt.

## mc_desktop/node_manager.py
- Normalize dictionary keys (`"Jog"` vs `"jog"`) or, better, replace the nested dicts with dataclasses/TypedDicts so shape mismatches are caught in development and consumers get typed accessors.
- Replace manual string concatenation in the various `get_*_values` helpers with `",".join(...)` or return structured collections, leaving formatting to the caller.
- Have `update_node_id` validate that `current_node_id` exists before mutating state and return a boolean result so the UI can surface failures instead of swallowing `KeyError`.
- Rework `remove_node` to delete by explicit node ID instead of relying on dict ordering derived from `keys()`, or adopt an ordered data structure.
- Consider consolidating per-node configuration into a single data container (dataclass) that holds config/stage/pid/motion/advanced data, enabling validation, sensible defaults, and slimmer accessor APIs.
