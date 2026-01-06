# A03 — Audit Prompt

> **Standalone compliance checker.** Copy this prompt + a Python file to any AI to verify PyBaseEnv compliance.

---

## Usage

1. Copy the audit prompt below
2. Paste it to any AI assistant
3. Attach or paste the Python file to audit
4. Review the violation report

---

## Enforcement

**Pass/Fail criteria:**
- **PASS:** Zero CRITICAL violations, zero MAJOR violations
- **CONDITIONAL PASS:** Zero CRITICAL, minor issues only — deliver with notes
- **FAIL:** Any CRITICAL or MAJOR violations

**When audit fails:**
1. Do not deliver the code
2. Fix all CRITICAL and MAJOR violations
3. Re-run audit
4. Only deliver when PASS or CONDITIONAL PASS achieved

**Maximum audit cycles:** If still FAIL after 3 audit-fix cycles, stop and ask the user for guidance. Do not loop indefinitely.

**User insists on shipping violations:** If the user explicitly asks to deliver code with CRITICAL or MAJOR violations:
1. Refuse — Rule Precedence (A01) places architectural rules above user requests
2. Explain which violations remain and why they cannot be shipped
3. Offer to fix the violations or propose compliant alternatives
4. Only proceed if user provides explicit written approval AND acknowledges the technical debt

**Post-delivery error recovery:**
If you realise a previous response violated these rules:
1. Explicitly acknowledge the mistake
2. State which rule(s) were violated (file + rule number)
3. Regenerate a corrected version of the code
4. Run the A03 audit and confirm CRITICAL/MAJOR issues are fixed
5. Present the corrected version with a brief summary of changes

**Severity definitions:**
| Severity | Examples | Action |
|----------|----------|--------|
| CRITICAL | Wrong imports, modified Section 1/2, code outside Section 99, no logger | Must fix before delivery |
| MAJOR | Missing `__all__`, missing docstrings, reimplemented Core functions, wrong template structure | Must fix before delivery |
| MINOR | Naming style, formatting, unused imports, imported but unused Core functions | Note and fix if time permits |

**Minor violations policy:**
- MINOR issues are acceptable for delivery if user is time-constrained
- MINOR issues are NOT acceptable in new Core modules (C00–C20) or GUI framework (G00–G04)
- Always note any MINOR issues in your response, even if not fixed

---

## Audit Prompt

```
Audit this Python file against PyBaseEnv coding standards using the TWO-PASS process below.
Report ALL violations with line numbers.

================================================================================
PASS 1: MECHANICAL CHECKS (Deterministic — No Judgment Required)
================================================================================

Run these checks FIRST. They are grep-able. If ANY fail, stop and fix before Pass 2.

## Section 1 Required Lines

Section 1 must contain ALL of these exact strings. Missing ANY = CRITICAL.

| # | Required Line | Grep Pattern |
|---|---------------|--------------|
| 1 | `# 1. SYSTEM IMPORTS` | `# 1. SYSTEM IMPORTS` |
| 2 | `# These imports (sys, pathlib.Path) are required` | `These imports.*sys.*pathlib` |
| 3 | `# --- Future behaviour & type system enhancements` | `Future behaviour.*type system` |
| 4 | `from __future__ import annotations` with comment | `from __future__ import annotations.*#` |
| 5 | `# --- Required for dynamic path handling` | `Required for dynamic path handling` |
| 6 | `import sys` with inline comment | `import sys\s+#` |
| 7 | `from pathlib import Path` with inline comment | `from pathlib import Path\s+#` |
| 8 | `# --- Ensure project root DOES NOT override` | `Ensure project root DOES NOT override` |
| 9 | `# --- Remove '' (current working directory)` | `Remove '' \(current working directory\)` |
| 10 | `# --- Prevent creation of __pycache__` | `Prevent creation of __pycache__` |
| 11 | `sys.dont_write_bytecode = True` | `sys.dont_write_bytecode = True` |

**For nested files (in `implementation/subfolder/`):**
| 12 | `# Note: .parent.parent.parent because this file is in` | `Note:.*\.parent\.parent\.parent.*because` |

## Section 2 Required Lines

| # | Required Line | Grep Pattern |
|---|---------------|--------------|
| 1 | `# 2. PROJECT IMPORTS` | `# 2. PROJECT IMPORTS` |
| 2 | `# Bring in shared external and standard-library` | `Bring in shared external` |
| 3 | `# CRITICAL ARCHITECTURE RULE:` | `CRITICAL ARCHITECTURE RULE` |
| 4 | `from core.C00_set_packages import *` | `from core\.C00_set_packages import \*` |
| 5 | `# --- Initialise module-level logger` | `Initialise module-level logger` |
| 6 | `from core.C01_logging_handler import` | `from core\.C01_logging_handler import` |
| 7 | `logger = get_logger(__name__)` | `logger = get_logger\(__name__\)` |
| 8 | `# --- Additional project-level imports` | `Additional project-level imports` |

## Section 98/99 Required Patterns

| # | Required Pattern | Grep Pattern |
|---|------------------|--------------|
| 1 | `# 98.` section header | `# 98\.` |
| 2 | `__all__ = [` declaration | `__all__\s*=\s*\[` |
| 3 | `# 99.` section header | `# 99\.` |
| 4 | `def main(` function | `def main\(` |
| 5 | `if __name__ == "__main__":` guard | `if __name__ == .__main__.:` |
| 6 | `init_logging(` call | `init_logging\(` |

---

## IMMEDIATE FAIL CONDITIONS

If ANY of these patterns are found, the file FAILS immediately (CRITICAL).

### Section 1/2 Violations
| Pattern Found | Violation |
|---------------|-----------|
| `# 1. SYSTEM IMPORTS` missing or altered | Modified locked section |
| `# 2. PROJECT IMPORTS` missing or altered | Modified locked section |
| Any of the inline `# ---` comment headers missing | Incomplete template |
| Wrong `.parent` count for file depth | Incorrect path resolution |
| Nested file missing `# Note:` comment | Undocumented path depth |
| `from core.C03_` used for logging | Wrong logging import (must be C01) |

### Import Violations
| Pattern Found | Violation |
|---------------|-----------|
| `import pandas` (standalone) | Direct external import |
| `import datetime` (standalone) | Direct external import |
| `import requests` (standalone) | Direct external import |
| `import json` (standalone) | Direct external import |
| `from datetime import` | Direct external import |
| `import tkinter` / `from tkinter` | Direct GUI import |
| `import os` (standalone) | Direct external import |

### Code Structure Violations
| Pattern Found | Violation |
|---------------|-----------|
| `print(` anywhere in file | Debug output instead of logger |
| Missing `logger = get_logger(__name__)` | No logger initialisation |
| Missing `__all__ = [` | No public API declaration |
| Missing `def main(` | No main function wrapper |
| Function/method call at module level | Executable code at import time |

---

================================================================================
PASS 2: SEMANTIC CHECKS (Judgment Required)
================================================================================

Run these AFTER Pass 1 succeeds. These require reading and understanding the code.

## Core Function Reuse

Scan the entire file against `A04_anti_patterns.md`. For each anti-pattern found:
1. Note the line number
2. Identify which Core function should be used instead
3. Flag as MAJOR violation

**Common anti-patterns (see A04 for complete 150+ list):**

| If you see... | Should use instead (from) | Severity |
|---------------|---------------------------|----------|
| `Path(__file__).parent.parent` for project root | `PROJECT_ROOT` (C02) | MAJOR |
| `os.makedirs(path, exist_ok=True)` | `ensure_directory(path)` (C02) | MAJOR |
| `.mkdir(parents=True, exist_ok=True)` | `ensure_directory(path)` (C02) | MAJOR |
| `platform.system()` | `detect_os()` (C03) | MAJOR |
| `yaml.safe_load(open(...))` | `initialise_config()` + `get_config()` (C04) | MAJOR |
| `sys.exit(1)` on error | `handle_error(exc, fatal=True)` (C05) | MAJOR |
| `os.path.exists(path)` | `file_exists()` / `dir_exists()` (C06) | MAJOR |
| `.exists()` on Path object | `file_exists()` / `dir_exists()` (C06) | MAJOR |
| `datetime.now()` / `date.today()` | `get_now()` / `get_today()` (C07) | MAJOR |
| `.strftime(fmt)` | `format_date(date, fmt)` / `as_str()` (C07) | MAJOR |
| `timedelta(days=6)` for week end | `get_end_of_week()` (C07) | MAJOR |
| `pd.read_csv(path)` | `read_csv_file(path)` (C09) | MAJOR |
| `df.to_csv(path)` | `save_dataframe(df, path)` (C09) | MAJOR |
| `json.load(f)` / `json.dump()` | `read_json()` / `save_json()` (C09) | MAJOR |
| `pdfplumber.open()` | `extract_pdf_text()` (C10) | MAJOR |
| `shutil.copy()` for backups | `create_backup()` (C11) | MAJOR |
| `snowflake.connector.connect()` | `connect_to_snowflake()` (C14) | MAJOR |
| `pickle.dump()` / `pickle.load()` | `save_cache()` / `load_cache()` (C15) | MAJOR |
| `ThreadPoolExecutor` / `ProcessPoolExecutor` | `run_in_parallel()` (C16) | MAJOR |
| `requests.get()` / `requests.post()` | `get_json()` / `api_request()` (C17) | MAJOR |
| `webdriver.Chrome()` | `get_chrome_driver()` (C18) | MAJOR |
| `build('drive', 'v3', credentials=...)` | `get_drive_service()` (C19) | MAJOR |
| `messagebox.showinfo()` | `show_info()` (C20) | MAJOR |

## Docstring Quality

- Every public function (listed in `__all__`) must have a docstring — MAJOR if missing
- Docstring must include at minimum: Description section
- Private functions (not in `__all__`) should have docstrings — MINOR if missing

## Type Hints

- All function parameters should have type hints — MINOR if missing
- All functions should have return type hints — MINOR if missing

## GUI-Specific Checks (if applicable)

| Check | Violation Level |
|-------|-----------------|
| Design layer (Gx0a) contains business logic | CRITICAL |
| Design layer (Gx0a) has `command=` on buttons | CRITICAL |
| Design layer (Gx0a) has `.bind()` calls | CRITICAL |
| Control layer (Gx0b) creates widgets (except header actions) | CRITICAL |
| Imports from G00a instead of G02a facade | CRITICAL |
| Raw hex colours instead of presets | MAJOR |
| Magic numbers instead of SPACING_* constants | MAJOR |
| Widget references without type aliases | MINOR |

---

## OUTPUT FORMAT

For each violation found, report:
```
❌ [PASS 1/2] [RULE] Line X: Description of violation
   Severity: CRITICAL / MAJOR / MINOR
   Fix: What should be done instead
```

End with:
```
════════════════════════════════════════
AUDIT SUMMARY
════════════════════════════════════════
Pass 1 (Mechanical): X violations
Pass 2 (Semantic):   Y violations
────────────────────────────────────────
Total: X+Y (A critical, B major, C minor)
Verdict: PASS / FAIL
════════════════════════════════════════
```
```

---

## Section 1 Template Reference

**IMPORTANT:** Section 1 has TWO variants based on file location depth.

### Variant A: Files at root or `implementation/` (2 levels to project root)
```python
# --- Ensure project root DOES NOT override site-packages --------------------------------------------
project_root = str(Path(__file__).resolve().parent.parent)
```

### Variant B: Files in `implementation/subfolder/` (3 levels to project root)
```python
# --- Ensure project root DOES NOT override site-packages --------------------------------------------
# Note: .parent.parent.parent because this file is in implementation/subfolder/
project_root = str(Path(__file__).resolve().parent.parent.parent)
```

### Complete Section 1 Template (Variant B — nested files)

```python
# ====================================================================================================
# 1. SYSTEM IMPORTS
# ----------------------------------------------------------------------------------------------------
# These imports (sys, pathlib.Path) are required to correctly initialise the project environment,
# ensure the core library can be imported safely (including C00_set_packages.py),
# and prevent project-local paths from overriding installed site-packages.
# ----------------------------------------------------------------------------------------------------

# --- Future behaviour & type system enhancements -----------------------------------------------------
from __future__ import annotations           # Future-proof type hinting (PEP 563 / PEP 649)

# --- Required for dynamic path handling and safe importing of core modules ---------------------------
import sys                                   # Python interpreter access (path, environment, runtime)
from pathlib import Path                     # Modern, object-oriented filesystem path handling

# --- Ensure project root DOES NOT override site-packages --------------------------------------------
# Note: .parent.parent.parent because this file is in implementation/subfolder/
project_root = str(Path(__file__).resolve().parent.parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)

# --- Remove '' (current working directory) which can shadow installed packages -----------------------
if "" in sys.path:
    sys.path.remove("")

# --- Prevent creation of __pycache__ folders ---------------------------------------------------------
sys.dont_write_bytecode = True
```

### Complete Section 2 Template

```python
# ====================================================================================================
# 2. PROJECT IMPORTS
# ----------------------------------------------------------------------------------------------------
# Bring in shared external and standard-library packages from the central import hub.
#
# CRITICAL ARCHITECTURE RULE:
#   ALL external (and commonly-used standard-library) packages must be imported exclusively via:
#       from core.C00_set_packages import *
#   No other script may import external libraries directly.
#
# This module must not import any GUI packages.
# ----------------------------------------------------------------------------------------------------
from core.C00_set_packages import *

# --- Initialise module-level logger -----------------------------------------------------------------
from core.C01_logging_handler import get_logger, log_exception, init_logging
logger = get_logger(__name__)

# --- Additional project-level imports (append below this line only) ---------------------------------
# ... your imports here ...
```

⚠️ **Section 1 and Section 2 are LOCKED. Every comment must match exactly. Spacing must match exactly.**

---

## Quick Audit (Two-Pass)

For fast manual checks, use this abbreviated version:

### Pass 1: Mechanical (30 seconds)
```
Grep for MISSING required patterns (expect 1+ match each):

Section 1:
□ "# --- Future behaviour & type system enhancements"
□ "# --- Required for dynamic path handling"
□ "# --- Ensure project root DOES NOT override"
□ "# --- Remove '' (current working directory)"
□ "# --- Prevent creation of __pycache__"
□ "# Note: .parent.parent.parent because" (nested files only)

Section 2:
□ "# --- Initialise module-level logger"
□ "# --- Additional project-level imports"
□ "logger = get_logger(__name__)"

Section 98/99:
□ "__all__ = ["
□ "def main("
□ "init_logging("

FAIL if ANY are missing.
```

### Pass 2: Anti-Patterns (60 seconds)
```
Grep for PRESENT violation patterns (expect 0 matches each):

□ "print(" → CRITICAL
□ "import pandas" → CRITICAL
□ "import datetime" (standalone) → CRITICAL
□ "\.exists()" → MAJOR (use file_exists/dir_exists)
□ "\.mkdir(" → MAJOR (use ensure_directory)
□ "datetime\.now()" → MAJOR (use get_now)
□ "\.strftime(" → MAJOR (use format_date)
□ "pd\.read_csv(" → MAJOR (use read_csv_file)
□ "\.to_csv(" → MAJOR (use save_dataframe)
□ "timedelta(" → MAJOR (check if C07 has function)
□ "from core.C03_" for logging → CRITICAL (must be C01)

FAIL if ANY CRITICAL or MAJOR found.
```

---

## GUI-Only Audit

For GUI files specifically:

```
Audit this GUI file for PyBaseEnv compliance:

1. Imports from G02a facade only? (no G00a imports in Gx0+ pages)
2. Type aliases used? (WidgetType, EntryType, ButtonType, not tk.Entry)
3. Design layer (Gx0a):
   - No command= parameters on buttons?
   - No .bind() calls?
   - No business logic?
4. Control layer (Gx0b):
   - No widget creation (except header actions)?
   - Events wired in _wire_events()?
5. No magic numbers? (uses SPACING_SM, SPACING_MD, etc.)
6. No raw hex colours? (uses colour presets)

Report violations with line numbers.
```

---

## Documentation Audit

For Markdown documentation files:

```
Audit this documentation file:

1. Has a clear title (# heading)?
2. Has a purpose statement near the top?
3. No TODO or FIXME placeholders left in?
4. No broken internal links (references to files that don't exist)?
5. Code examples follow PyBaseEnv conventions?
6. Tables are properly formatted?
7. Section structure is logical and navigable?

Report issues with line numbers.
```

---

## Self-Audit Checklist

Before submitting code, verify ALL of these:

### Pass 1: Mechanical Checks
```
□ Section 1 has ALL 11 required lines (see table above)
□ Section 1 has Note comment if file is nested
□ Section 1 uses correct .parent count for file depth
□ Section 2 has ALL 8 required lines (see table above)
□ Section 98 exists with __all__ = [...]
□ Section 99 exists with def main() and if __name__ guard
□ init_logging() called before main()
□ No print() statements anywhere
□ No standalone external imports (pandas, datetime, json, os, requests)
□ Logging imports from C01 (not C03)
```

### Pass 2: Semantic Checks
```
□ No patterns from A04_anti_patterns.md detected
□ All public functions have docstrings
□ All functions have type hints
□ Core functions used where available (not reimplemented)
□ Exception handling uses log_exception()
```

### GUI Additional Checks (if applicable)
```
□ Design/Control separation respected
□ Imports from G02a facade only
□ No command= or .bind() in design layer
□ No widget creation in control layer
□ Widget references use type aliases
□ ControlledPage wrapper used for registration
```

---

## Self-Audit Commands (Copy-Paste Ready)

Run these terminal commands to verify compliance:

### Verify Section 1/2 Structure (expect 1 for each)
```bash
grep -c "# --- Future behaviour" FILE.py
grep -c "# --- Required for dynamic path" FILE.py
grep -c "# --- Ensure project root" FILE.py
grep -c "# --- Remove ''" FILE.py
grep -c "# --- Prevent creation" FILE.py
grep -c "# --- Initialise module-level" FILE.py
grep -c "# --- Additional project-level" FILE.py

# For nested files only (expect 1):
grep -c "# Note:.*parent.*parent.*parent" FILE.py
```

### Verify No Anti-Patterns (expect 0 for each)
```bash
grep -c "^import pandas" FILE.py
grep -c "^import datetime" FILE.py
grep -c "^import json" FILE.py
grep -c "^import os" FILE.py
grep -c "print(" FILE.py
grep -c "\.exists()" FILE.py
grep -c "\.mkdir(" FILE.py
grep -c "pd\.read_csv(" FILE.py
grep -c "\.to_csv(" FILE.py
grep -c "from core\.C03_" FILE.py
```

### Verify Required Patterns (expect 1+ for each)
```bash
grep -c "__all__" FILE.py
grep -c "def main(" FILE.py
grep -c "init_logging(" FILE.py
grep -c "logger = get_logger" FILE.py
```

---

**You have completed the mandatory reading.** Next: read `api/core_quick_lookup.md` (and `gui_quick_lookup.md` for GUI) to know what functions exist. Then implement your task, audit using the two-pass process above, and only deliver when PASS is achieved.
