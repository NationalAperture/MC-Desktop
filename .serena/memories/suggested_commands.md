# Suggested Commands for MC-Desktop Development

## Environment Setup
```bash
# Create virtual environment and install dependencies
uv venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows
uv pip install -e .
```

## Running the Application
```bash
# Standard run
uv run python -m mc_desktop

# Or after installing
mc-desktop
```

## Testing
```bash
# Run all tests with unittest
uv run python -m unittest discover tests

# Run all tests with pytest (verbose)
uv run python -m pytest tests/ -v

# Run specific test file
uv run python -m pytest tests/test_macro_runner.py -v

# Run benchmarks
uv run python -m pytest tests/benchmarks/ -v
```

## UI Development
```bash
# Regenerate Python UI classes from .ui files
# Run this after editing .ui files in Qt Creator
uv run python scripts/generate_ui.py
```

## Building Executables
```bash
# Install PyInstaller first
uv pip install pyinstaller

# One-directory build (for development/testing)
uv run pyinstaller \
  --name NAI-Mover \
  --onedir \
  --windowed \
  --collect-all PySide6 \
  --collect-data mc_desktop.resources \
  --hidden-import mc_desktop.resources \
  --hidden-import serial.tools.list_ports \
  mc_desktop/__main__.py

# One-file build (for distribution)
uv run pyinstaller \
  --name NAI-Mover \
  --onefile \
  --windowed \
  --collect-all PySide6 \
  --collect-data mc_desktop.resources \
  --hidden-import mc_desktop.resources \
  --hidden-import serial.tools.list_ports \
  mc_desktop/__main__.py
```

## Git and Release
```bash
# Standard git commands
git status
git diff
git log --oneline -10

# Create a release (after updating version.py)
git tag vX.Y.Z
git push origin main --tags
```

## Utility Commands (Linux)
```bash
# List files
ls -la

# Find files
find . -name "*.py"

# Search in files
grep -r "pattern" mc_desktop/

# View logs
tail -f logs/info.log
```
