# MC-Desktop (NAI-Mover) Project Overview

## Purpose
Desktop control panel for National Aperture, Inc. MC-6 series motion controllers. The application provides a graphical interface for configuring and controlling precision motion stages via serial communication.

## Tech Stack
| Component | Technology |
|-----------|------------|
| Language | Python 3.13+ |
| GUI Framework | PySide6 (Qt6) |
| Serial Communication | pyserial |
| Package Management | uv |
| Testing | pytest, unittest, pytest-qt |
| Bundling | PyInstaller |
| Version Control | Git + GitHub Actions for CI/CD |

## Key Dependencies
- `PySide6>=6.10.0` - Qt6 GUI framework
- `pyserial>=3.5` - Serial port communication  
- `packaging>=25.0` - Version comparison utilities
- `pytest>=9.0.2` - Testing framework
- `pytest-qt>=4.5.0` - Qt widget testing

## Project Structure
```
mc_desktop/
├── app.py              # Application bootstrap and logging
├── communication.py    # Serial transport and worker threads
├── node_manager.py     # Node configuration state management
├── commands.py         # Centralized serial command constants
├── version.py          # Version string (single source of truth)
├── updater.py          # GitHub release update checker
├── resources/          # Static assets (stylesheets)
└── ui/
    ├── controllers.py  # UI logic controllers (MacroRunner, NodeSettingsController)
    ├── main_window.py  # Main window implementation
    ├── update_dialog.py # Update prompt dialog
    ├── designer/       # Qt Designer .ui source files (DO NOT EDIT forms/)
    └── forms/          # Auto-generated PySide6 wrappers
```

## Architecture Patterns
- **Signal-Slot Pattern**: Qt signals for communication between components
- **Worker Threads**: Background serial communication via `Worker` class
- **Fake Objects for Testing**: `FakeSerial`, `FakeWindow`, etc. for hardware-free testing
- **Command Constants**: All serial commands centralized in `commands.py`
- **State Machine**: `MacroRunner` uses state machine for macro execution flow

## Entry Points
- Module: `python -m mc_desktop`
- Script: `mc-desktop` (after installation)
- Main function: `mc_desktop.app:run_app`
