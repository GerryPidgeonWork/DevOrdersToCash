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
| CRITICAL | Wrong imports, missing bootstrap, code outside Section 99, no logger | Must fix before delivery |
| MAJOR | Missing `__all__`, missing docstrings, wrong template structure | Must fix before delivery |
| MINOR | Naming style, formatting, missing Notes in docstring | Note and fix if time permits |

**Minor violations policy:**
- MINOR issues are acceptable for delivery if user is time-constrained
- MINOR issues are NOT acceptable in new Core modules (C00–C20) or GUI framework (G00–G04)
- Always note any MINOR issues in your response, even if not fixed

**Critical violations include:**
- Bypassing C00_set_packages for external imports
- Bypassing G02a facade in Gx0+ pages
- Missing or modified Section 1 bootstrap
- Executable code outside Section 99
- Missing logger initialisation
- Business logic in Gx0a design layer
- Widget creation in Gx0b control layer
- Missing `__all__` declaration
- No docstrings on public functions

---

## Audit Prompt

```
Audit this Python file against PyBaseEnv coding standards. Report ALL violations with line numbers.

## STRUCTURAL CHECKS

□ Section 1 (System Imports) — Must contain exact bootstrap:
  - `from __future__ import annotations`
  - `import sys`
  - `from pathlib import Path`
  - project_root setup
  - sys.path manipulation
  - `sys.dont_write_bytecode = True`
  
□ Section 2 (Project Imports) — Must contain:
  - `from core.C00_set_packages import *`
  - `from core.C01_logging_handler import get_logger, log_exception, init_logging`
  - `logger = get_logger(__name__)`

□ Sections numbered correctly: 1, 2, 3, 98, 99 (no other section numbers)

□ Section 98 contains `__all__ = [...]`

□ Section 99 contains:
  - `def main()` function
  - `if __name__ == "__main__":` block
  - `init_logging()` call

□ No executable code outside Section 99 (no module-level function calls, no print statements, no object instantiation)

## IMPORT CHECKS

□ No direct external imports (pandas, requests, datetime, json, etc. must come from C00)
□ No `import tkinter` or `from tkinter import` (must use G00a or G02a)
□ No imports from higher-numbered modules (C03 cannot import C05, G01 cannot import G02)
□ GUI pages (Gx0+) import from G02a only, never G00a

## CODE QUALITY CHECKS

□ No `print()` statements (use logger.info, logger.debug, etc.)
□ All public functions have docstrings with Description section
□ All functions have type hints (parameters and return type)
□ Exception handling uses `log_exception()` not bare `except:`
□ No magic numbers in GUI code (must use SPACING_*, colour presets)

## GUI-SPECIFIC CHECKS (if applicable)

□ Design layer (Gx0a) contains no business logic
□ Design layer (Gx0a) contains no event handler wiring (no `command=`, no `.bind()`)
□ Control layer (Gx0b) creates no widgets (except header action buttons)
□ Widget references use type aliases (EntryType, ButtonType, etc.)
□ No raw hex colours (use colour presets)

## OUTPUT FORMAT

For each violation found, report:
- ❌ [RULE] Line X: Description of violation
- Severity: CRITICAL / MAJOR / MINOR

(See "Severity definitions" table above for classification)

End with:
- Total violations: X (Y critical, Z major, W minor)
- Verdict: PASS (0 critical, 0 major) / FAIL
```

---

## Quick Audit (Abbreviated)

For fast checks, use this shorter version:

```
Quick audit this Python file:
1. Imports via C00_set_packages? (no direct pandas/requests/datetime)
2. Logger initialised with get_logger(__name__)?
3. Sections numbered 1, 2, 3, 98, 99?
4. No code outside Section 99?
5. No print() statements?
6. All public functions have docstrings?
7. __all__ declared in Section 98?

Report violations with line numbers.
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

## Self-Audit Reminder

Before submitting code, developers should verify:

- [ ] Started from correct template
- [ ] All `{{PLACEHOLDER}}` values replaced
- [ ] Template instruction block deleted
- [ ] Imports follow hub architecture
- [ ] Logger initialised
- [ ] No print() statements
- [ ] Docstrings on all public functions
- [ ] `__all__` declared in Section 98
- [ ] No side-effects at import time

For GUI additionally:

- [ ] Design/Control separation respected
- [ ] Imports from G02a facade only
- [ ] Widget references use type aliases
- [ ] ControlledPage wrapper used for registration

---

**You have completed the mandatory reading.** Next: read `api/core_quick_lookup.md` (and `gui_quick_lookup.md` for GUI) to know what functions exist. Then implement your task, audit against the checks above, and only deliver when PASS is achieved.
