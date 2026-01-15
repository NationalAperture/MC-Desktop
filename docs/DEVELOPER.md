# Developer Setup Guide

This guide provides instructions for setting up a development environment for MC-Desktop (NAI-Mover).

## Prerequisites

### Required Software

| Software | Version | Purpose |
|----------|---------|---------|
| Python | 3.13+ | Runtime environment |
| uv | Latest | Package and virtualenv management |
| Git | Latest | Version control |

### Optional Software

| Software | Purpose |
|----------|---------|
| Qt Creator | Visual UI design (editing .ui files) |
| PyCharm / VS Code | IDE with Python support |
| PyInstaller | Building standalone executables |

## Initial Setup

### 1. Clone the Repository

```bash
git clone https://github.com/NationalAperture/MC-Desktop.git
cd MC-Desktop
```

### 2. Install uv (if not already installed)

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Or via pip
pip install uv
```

### 3. Create Virtual Environment and Install Dependencies

```bash
uv venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows

uv pip install -e .
```

This installs the project in editable mode with all dependencies:
- `PySide6` - Qt6 GUI framework
- `pyserial` - Serial port communication
- `packaging` - Version comparison utilities
- `pyinstaller` - Executable bundling (optional)

### 4. Verify Installation

```bash
uv run python -m mc_desktop
```

The application window should appear.

## Project Structure

```
MC-Desktop/
├── mc_desktop/                 # Main package
│   ├── __init__.py
│   ├── __main__.py            # Entry point for python -m
│   ├── app.py                 # Application bootstrap
│   ├── communication.py       # Serial communication layer
│   ├── node_manager.py        # Node state management
│   ├── updater.py             # Auto-update functionality
│   ├── version.py             # Version string
│   ├── resources/             # Static assets
│   │   └── Diffnes-Gold.qss   # Qt stylesheet
│   └── ui/                    # User interface
│       ├── controllers.py     # UI logic controllers
│       ├── main_window.py     # Main window implementation
│       ├── update_dialog.py   # Update dialog
│       ├── designer/          # Qt Designer .ui files
│       └── forms/             # Auto-generated Python UI classes
├── tests/                     # Unit tests
├── docs/                      # Documentation
├── scripts/                   # Utility scripts
│   └── generate_ui.py         # UI regeneration script
├── pyproject.toml             # Project configuration
├── README.md
└── TODO.md
```

## Development Workflow

### Running the Application

```bash
# Standard run
uv run python -m mc_desktop

# Or after installing
mc-desktop
```

### Running Tests

```bash
# Run all tests
uv run python -m unittest discover tests

# Run specific test file
uv run python -m pytest tests/test_macro_runner.py

# Run with verbose output
uv run python -m pytest tests/ -v
```

### Code Style

The project follows standard Python conventions:
- PEP 8 for code style
- Type hints encouraged (see `controllers.py` for examples)
- Docstrings for public methods

### Editing UI Files

1. **Open Qt Creator** and load `mc_desktop/ui/designer/application.pyproject`

2. **Edit the .ui files** in the designer:
   - `form.ui` - Main application window
   - `connection_form.ui` - Serial connection dialog
   - `motor_stats.ui` - Motor status widget
   - `record_bus.ui` - Bus recording dialog
   - `record_system.ui` - System recording dialog

3. **Regenerate Python classes**:
   ```bash
   uv run python scripts/generate_ui.py
   ```

   This runs `pyside6-uic` on each .ui file and outputs to `mc_desktop/ui/forms/`.

4. **Important**: Never edit files in `mc_desktop/ui/forms/` directly - they are overwritten on regeneration.

### Adding New Dependencies

```bash
# Add to pyproject.toml manually, then:
uv pip install -e .

# Or use uv directly
uv pip install <package-name>
# Then add to pyproject.toml
```

## Testing Guide

### Test Structure

```
tests/
├── test_app.py              # Application bootstrap tests
├── test_node_manager.py     # Node state management tests
├── test_macro_runner.py     # Macro execution tests
└── test_ui_controllers.py   # Controller unit tests
```

### Writing Tests

Tests use Python's `unittest` framework with pytest compatibility:

```python
# Example test with fake objects (preferred pattern)
from mc_desktop.ui.controllers import MacroRunner

class FakeWindow:
    def __init__(self):
        self.serial = FakeSerial()
        self.macro_text = FakeTextEdit()

    def log_sent_messages(self, msg):
        pass

def test_macro_runner_executes_commands():
    window = FakeWindow()
    window.macro_text.setPlainText("0 mvr 100")
    runner = MacroRunner(window)

    runner.run_macro()

    assert len(window.serial.sent) == 1
```

### Running Tests Without Hardware

All tests use fake/mock objects to avoid requiring actual hardware:
- `FakeSerial` - Captures transmitted commands
- `FakeWindow` - Simulates the main window interface
- `FakeTextEdit` / `FakeLabel` - Qt widget stubs

## Building Executables

### One-Directory Build (Recommended for Development)

```bash
uv run pyinstaller \
  --name NAI-Mover \
  --onedir \
  --windowed \
  --collect-all PySide6 \
  --collect-data mc_desktop.resources \
  --hidden-import mc_desktop.resources \
  --hidden-import serial.tools.list_ports \
  mc_desktop/__main__.py
```

Output: `dist/NAI-Mover/` folder with executable and dependencies.

### One-File Build (For Distribution)

```bash
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

Output: Single `dist/NAI-Mover` executable.

## Debugging

### Logging

The application logs to both console and file:
- **Console**: INFO level and above
- **File**: DEBUG level, located at `logs/info.log`

```python
import logging
logger = logging.getLogger("mc_desktop")
logger.debug("Detailed debug info")
logger.info("General information")
logger.warning("Warning message")
logger.error("Error occurred")
```

### Serial Communication Debugging

Enable verbose serial logging by checking `logs/info.log` for:
- Commands sent to controller
- Responses received
- Status polling results

### Qt Debugging

For UI issues, use Qt's built-in debugging:
```python
from PySide6.QtCore import qDebug
qDebug("Widget state: " + str(widget.isVisible()))
```

## Common Issues

### Import Errors After UI Changes

**Problem**: `ModuleNotFoundError` for form classes

**Solution**: Regenerate UI files:
```bash
uv run python scripts/generate_ui.py
```

### Serial Port Access Denied

**Problem**: Permission denied when connecting to serial port

**Solution**:
- Linux: Add user to `dialout` group: `sudo usermod -a -G dialout $USER`
- Windows: Close other applications using the COM port
- macOS: Check System Preferences > Security & Privacy

### PyInstaller Build Fails

**Problem**: Missing modules or resources in built executable

**Solution**: Ensure all hidden imports and data files are specified:
```bash
--hidden-import <module>
--collect-data <package>
```

### Stylesheet Not Applied

**Problem**: Application appears unstyled

**Solution**: Verify `mc_desktop/resources/Diffnes-Gold.qss` exists and is included in build.

## Release Process

1. Update version in `mc_desktop/version.py`
2. Run tests: `uv run python -m unittest discover tests`
3. Commit changes: `git commit -am "Bump version to X.Y.Z"`
4. Create tag: `git tag vX.Y.Z`
5. Push: `git push origin main --tags`
6. GitHub Actions automatically builds and creates release

## Getting Help

- **Issues**: https://github.com/NationalAperture/MC-Desktop/issues
- **Documentation**: See `docs/` folder
- **Architecture**: See `docs/ARCHITECTURE.md`
- **API Reference**: See `docs/API.md`
