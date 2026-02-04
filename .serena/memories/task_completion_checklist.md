# Task Completion Checklist for MC-Desktop

## Before Marking a Task Complete

### 1. Code Quality
- [ ] Code follows PEP 8 style guidelines
- [ ] Type hints added where practical
- [ ] Docstrings added to new public methods/classes
- [ ] No hardcoded serial command strings (use `commands.py` constants)

### 2. Testing
Run the test suite to ensure no regressions:
```bash
uv run python -m unittest discover tests
```

For specific test coverage:
```bash
uv run python -m pytest tests/ -v
```

- [ ] All existing tests pass
- [ ] New tests added for new functionality
- [ ] Tests use fake objects (no hardware required)

### 3. UI Changes (if applicable)
If you modified `.ui` files:
```bash
uv run python scripts/generate_ui.py
```
- [ ] UI regeneration completed without errors
- [ ] Did NOT edit files in `mc_desktop/ui/forms/` directly

### 4. Documentation
- [ ] CHANGELOG.md updated under `[Unreleased]` section (if significant change)
- [ ] README.md updated if new features affect usage
- [ ] Code comments added for complex logic

### 5. Version Changes (for releases only)
- [ ] Update `mc_desktop/version.py` with new version
- [ ] Create git tag: `git tag vX.Y.Z`

## Quick Validation Commands
```bash
# Run tests
uv run python -m unittest discover tests

# Verify app launches
uv run python -m mc_desktop

# Check for syntax errors (implicit in test run)
python -m py_compile mc_desktop/**/*.py
```

## Common Post-Task Issues
- **Import errors after UI changes**: Run `uv run python scripts/generate_ui.py`
- **Test failures with signals**: Ensure Qt event loop is properly handled in tests
- **Missing command constants**: Add new commands to `mc_desktop/commands.py`
