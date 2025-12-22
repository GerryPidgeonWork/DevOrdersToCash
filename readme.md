# PyBaseEnv

A production-ready Python project framework with strict architectural governance, reusable Core utilities, and an optional GUI layer built on Tkinter/ttk.

---

## What is PyBaseEnv?

PyBaseEnv is a **boilerplate framework** designed for building maintainable Python applications. It provides:

- **Core Library (C00–C20):** Battle-tested utilities for logging, file I/O, validation, API calls, data processing, and more
- **GUI Framework (G00–G04):** A layered Tkinter/ttk system with design tokens, widget factories, and page patterns
- **AI Governance System:** Machine-readable documentation that enables AI coding assistants to work within strict architectural boundaries

The framework enforces consistency through templates, import rules, and a clear separation of concerns.

---

## Key Features

| Feature | Description |
|---------|-------------|
| **Centralised Imports** | All external packages flow through `C00_set_packages.py` — one place to manage dependencies |
| **Structured Logging** | Built-in logger with file rotation, exception handling, and no `print()` statements |
| **Validation Utilities** | Consistent patterns: `validate_*` raises, `*_exists` returns bool |
| **GUI Design System** | Design tokens, spacing scale, colour families — change theme in one place |
| **Page Architecture** | Clean separation: Gx0a (design/presentation) + Gx0b (controller/logic) |
| **AI-Ready Documentation** | `.ai_instruction/` folder enables AI assistants to follow project rules automatically |

---

## Project Structure

```
PyBaseEnv/
├── .ai_instruction/          # AI governance (read-only contract)
│   ├── A00_start_here.md     # Entry point for AI assistants
│   ├── A01_rules.md          # Non-negotiable rules
│   ├── A02_process.md        # Workflow requirements
│   ├── A03_audit.md          # Code review checklist
│   └── api/                  # Function reference documentation
│
├── core/                     # Reusable utilities (C00–C20)
│   ├── C00_set_packages.py   # External package hub
│   ├── C01_logging_handler.py
│   ├── C02_set_file_paths.py
│   └── ...
│
├── gui/                      # GUI framework + pages (G00–G04, Gx0)
│   ├── G00a_gui_packages.py  # Tkinter/ttk import hub
│   ├── G01a_style_config.py  # Design tokens
│   ├── G02a_widget_primitives.py  # Widget factories (THE FACADE)
│   ├── G03a_layout_patterns.py
│   ├── G04d_app_shell.py     # Application shell
│   ├── Gx0a_design_template.py    # Page design template
│   └── Gx0b_control_template.py   # Page controller template
│
├── implementation/           # Project-specific business logic
├── main/                     # Application entry points
├── config/                   # Configuration files
├── data/                     # Input/output data
├── outputs/                  # Generated deliverables
├── logs/                     # Runtime log files (auto-created)
├── templates/                # Script templates
│   └── script_templates.py
└── tests/                    # Automated tests
```

---

## Getting Started

### 1. Clone or Copy the Boilerplate

```bash
git clone <repository-url> MyProject
cd MyProject
```

### 2. Create Virtual Environment

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Create Your First Script

Copy the template and customise:

```bash
cp templates/script_templates.py implementation/my_script.py
```

Replace all `{{PLACEHOLDER}}` values and implement your logic in Section 3.

---

## Architecture Overview

### Core Library (C00–C20)

| Layer | Modules | Purpose |
|-------|---------|---------|
| Foundation | C00–C05 | Packages, logging, paths, config, errors |
| Utilities | C06–C13 | Validation, file I/O, dates, strings, PDF, backup, DataFrames |
| Integrations | C14–C20 | Snowflake, caching, parallel, REST API, Selenium, Google Drive |

**Import Rule:** All external packages come through `C00_set_packages.py`:

```python
from core.C00_set_packages import *
```

### GUI Framework (G00–G04)

| Layer | Purpose |
|-------|---------|
| G00 | Tkinter/ttk import hub |
| G01 | Design tokens (colours, spacing, typography) |
| G02 | Widget factories + layout utilities (**facade layer**) |
| G03 | Layout patterns, containers, forms, tables |
| G04 | AppShell, Navigator, AppState |

**Import Rule:** Pages import from `G02a_widget_primitives.py` only:

```python
from gui.G02a_widget_primitives import (
    make_frame, make_label, make_button,
    SPACING_MD, StringVar,
)
```

### Page Architecture (Gx0a/Gx0b)

Every GUI page is a **pair**:

| File | Responsibility |
|------|----------------|
| `Gx0a_*_design.py` | Visual layout, widget creation, NO event handlers |
| `Gx0b_*_controller.py` | Event wiring, validation, business logic, NO widget creation |

```
┌─────────────────────┐     ┌─────────────────────┐
│   Gx0a (Design)     │────▶│  Gx0b (Controller)  │
│                     │     │                     │
│ • Creates widgets   │     │ • Wires events      │
│ • Stores references │     │ • Implements logic  │
│ • Returns frame     │     │ • Updates UI state  │
└─────────────────────┘     └─────────────────────┘
```

---

## Script Structure

Every Python file follows this structure:

```python
# Section 1: System Imports (LOCKED)
from __future__ import annotations
import sys
from pathlib import Path
# ... bootstrap code ...

# Section 2: Project Imports (LOCKED)
from core.C00_set_packages import *
from core.C01_logging_handler import get_logger
logger = get_logger(__name__)

# Section 3–97: Implementation (FLEXIBLE)
# Your code here...

# Section 98: Public API Surface (LOCKED)
__all__ = ["my_function"]

# Section 99: Main Execution (LOCKED)
def main() -> None:
    logger.info("Running...")

if __name__ == "__main__":
    init_logging()
    main()
```

---

## Design Tokens

### Spacing Scale (4px grid)

| Token | Value |
|-------|-------|
| `SPACING_XS` | 4px |
| `SPACING_SM` | 8px |
| `SPACING_MD` | 16px |
| `SPACING_LG` | 24px |
| `SPACING_XL` | 32px |
| `SPACING_XXL` | 48px |

### Colours

**Background (`bg_colour`):** `PRIMARY`, `SECONDARY`, `SUCCESS`, `WARNING`, `ERROR`

**Foreground (`fg_colour`):** `BLACK`, `WHITE`, `GREY`, `PRIMARY`, `SECONDARY`, `SUCCESS`, `WARNING`, `ERROR`

**Shades (`bg_shade`):** `LIGHT`, `MID`, `DARK`, `XDARK`

---

## For AI Assistants

If you're an AI coding assistant, **start here:**

```
.ai_instruction/A00_start_here.md
```

This folder contains machine-readable governance that defines:

- Mandatory reading order
- Import rules and patterns
- Template requirements
- Audit checklists
- API documentation

**Do not write code until you have read the governance documents.**

---

## Creating New Files

### New Script (Non-GUI)

```bash
cp templates/script_templates.py implementation/my_script.py
```

### New GUI Page

```bash
cp gui/Gx0a_design_template.py gui/G10a_mypage_design.py
cp gui/Gx0b_control_template.py gui/G10b_mypage_controller.py
```

Then register with AppShell:

```python
app.register_page("mypage", ControlledMyPage)
```

---

## Quick Reference

### Common Core Functions

| Task | Function | Module |
|------|----------|--------|
| Get logger | `get_logger(__name__)` | C01 |
| Check file exists | `file_exists(path)` | C06 |
| Validate file exists | `validate_file_exists(path)` | C06 |
| Read JSON | `read_json(path)` | C07 |
| Write JSON | `write_json(path, data)` | C07 |
| HTTP GET | `get_json(url)` | C17 |
| HTTP POST | `post_json(url, payload)` | C17 |

### Common GUI Functions

| Task | Function | Module |
|------|----------|--------|
| Create frame | `make_frame(parent, padding="MD")` | G02a |
| Create label | `make_label(parent, text="...")` | G02a |
| Create button | `make_button(parent, text="...", command=...)` | G02a |
| Two-column layout | `two_column_layout(parent)` → `(outer, left, right)` | G03a |
| Page title | `page_title(parent, text="...")` | G02a |

---

## Author

**Gerry Pidgeon**

---

## License

[Your license here]