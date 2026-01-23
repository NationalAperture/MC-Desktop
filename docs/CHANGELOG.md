# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Documentation suite in `docs/` folder:
  - `API.md` - Serial command protocol reference
  - `ARCHITECTURE.md` - Software architecture and component diagrams
  - `DEVELOPER.md` - Developer setup and contribution guide
  - `MACRO_SYNTAX.md` - User guide for macro automation

### Changed

### Fixed

### Removed

---

## [0.1.9] - 2025-01-15

### Added
- Auto-update system with GitHub Releases integration (`updater.py`, `update_dialog.py`)
- Version display in status bar footer
- Patch notes display in update dialog
- Comprehensive documentation in `docs/` folder

### Changed
- Build optimization for faster startup and smaller bundles

## [0.1.8] - 2025-01-14

### Added
- Unit tests for macro runner with completion signal handling
- Tests for wait and loop commands in macros

### Changed
- Macro execution now waits for motion completion signal before advancing
- `command_complete` signal added to `CommunicationManager`

### Fixed
- Macros no longer advance before motion completes

## [0.1.7] - 2025-01-13

### Changed
- Refactored `mc_desktop.node_manager` to use structured dataclasses instead of raw dicts
- Overhauled `mc_desktop.communication` with blocking worker queue and serial transport wrapper
- Extracted macro execution, settings management, and prompt-driven commands into dedicated UI controllers
- Reorganized designer assets under `mc_desktop/ui/designer/`

### Added
- `scripts/generate_ui.py` for regenerating PySide6 forms after editing `.ui` files
- Unit tests for node manager (CSV helpers, pointer updates, lifecycle validation)
- Centralized logging in communication layer

---

## Version History Summary

| Version | Date | Highlights |
|---------|------|------------|
| 0.1.9 | 2025-01-15 | Auto-update system, documentation |
| 0.1.8 | 2025-01-14 | Macro completion signals, tests |
| 0.1.7 | 2025-01-13 | Major refactor: dataclasses, controllers |

---

## How to Update This Changelog

When making changes, add entries under `[Unreleased]` in the appropriate category:

- **Added** - New features
- **Changed** - Changes in existing functionality
- **Deprecated** - Soon-to-be removed features
- **Removed** - Removed features
- **Fixed** - Bug fixes
- **Security** - Vulnerability fixes

When releasing a new version:
1. Move `[Unreleased]` entries to a new version section
2. Add the version number and release date
3. Update `mc_desktop/version.py`
4. Commit with message: `chore: release vX.Y.Z`
5. Tag: `git tag vX.Y.Z && git push origin vX.Y.Z`
