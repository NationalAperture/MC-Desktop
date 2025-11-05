# Distribution Guide

This document captures the manual workflow for cutting and distributing MC Desktop releases through GitHub Releases. It assumes you have commit rights to the repository and access to the project’s signing credentials (if any).

---

## 1. Pre-release Checklist
- Ensure the target branch (usually `main`) contains all changes slated for release.
- Update `pyproject.toml` and any other version markers to the new semantic version.
- Refresh `CHANGELOG.md` with a dated entry summarising user-facing changes.
- Run the automated test suite locally:  
  `python3 -m unittest discover tests`
- Smoke-test the GUI on your development machine once with a local virtualenv:  
  `uv run python -m mc_desktop`

Commit the version bump + changelog, then tag the release commit:
```bash
git commit -am "Release vX.Y.Z"
git tag -s vX.Y.Z -m "Release vX.Y.Z"          # drop -s if you do not sign tags
git push origin main
git push origin vX.Y.Z
```

---

## 2. Build Artifacts
PyInstaller output is OS-specific, so build on each target platform.

### Linux (e.g., Ubuntu)
```bash
uv pip install pyinstaller
uv run pyinstaller \
  --name NAI-Mover \
  --onefile \
  --windowed \
  --collect-all PySide6 \
  --collect-data mc_desktop.resources \
  --hidden-import serial.tools.list_ports \
  mc_desktop/__main__.py
```
- Result: `dist/NAI-Mover` (single-file ELF). Optionally repeat with `--onedir` to ship a directory bundle for easier debugging.

### Windows (PowerShell)
```powershell
uv pip install pyinstaller
uv run pyinstaller `
  --name NAI-Mover `
  --onefile `
  --windowed `
  --collect-all PySide6 `
  --collect-data mc_desktop.resources `
  --hidden-import serial.tools.list_ports `
  mc_desktop/__main__.py
```
- Result: `dist\NAI-Mover.exe`. Repeat with `--onedir` if you also want a directory bundle.

Copy the final artifacts to a clean staging area, zip them with platform-specific names, and record checksums (SHA256) for release notes.

---

## 3. Publish the GitHub Release
1. Navigate to **Releases → Draft a new release**.
2. Choose tag `vX.Y.Z` and target branch `main`.
3. Title: `vX.Y.Z`.
4. Release notes:
   - Bullet the highlights (copy from `CHANGELOG.md`).
   - Include SHA256 hashes for each uploaded asset.
   - Link to any migration instructions or known issues.
5. Upload assets:
   - `NAI-Mover-linux-x86_64.tar.gz` (or similar naming).
   - `NAI-Mover-windows-x86_64.zip`.
   - Any supplementary docs (e.g., checksum file).
6. Mark as “Latest” and publish. Use the “Pre-release” toggle if you are asking users to test before a full rollout.

---

## 4. Notifying Users & Updates
- Share the GitHub release link with downstream users (email, Slack, etc.).
- If you maintain an auto-updater, ensure it polls the GitHub Releases API or a curated manifest and provide the new asset URLs.
- For manual updates:
  1. Direct users to download the latest binary for their OS.
  2. Instruct them to replace the previous executable/bundle.
  3. Remind Windows users to unblock the file if SmartScreen warns about an unknown publisher.

Maintain a lightweight `UPDATES.md` (optional) detailing recommended upgrade paths if releases involve data migrations or config changes.

---

## 5. Post-release Follow-up
- Monitor issue tracker and crash logs (`logs/info.log` in user reports) for regressions.
- If a hotfix is needed, repeat the workflow with an incremented patch version (e.g., `vX.Y.Z+1`) and clearly label the release notes.

---

## 6. Automation Ideas (Future Work)
- Add GitHub Actions jobs that build Linux/Windows artifacts automatically on tag push.
- Cache PyInstaller outputs and upload them directly from CI to the draft release.
- Integrate checksum verification into CI to reduce manual steps.

Following this process keeps official binaries consistent across platforms and provides a clear upgrade story for users. Update this guide whenever the build tooling or release cadence changes.
