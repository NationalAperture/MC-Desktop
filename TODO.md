# TODO

- [x] Trace the macro callback flow to confirm that `CommunicationManager.transmit()` now emits `main_thread` callbacks immediately while completion is handled separately (`mc_desktop/communication.py`).
- [x] Add a dedicated completion signal that fires once `_update_motion_state()` determines the axis is stationary so macro sequencing can wait for the real completion event (`mc_desktop/communication.py`).
- [x] Update macro execution to queue steps until the new completion notification arrives instead of relying on the pre-completion callback (`mc_desktop/ui/controllers.py`).
- [x] Backstop the change with unit tests that simulate motion + idle responses to ensure macros only advance after the completion signal, and cover wait/loop commands (`tests/test_macro_runner.py`).
- [x] Document the updated macro execution flow for future maintenance (`README.md`).
