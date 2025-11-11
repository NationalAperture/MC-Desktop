# MC Desktop

Desktop control panel for MC hardware built with PySide6.

## Prerequisites
- Python 3.13 or newer
- [uv](https://github.com/astral-sh/uv) CLI (handles virtualenvs and installs)
- Qt runtime provided by `PySide6` (pulled in via `uv pip`)

## Setup
```bash
uv venv
source .venv/bin/activate  # On Windows use: .venv\Scripts\activate
uv pip install -e .
```

## Run
Launch the Qt UI after activating the virtual environment:
```bash
uv run python -m mc_desktop
```

### Edit UI in Qt Creator
1. Launch Qt Creator and open `mc_desktop/ui/designer/application.pyproject`.
2. Modify any of the `.ui` forms located in `mc_desktop/ui/designer/`.
3. Regenerate the Python form classes so the app picks up your UI changes:
```bash
source .venv/bin/activate  # Windows: .venv\Scripts\activate
uv run python scripts/generate_ui.py
```
The regenerated files land in `mc_desktop/ui/forms/`; never edit them by hand because they are overwritten each time.

## Test
Characterization tests ensure the refactor remains stable:
```bash
uv run python -m unittest discover tests
```

## PyInstaller Bundles
- Install PyInstaller inside the project environment first: `uv pip install pyinstaller`.
- Use the packaged entry module (`mc_desktop/__main__.py`) so the bundled executable runs `run_app()`.
- Single directory build (creates an `NAI-Mover/` folder containing the executable and supporting files):
  ```bash
  uv run pyinstaller \
    --name NAI-Mover \
    --onedir \
    --windowed \
    --collect-all PySide6 \
    --collect-data mc_desktop.resources \
    --hidden-import serial.tools.list_ports \
    mc_desktop/__main__.py
  ```
- Single file build (packs everything into one executable while still bundling resources at runtime):
  ```bash
  uv run pyinstaller \
    --name NAI-Mover \
    --onefile \
    --windowed \
    --collect-all PySide6 \
    --collect-data mc_desktop.resources \
    --hidden-import serial.tools.list_ports \
    mc_desktop/__main__.py
  ```
- Both commands pull in the Qt plugins bundled with PySide6 and copy everything under `mc_desktop/resources/` (e.g., `.qss` stylesheets). Add extra `--collect-data` flags if you introduce additional resource packages.

## Project Layout
```
mc_desktop/
  app.py               # bootstrap & logging
  communication.py     # serial transport and worker threads
  node_manager.py      # node configuration state
  ui/
    designer/          # source .ui files + Qt Creator project
    forms/             # auto-generated PySide6 wrappers (do not edit)
```

## Macro Execution Flow
- Motion commands queued from the macro UI now opt into completion tracking via the `command_complete` signal emitted by `CommunicationManager` once the axis reports it is stationary.
- `MacroRunner` waits for that completion notification before dispatching the next macro step, ensuring waits and loops only advance after motion finishes.
- Loop constructs (`loop n` … `end`) and `wait` commands are evaluated by `MacroRunner`'s state machine so repeated moves are resent only after the transport confirms completion.


