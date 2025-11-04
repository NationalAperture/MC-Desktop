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

## Build
Create a source and wheel distribution using the project’s `pyproject.toml`:
```bash
uv tool install --upgrade build
uv run python -m build
```
The artifacts will appear in the `dist/` directory.

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
