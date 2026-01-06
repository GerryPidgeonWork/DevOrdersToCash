# A01 — Rules

> **Non-negotiable principles and hard rules.** Violations are failures.

---

## Governing Principles

These principles define **why** the rules exist. Understand them before reading the rules.

> **Note:** This document defines *rules only*. All process, traversal, and failure-handling behaviour is defined normatively in `A00_start_here.md`.

### 1. Determinism Over Flexibility

Every script must behave identically regardless of who writes it. Architecture eliminates variation. Personal style is not permitted.

### 2. Reuse Over Reinvention

If a Core function exists, use it. Do not write alternatives, wrappers, or “improved” versions. The framework is the single source of implementation.

### 3. Explicit Over Implicit

All imports are declared. All dependencies are visible. All sections are numbered. Nothing is hidden or magical.

### 4. Isolation Over Coupling

Layers do not reach into each other. Dependencies flow one direction only. Modules do not know about modules above them.

### 5. Safety Over Convenience

No side-effects at import time. No global state mutation. No runtime surprises. A module can be imported without executing business logic.

---

## Hard Rules — Import Architecture

### Rule I-1: External Packages via Hub Only

All external **and standard library** packages MUST be imported via the central hub:

```python
from core.C00_set_packages import *
```

**Forbidden:**

```python
import pandas as pd           # VIOLATION
from datetime import datetime # VIOLATION
import requests               # VIOLATION
```

**Why:** Guarantees consistent dependency availability. Enables global version control. Prevents import fragmentation.

---

### Rule I-1.a: Bootstrap Import Exception

The following standard library imports are permitted **only** for the purpose of establishing safe import paths for Core modules:

* `import sys`
* `from pathlib import Path`

**Conditions:**

* Usage must be limited strictly to path resolution and `sys.path` configuration
* Logic may appear **only in top-level entry-point or implementation modules**
* No business logic or runtime configuration may execute at import time
* The exception must be documented with an inline comment explaining its purpose

This exception exists solely to allow Core bootstrapping and does not permit general standard-library imports elsewhere.

---

### Rule I-2: GUI Packages via Facade Only

GUI framework modules (G00–G04) import GUI packages via:

```python
from gui.G00a_gui_packages import tk, ttk
```

GUI page modules (Gx0+) MUST import via the **G02a facade only**:

```python
from gui.G02a_widget_primitives import (
    WidgetType, EntryType, ButtonType, StringVar,
    make_label, make_button, make_entry,
)
```

**Forbidden in Gx0+ pages:**

```python
import tkinter as tk                    # VIOLATION
from tkinter import ttk                 # VIOLATION
from gui.G00a_gui_packages import tk    # VIOLATION — use G02a facade
```

**Why:** G02a is the facade layer. If Tkinter is ever replaced, only G02a changes. Pages never touch raw tk/ttk.

---

### Rule I-3: Logger Initialisation Pattern

Every module MUST initialise logging using this exact pattern:

```python
from core.C03_logging_handler import get_logger, log_exception, init_logging
logger = get_logger(__name__)
```

**Why:** Ensures consistent log formatting. Enables centralised log management.

---

### Rule I-4: No Cross-Layer Imports

Modules MUST NOT import from higher-numbered modules in the same tier.

**Examples:**

* `C03` cannot import from `C04`
* `G01` cannot import from `G02`
* Lower layers cannot depend on higher layers

**Why:** Prevents circular dependencies and enforces architectural hierarchy.

---

## Hard Rules — Script Structure

### Rule S-1: Section Numbers Are Mandatory

Every script MUST contain these numbered sections **in order**:

| Section  | Purpose         |
| -------- | --------------- |
| **1**    | System Imports  |
| **2**    | Project Imports |
| **3–97** | Implementation  |
| **98**   | Public API      |
| **99**   | Main Execution  |

---

### Rule S-2: Required Bootstrap (Canonical)

Section **1** and Section **2** are **immutable protected regions**.

Their contents are defined **normatively** by:

* The templates in `.ai_instruction/templates/`, and
* The mechanical checks enforced by **`A03_audit.md`**

If there is **any discrepancy** between examples shown in documentation and the strings required by A03:

> **A03 takes precedence.**

You MUST copy these sections **exactly** from the template. Do not retype, shorten, or adapt them.

---

### Rule S-3: No Executable Code Outside Section 99

All runtime execution MUST occur inside the `main()` function guarded by:

```python
if __name__ == "__main__":
```

---

### Rule S-4: Public API Declaration

Every module MUST declare its public interface in Section **98** using `__all__`.

---

### Rule S-5: No Print Statements

Use logging, not `print()`.

---

### Rule S-6: Exception Logging

Use `log_exception()` for caught exceptions. Do not manually format tracebacks.

---

## Hard Rules — Templates

### Rule T-1: All Scripts From Templates

Every new Python file MUST originate from a template in `.ai_instruction/templates/`.

---

### Rule T-2: Placeholder Replacement

All `{{PLACEHOLDER}}` markers MUST be replaced before delivery.

---

### Rule T-3: Delete Instruction Block

Template instruction blocks MUST be removed before delivery.

---

## Hard Rules — Naming Conventions

### Rule N-1: File Naming

Core, GUI framework, and page files MUST follow the documented naming scheme.

**Authoritative references:**

* `.ai_instruction/templates/project_structures.md`
* `api/gui_pages.md`

---

### Rule N-2: Class Naming

Class names MUST follow the documented patterns.

**Authoritative references:**

* `api/gui_pages.md`
* `api/gui_foundation.md`

---

### Rule N-3: Function Naming

Use `snake_case` for functions.

---

### Rule N-4: No Renaming

Never rename Core or GUI public symbols. Names are permanent.

---

## Enforcement

### Rule Precedence (Highest First)

1. `.ai_instruction/` governance files (A00–A04)
2. User requests
3. Convenience or stylistic preferences

---

### Audit Authority and Error Handling

Compliance is enforced mechanically by **`A03_audit.md`**.

If you believe the audit itself is incorrect, inconsistent, or contains an error:

* Do NOT bypass or weaken the audit
* Do NOT silently fail or loop indefinitely
* You MUST explicitly flag the issue to the user and explain the inconsistency

Only the user may authorise changes to audit rules.

---

### User Override Policy

Users MAY request delivery of code that violates governance rules.

Such requests:

* MUST be explicitly acknowledged as non-compliant
* MUST list the violated rule(s)
* MUST record that the user has accepted the resulting technical debt

Absent explicit acknowledgement, **governance rules override user requests**.
