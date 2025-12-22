# Core Foundation (C00–C05)

> Last Updated: 2026-01-01

> Infrastructure that **every script depends on**. Read this first.

**Who uses these:** Every script in `implementation/`, every GUI module (G00–G04), and all entry-points under `main/`. No script may bypass them.

---

## Dependency Chain

```
C00_set_packages     ← Root (no dependencies)
       ↓
C01_logging_handler  ← Depends on C00
       ↓
C02_set_file_paths   ← Depends on C00, C01
       ↓
C03_system_processes ← Depends on C00, C01
       ↓
C04_config_loader    ← Depends on C00, C01, C02
       ↓
C05_error_handler    ← Depends on C00, C01, C04
```

---

## C00_set_packages

**Purpose:** Central import hub. All external and standard library packages are imported here and re-exported.

**Critical Rule:** Never import external packages directly. Always use:
```python
from core.C00_set_packages import *
```

**Warning:** Never use `import pandas as pd`, `import numpy as np`, etc. Re-exports in C00 define canonical naming across the project (`pd`, `np`, etc.).

### What's Available

> **Note:** This is a summary of the most common exports. For the full, authoritative list, see `__all__` in `C00_set_packages.py`.

**Standard Library:**
`sys`, `Path`, `os`, `re`, `json`, `csv`, `shutil`, `glob`, `tempfile`, `subprocess`, `hashlib`, `pickle`, `zipfile`, `io`, `BytesIO`, `time`, `datetime`, `date`, `timedelta`, `dt` (datetime module alias), `calendar`, `platform`, `getpass`, `logging`, `threading`, `queue`, `contextlib`, `deepcopy`, `dedent`, `dataclass`

**Typing:**
`Any`, `Callable`, `cast`, `Dict`, `List`, `Tuple`, `Optional`, `Union`, `Sequence`, `Iterable`, `Mapping`, `MutableMapping`, `Type`, `Literal`, `Protocol`, `overload`, `TYPE_CHECKING`

**Concurrency:**
`ThreadPoolExecutor`, `ProcessPoolExecutor`, `as_completed`

**Third-Party:**
- `pd` (pandas), `np` (numpy)
- `requests`
- `openpyxl`
- `yaml`
- `tqdm`
- `pdfplumber`, `PyPDF2`, `extract_text` (pdfminer)
- `snowflake.connector`

**Selenium:**
`webdriver`, `By`, `Keys`, `Options`, `WebDriverWait`, `EC`, `ChromeDriverManager`

**Google API:**
`Request`, `Credentials`, `InstalledAppFlow`, `build`, `HttpError`, `MediaFileUpload`, `MediaIoBaseUpload`, `MediaIoBaseDownload`

---

## C01_logging_handler

**Purpose:** Centralised logging with file output, console output, and exception capture.

### Setup Pattern (Required in Every Script)

```python
from core.C01_logging_handler import get_logger, log_exception, init_logging
logger = get_logger(__name__)

# In main() or entry point:
init_logging()
```

### Key Functions

| Function | Signature | Use |
|----------|-----------|-----|
| `init_logging` | `(log_directory: Path \| None = None, level: int = logging.INFO, enable_console: bool = True) -> None` | Call once at application start. Idempotent. |
| `get_logger` | `(name: str \| None = None) -> logging.Logger` | Get a logger instance. Pass `__name__`. |
| `log_exception` | `(exception: Exception, logger_instance: logging.Logger \| None = None, context: str = "") -> None` | Log exception with full traceback. |
| `log_divider` | `(level: str = "info", label: str = "", width: int = 80) -> None` | Visual separator in logs. |
| `enable_print_redirection` | `() -> None` | Route print() to logging. |
| `disable_print_redirection` | `() -> None` | Restore normal print(). |

### Constants

| Name | Value | Purpose |
|------|-------|---------|
| `LOG_FORMAT` | `"%(asctime)s \| %(levelname)-8s \| ..."` | Log line format |
| `DATE_FORMAT` | `"%Y-%m-%d %H:%M:%S"` | Timestamp format |
| `LOGS_DIR` | `PROJECT_ROOT / "logs"` | Default log location |
| `active_log_file` | `Path \| None` | Current log file path (after init) |

---

## C02_set_file_paths

**Purpose:** Single source of truth for all project directories and path utilities.

**Critical Rule:** Other modules must not re-implement their own project root or folder discovery. Always use these constants.

**❌ Incorrect:**
```python
from pathlib import Path
root = Path(__file__).resolve().parent.parent
```

**✅ Correct:**
```python
from core.C02_set_file_paths import PROJECT_ROOT
```

### Directory Constants

All paths are `Path` objects relative to `PROJECT_ROOT`:

| Constant | Path | Purpose |
|----------|------|---------|
| `PROJECT_ROOT` | Auto-detected | Project root directory |
| `PROJECT_ROOT_STR` | String version | For APIs requiring strings |
| `PROJECT_NAME` | Folder name | Project identifier |
| `USER_HOME_DIR` | `Path.home()` | User's home directory |
| `DATA_DIR` | `/data` | Input data files |
| `OUTPUTS_DIR` | `/outputs` | Generated outputs |
| `LOGS_DIR` | `/logs` | Log files |
| `CONFIG_DIR` | `/config` | Configuration files |
| `CACHE_DIR` | `/cache` | Cached data |
| `CREDENTIALS_DIR` | `/credentials` | API credentials |
| `SQL_DIR` | `/sql` | SQL query files |
| `CORE_DIR` | `/core` | Core modules |
| `GUI_DIR` | `/gui` | GUI modules |
| `IMPLEMENTATION_DIR` | `/implementation` | Business logic |
| `MAIN_DIR` | `/main` | Entry point scripts |
| `BINARY_FILES_DIR` | `/binary_files` | Non-text assets |
| `SCRATCHPAD_DIR` | `/scratchpad` | Temporary work |
| `TECH_DOCS_DIR` | `/tech_docs` | Technical documentation |
| `USER_GUIDES_DIR` | `/user_guides` | End-user documentation |

**Google Drive Paths:**
| Constant | Path |
|----------|------|
| `GDRIVE_DIR` | Same as `CREDENTIALS_DIR` |
| `GDRIVE_CREDENTIALS_FILE` | `/credentials/credentials.json` |
| `GDRIVE_TOKEN_FILE` | `/credentials/token.json` |

**Collection:**
`CORE_FOLDERS` — Tuple of all directory constants for iteration.

### Utility Functions

| Function | Signature | Use |
|----------|-----------|-----|
| `ensure_directory` | `(path: Path) -> Path` | Create directory if missing. Returns resolved path. |
| `build_path` | `(*parts: str \| Path) -> Path` | Join path components. Returns resolved path. |
| `get_temp_file` | `(suffix: str = "", prefix: str = "temp_", directory: Path \| None = None) -> Path` | Generate unique temp file path (file not created). |
| `path_exists_safely` | `(path: Path) -> bool` | Check existence without raising exceptions. |
| `normalise_shared_drive_root` | `(selected_root: str \| Path) -> Path` | Collapse Google Shared Drive paths to drive root. |

### Example

```python
from core.C02_set_file_paths import DATA_DIR, OUTPUTS_DIR, ensure_directory, build_path

# Ensure output subdirectory exists
report_dir = ensure_directory(OUTPUTS_DIR / "reports")

# Build a file path
output_file = build_path(report_dir, "summary.csv")
```

---

## C03_system_processes

**Purpose:** OS detection and platform-specific folder resolution.

### Functions

| Function | Signature | Returns |
|----------|-----------|---------|
| `detect_os` | `() -> str` | `"Windows"`, `"Windows (WSL)"`, `"macOS"`, `"Linux"`, or `"iOS"` |
| `user_download_folder` | `() -> Path` | User's Downloads directory (platform-aware, WSL-aware) |

### Example

```python
from core.C03_system_processes import detect_os, user_download_folder

if detect_os() == "Windows (WSL)":
    downloads = user_download_folder()  # Returns /mnt/c/Users/.../Downloads
```

---

## C04_config_loader

**Purpose:** Load YAML/JSON configuration from `/config/` directory.

### Setup

Configuration is **not loaded at import time**. You must call:
```python
from core.C04_config_loader import initialise_config, get_config
initialise_config()
```

### Config File Locations

Automatically loads (in order, merged):
1. `config/config.yaml` or `config/config.yml`
2. `config/settings.json`

Later files override earlier ones. Nested dicts are merged recursively.

### Functions

| Function | Signature | Use |
|----------|-----------|-----|
| `initialise_config` | `() -> Dict[str, Any]` | Load all config files. Call once at startup. |
| `reload_config` | `() -> Dict[str, Any]` | Re-read config files. |
| `get_config` | `(section: str, key: str, default: Any = None) -> Any` | Safely retrieve a config value. |

### Example

```python
from core.C04_config_loader import initialise_config, get_config

initialise_config()

# config.yaml contains:
# snowflake:
#   user: "my_user"
#   warehouse: "COMPUTE_WH"

user = get_config("snowflake", "user")
warehouse = get_config("snowflake", "warehouse", default="DEFAULT_WH")
```

### Direct Access

The `CONFIG` dict is available for direct access after initialisation:
```python
from core.C04_config_loader import CONFIG
all_snowflake_settings = CONFIG.get("snowflake", {})
```

---

## C05_error_handler

**Purpose:** Global exception handling for CLI and service applications.

### Setup

```python
from core.C05_error_handler import install_global_exception_hook, handle_error

# At application start:
install_global_exception_hook()
```

### Functions

| Function | Signature | Use |
|----------|-----------|-----|
| `install_global_exception_hook` | `() -> None` | Capture all uncaught exceptions via `sys.excepthook`. |
| `handle_error` | `(exception: Exception, context: str = "", fatal: bool = False) -> None` | Log exception. If `fatal=True` and config allows, exit application. |
| `global_exception_hook` | `(exc_type, exc_value, exc_traceback) -> None` | The hook function (auto-installed). |
| `simulate_error` | `() -> None` | Raises `ValueError` for testing error handlers. |

**When to use which:**
- `log_exception()` (from C01) — Log and continue. Use for recoverable errors where the app should keep running.
- `handle_error()` (from C05) — Log and potentially exit. Use only when you're prepared for the app to terminate (depending on config).

**Guidance:** Use exceptions for control flow in pipelines only with `log_exception()`. Reserve `handle_error(fatal=True)` for irrecoverable workflow termination.

### Fatal Exit Behaviour

Controlled by config:
```yaml
# config.yaml
error_handling:
  exit_on_fatal: true
```

When `exit_on_fatal: true` and `handle_error(..., fatal=True)` is called, the application exits with code 1.

### Example

```python
from core.C05_error_handler import install_global_exception_hook, handle_error

install_global_exception_hook()

try:
    risky_operation()
except Exception as e:
    handle_error(e, context="During data import", fatal=False)
    # Logged but continues

try:
    critical_operation()
except Exception as e:
    handle_error(e, context="Critical failure", fatal=True)
    # Exits if config allows
```

---

## Required Script Bootstrap

**Every script using Core modules MUST start with this structure.** Do not deviate:

```python
# ====================================================================================================
# 1. SYSTEM IMPORTS
# ====================================================================================================
from __future__ import annotations
import sys
from pathlib import Path

project_root = str(Path(__file__).resolve().parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)
if "" in sys.path:
    sys.path.remove("")
sys.dont_write_bytecode = True

# ====================================================================================================
# 2. PROJECT IMPORTS
# ====================================================================================================
from core.C00_set_packages import *
from core.C01_logging_handler import get_logger, log_exception, init_logging
logger = get_logger(__name__)

# ====================================================================================================
# 3. CONSTANTS
# ----------------------------------------------------------------------------------------------------
# Configuration values and magic numbers used throughout this module.
# ====================================================================================================

# Add constants here...

# ====================================================================================================
# 4. IMPLEMENTATION
# ----------------------------------------------------------------------------------------------------
# Main classes and functions for this module.
# ====================================================================================================

# Add implementation here...

# ====================================================================================================
# 98. PUBLIC API
# ====================================================================================================
__all__ = [
    # List exported names here
]

# ====================================================================================================
# 99. MAIN EXECUTION
# ====================================================================================================
def main() -> None:
    """Entry point. Keep business logic in implementation/ or core/, not here."""
    pass

if __name__ == "__main__":
    init_logging()
    main()
```

**Section Structure:**
- **Section 1:** System imports — do not modify
- **Section 2:** Project imports — hub imports, logger init
- **Sections 3–97:** Implementation — split into logical numbered sections, each with title and description
- **Section 98:** Public API — `__all__` declaration
- **Section 99:** Main execution — `main()` function and entry point

You do not need to use all sections 3–97. Use as many as needed for logical separation.

---

## Summary Table

| Module | Exports | Primary Use |
|--------|---------|-------------|
| C00 | 75 | Package hub — all external imports |
| C01 | 12 | Logging — get_logger, log_exception, init_logging |
| C02 | 25 | File paths — PROJECT_ROOT, directory constants, utilities |
| C03 | 2 | System — OS detection, platform paths |
| C04 | 8 | Config — YAML/JSON loading, get_config |
| C05 | 4 | Error handling — global hooks, handle_error |

**Total: 126 exports**

> *Export counts are indicative. `__all__` in each module's source code is authoritative.*