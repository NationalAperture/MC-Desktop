# Windows Load Time Optimization Guide

This document outlines optimizations to improve startup performance for the MC-Desktop Windows build.

---

## Priority 1: PyInstaller Configuration (Quick Wins)

These changes require editing `NAI-Mover.spec` only - no code changes needed.

### 1.1 Enable Python Bytecode Optimization

**File:** `NAI-Mover.spec` line 24

```python
# Change from:
optimize=0,

# Change to:
optimize=2,
```

**Why:** Level 2 optimization removes docstrings and assert statements from bytecode, reducing memory usage and load time.

**Expected improvement:** 100-300ms

---

### 1.2 Strip Debug Symbols

**File:** `NAI-Mover.spec` line 37

```python
# Change from:
strip=False,

# Change to:
strip=True,
```

**Why:** Debug symbols increase binary size and memory footprint. Production builds don't need them.

**Expected improvement:** 50-100ms + 5-10% smaller executable

---

### 1.3 Disable UPX Compression

**File:** `NAI-Mover.spec` line 38

```python
# Change from:
upx=True,

# Change to:
upx=False,
```

**Why:** UPX compresses the executable, but Windows must decompress the entire 273MB file into memory before the app can start. This decompression happens synchronously and blocks startup.

**Expected improvement:** 200-500ms

---

## Priority 2: Code Optimizations (Medium Effort)

### 2.1 Lazy-Load Serial Port Enumeration

**File:** `mc_desktop/ui/main_window.py` line 31

The `serial.tools.list_ports` module scans all COM ports at import time, which is slow on Windows.

```python
# Current (top of file):
from serial.tools import list_ports

# Change to: Remove the import from the top of the file
# Then import it only when needed in the method that uses it
```

Find where `list_ports` is used and add a local import:

```python
def _refresh_ports(self):
    from serial.tools import list_ports  # Lazy import
    ports = list_ports.comports()
    # ... rest of method
```

**Expected improvement:** 50-100ms

---

### 2.2 Defer Update Check

**File:** `mc_desktop/ui/main_window.py` line 376

```python
# Current:
QTimer.singleShot(2000, self._check_for_updates)

# Change to (delay until UI is fully interactive):
QTimer.singleShot(5000, self._check_for_updates)
```

**Why:** The GitHub API request can block the event loop on Windows. Delaying it gives the UI more time to become responsive first.

**Expected improvement:** 50-100ms perceived responsiveness

---

### 2.3 Defer Stylesheet Loading

**File:** `mc_desktop/app.py` lines 47-55

Move stylesheet application to after the window is shown:

```python
# Current in run_app():
_apply_stylesheet(app)
window = MainWindow()
window.show()

# Change to:
window = MainWindow()
window.show()
app.processEvents()  # Let window render first
_apply_stylesheet(app)
```

**Why:** Shows the window faster, then applies styling. Users perceive the app as loading quicker.

**Expected improvement:** 50-150ms perceived improvement

---

## Priority 3: Lazy-Load UI Tabs (Higher Effort)

Currently all 5 UI forms (1,586 lines of generated code) load at startup, even though users only see the first tab initially.

### 3.1 Implement Tab Lazy Loading

**Concept:** Only instantiate tab contents when the user first clicks on that tab.

```python
class MainWindow(QMainWindow):
    def __init__(self):
        # ... existing code ...

        # Track which tabs have been loaded
        self._tabs_loaded = {
            0: True,   # Connection tab - always load
            1: False,  # Settings tab
            2: False,  # Record tab
            # etc.
        }

        # Connect tab change signal
        self.tabWidget.currentChanged.connect(self._on_tab_changed)

    def _on_tab_changed(self, index: int):
        if not self._tabs_loaded.get(index, False):
            self._load_tab(index)
            self._tabs_loaded[index] = True

    def _load_tab(self, index: int):
        if index == 1:
            self._setup_settings_tab()
        elif index == 2:
            self._setup_record_tab()
        # etc.
```

**Expected improvement:** 100-200ms

---

## Priority 4: Build Distribution (Advanced)

### 4.1 Consider --onedir Mode

Instead of a single executable, PyInstaller can create a directory with the main exe and separate DLLs.

**Pros:**
- Windows caches DLLs between runs (faster subsequent launches)
- No decompression overhead
- Smaller individual file scans for antivirus

**Cons:**
- Distribution is a folder instead of single file
- Requires installer (NSIS, Inno Setup) for clean user experience

**To implement:** Modify `NAI-Mover.spec` or create a new spec file for directory mode.

---

### 4.2 Code Signing

**Why:** Windows SmartScreen and antivirus software are more suspicious of unsigned executables. They may perform deeper scans that delay startup.

**Solution:** Purchase a code signing certificate and sign the executable during the build process.

---

## Summary Table

| Optimization | File | Effort | Expected Improvement |
|-------------|------|--------|---------------------|
| Set `optimize=2` | NAI-Mover.spec | Trivial | 100-300ms |
| Set `strip=True` | NAI-Mover.spec | Trivial | 50-100ms |
| Set `upx=False` | NAI-Mover.spec | Trivial | 200-500ms |
| Lazy-load serial.tools | main_window.py | Easy | 50-100ms |
| Defer update check | main_window.py | Easy | 50-100ms |
| Defer stylesheet | app.py | Easy | 50-150ms |
| Lazy-load UI tabs | main_window.py | Medium | 100-200ms |
| Use --onedir mode | Build config | Medium | Varies |
| Code signing | Build pipeline | Medium | Varies |

**Total potential improvement: 600ms - 1.5+ seconds**

---

## How to Measure

Add timing instrumentation to measure actual impact:

```python
# In mc_desktop/__main__.py
import time
_start = time.perf_counter()

# ... existing imports and code ...

# At end of MainWindow.__init__():
print(f"Startup time: {time.perf_counter() - _start:.3f}s")
```

Or use Python's built-in profiler:

```bash
python -m cProfile -s cumtime -m mc_desktop > profile.txt
```

---

## Recommended Order of Implementation

1. Apply all three PyInstaller spec changes (5 minutes, ~400ms improvement)
2. Lazy-load serial.tools.list_ports (10 minutes, ~75ms improvement)
3. Defer update check to 5 seconds (1 minute, perceived improvement)
4. Test and measure results
5. If more improvement needed, implement lazy tab loading
