# Changelog

## Unreleased
- refactor `mc_desktop.node_manager` to use structured dataclasses instead of raw dicts, improving data integrity and aligning key casing for UI consumers.
- update Qt main window helpers to respect the new node lifecycle API and handle node add/remove/rename edge cases cleanly.
- add and expand unit tests for the node manager to lock in current behaviour (CSV helpers, pointer updates, lifecycle validation).
- add `scripts/generate_ui.py` for regenerating PySide6 forms after editing `.ui` files, and document the workflow in README.
- reorganize designer assets under `mc_desktop/ui/designer/` so Qt Creator edits stay isolated from generated code.
