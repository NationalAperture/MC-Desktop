# Code Style and Conventions for MC-Desktop

## Python Style
- **PEP 8**: Follow standard Python style guidelines
- **Type Hints**: Encouraged for function signatures and class attributes
- **Docstrings**: Required for public methods and classes

## Naming Conventions
- Classes: `PascalCase` (e.g., `MacroRunner`, `NodeSettingsController`)
- Functions/Methods: `snake_case` (e.g., `run_macro`, `get_stage_values`)
- Constants: `UPPER_SNAKE_CASE` (e.g., `CMD_MOVE_ABSOLUTE`)
- Private methods: Leading underscore (e.g., `_dispatch_command`)

## Type Hints Examples
```python
def __init__(self) -> None:
    self._lines: list[str] = []

def toPlainText(self) -> str:
    return "\n".join(self._lines)

def queue_serial_command(self, params: tuple[str, ...], **kwargs: object) -> None:
    ...
```

## Testing Patterns
- Use **fake objects** instead of mocks when possible
- Fake classes follow pattern: `FakeSerial`, `FakeWindow`, `FakeTextEdit`
- Tests should run without hardware using these fakes
- Test files named: `test_<module_name>.py`

## UI Development
- **Never edit** files in `mc_desktop/ui/forms/` - they are auto-generated
- Edit `.ui` files in Qt Creator at `mc_desktop/ui/designer/`
- Run `uv run python scripts/generate_ui.py` after UI changes
- Controllers in `mc_desktop/ui/controllers.py` contain business logic

## Command Constants
- All serial commands defined in `mc_desktop/commands.py`
- Use constants instead of string literals: `CMD_MOVE_ABSOLUTE` not `"mva"`

## Commit Messages
Conventional commit format recommended:
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation only
- `refactor:` Code change without new feature or bug fix
- `test:` Adding/updating tests
- `chore:` Maintenance tasks

## Import Organization
1. Standard library imports
2. Third-party imports
3. Local application imports

## Logging
```python
import logging
logger = logging.getLogger("mc_desktop")
logger.debug("Detailed debug info")
logger.info("General information")
logger.error("Error occurred")
```
Logs written to: `logs/info.log`
