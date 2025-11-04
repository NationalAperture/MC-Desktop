# MC Desktop

Desktop control panel for MC hardware built with PySide6.

## Prerequisites
- Python 3.13 or newer
- Qt dependencies provided by `PySide6` (installed automatically via `pip`)

## Setup
```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows use: .venv\Scripts\activate
pip install --upgrade pip
pip install -e .
```

## Run
Launch the Qt UI after activating the virtual environment:
```bash
python -m mc_desktop
```

### Update UI Forms
After modifying any `.ui` file in `mc_desktop/ui/designer/` via Qt Creator, regenerate the Python form classes:
```bash
source .venv/bin/activate  # Windows: .venv\Scripts\activate
python scripts/generate_ui.py
```

## Test
Characterization tests ensure the refactor remains stable:
```bash
python -m unittest discover tests
```

## Build
Create a source and wheel distribution using the project’s `pyproject.toml`:
```bash
pip install --upgrade build
python -m build
```
The artifacts will appear in the `dist/` directory.
