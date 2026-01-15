# Contributing to MC-Desktop

Thank you for your interest in contributing to MC-Desktop (NAI-Mover).

## Development Setup

See [docs/DEVELOPER.md](docs/DEVELOPER.md) for detailed setup instructions.

## Making Changes

### 1. Create a Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/bug-description
```

### 2. Make Your Changes

- Follow existing code style and patterns
- Add tests for new functionality
- Update documentation if needed

### 3. Update the Changelog

**Important**: Update `CHANGELOG.md` with your changes under the `[Unreleased]` section.

Add your entry to the appropriate category:
- **Added** - New features
- **Changed** - Changes to existing functionality
- **Fixed** - Bug fixes
- **Removed** - Removed features

Example:
```markdown
## [Unreleased]

### Added
- New keyboard shortcut for emergency stop (Escape key)

### Fixed
- Serial connection timeout now properly handled
```

### 4. Commit Your Changes

Use clear, descriptive commit messages. We recommend (but don't require) conventional commit format:

```bash
# Format: <type>: <description>

git commit -m "feat: add keyboard shortcuts for jog controls"
git commit -m "fix: prevent crash when no node selected"
git commit -m "docs: update macro syntax examples"
git commit -m "refactor: extract serial commands to constants"
git commit -m "test: add coverage for edge cases"
```

**Commit Types:**
| Type | Description |
|------|-------------|
| `feat` | New feature |
| `fix` | Bug fix |
| `docs` | Documentation only |
| `refactor` | Code change that doesn't fix a bug or add a feature |
| `test` | Adding or updating tests |
| `chore` | Maintenance tasks, releases |
| `perf` | Performance improvement |

### 5. Submit a Pull Request

```bash
git push origin feature/your-feature-name
```

Then create a Pull Request on GitHub.

## Release Process

Releases are managed by maintainers:

1. Review and merge PRs
2. Update `CHANGELOG.md`:
   - Move `[Unreleased]` items to new version section
   - Add version number and date
3. Update version in `mc_desktop/version.py`
4. Commit: `git commit -am "chore: release v0.2.0"`
5. Tag and push: `git tag v0.2.0 && git push origin main --tags`
6. GitHub Actions automatically builds and publishes the release

## Optional: Automated Changelog Generation

If you prefer automated changelog generation from commit messages, you can use `git-cliff`:

### Setup git-cliff

```bash
# Install
cargo install git-cliff
# or
pip install git-cliff
```

### Configuration

Create `cliff.toml` in project root:

```toml
[changelog]
header = """
# Changelog\n
All notable changes to this project will be documented in this file.\n
"""
body = """
{% if version %}\
    ## [{{ version | trim_start_matches(pat="v") }}] - {{ timestamp | date(format="%Y-%m-%d") }}
{% else %}\
    ## [Unreleased]
{% endif %}\
{% for group, commits in commits | group_by(attribute="group") %}
    ### {{ group | striptags | trim | upper_first }}
    {% for commit in commits %}
        - {{ commit.message | upper_first }}\
    {% endfor %}
{% endfor %}\n
"""
footer = ""
trim = true

[git]
conventional_commits = true
filter_unconventional = true
commit_parsers = [
    { message = "^feat", group = "Added" },
    { message = "^fix", group = "Fixed" },
    { message = "^doc", group = "Documentation" },
    { message = "^perf", group = "Performance" },
    { message = "^refactor", group = "Changed" },
    { message = "^test", group = "Testing" },
    { message = "^chore\\(release\\)", skip = true },
    { message = "^chore", group = "Miscellaneous" },
]
filter_commits = false
tag_pattern = "v[0-9].*"
```

### Generate Changelog

```bash
# Preview unreleased changes
git cliff --unreleased

# Generate full changelog
git cliff -o CHANGELOG.md

# Generate for specific version
git cliff --tag v0.2.0 -o CHANGELOG.md
```

## Code Style

- Follow PEP 8 for Python code
- Use type hints where practical
- Add docstrings to public functions and classes
- Keep functions focused and reasonably sized

## Testing

```bash
# Run all tests
uv run python -m unittest discover tests

# Run specific test file
uv run python -m pytest tests/test_macro_runner.py -v
```

## Questions?

- Open an issue for bugs or feature requests
- Check existing issues before creating new ones
