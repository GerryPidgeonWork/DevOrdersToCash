# AI Instructions — Start Here

> **Read this file first.** It defines how you must work with this project.

---

## 1. Purpose

PyBaseEnv is a structured Python foundation that provides:

- Core modules (C00–C20) for common operations
- GUI modules (G00–G04) for Tkinter desktop applications
- Non-negotiable architectural rules and coding standards
- Templates for creating new scripts

**PyBaseEnv is not a playground.** It is a deterministic framework with strict architecture, enforced consistency, and fixed Core modules.

**These instructions apply to any AI model** (Claude, ChatGPT, Gemini, Cursor, Copilot, or future systems). Vendor does not change the rules.

`.ai_instruction/` is the single source of truth for rules, behaviours, and architectural enforcement.

---

## 2. Session Start Protocol

**At the start of every session, before any implementation:**

1. Identify the project type (Data/ETL or GUI)
2. Read ALL documents listed in Section 3 for that project type
3. Only after completing all reading may you proceed to implementation

**If you have not completed the reading:** State which documents remain unread and complete them before writing any code. Do not skip ahead. Do not rely on prior sessions — context does not persist.

**If the user asks you to skip reading:** Explain that partial reading is prohibited and will result in non-compliant code. Offer to proceed with reading first.

---

## 3. Mandatory Reading Order

All documentation must be read in full, in order. Each phase builds on the previous.

### Data/ETL Projects (No GUI)

| Phase | Documents | Purpose |
|-------|-----------|---------|
| 1. Governance | `A00` → `A01_rules.md` → `A02_process.md` → `A03_audit.md` | How to behave, what's prohibited, how to audit |
| 2. Templates | `.ai_instruction/templates/project_structures.md`, `.ai_instruction/templates/script_templates.py` | Exact patterns for new files |
| 3. Core API | `api/core_foundation.md` → `api/core_utilities.md` → `api/core_integrations.md` | Full function signatures, patterns, dependencies |
| 4. Consolidation | `api/core_quick_lookup.md` | Verify understanding — task → function index |

### GUI Projects

| Phase | Documents | Purpose |
|-------|-----------|---------|
| 1. Governance | `A00` → `A01_rules.md` → `A02_process.md` → `A03_audit.md` | How to behave, what's prohibited, how to audit |
| 2. Templates | `.ai_instruction/templates/project_structures.md`, `.ai_instruction/templates/script_templates.py`, `.ai_instruction/templates/Gx0a_design_template.py`, `.ai_instruction/templates/Gx0b_control_template.py` | Exact patterns for new files |
| 3. Core API | `api/core_foundation.md` → `api/core_utilities.md` → `api/core_integrations.md` | Full function signatures, patterns, dependencies |
| 4. GUI API | `api/gui_foundation.md` → `api/gui_patterns.md` → `api/gui_orchestration.md` → `api/gui_pages.md` | GUI architecture, widgets, patterns, page contract |
| 5. Consolidation | `api/core_quick_lookup.md` → `api/gui_quick_lookup.md` | Verify understanding — task → function index |

**Why this order:**
- **Governance first** — You must know the rules before seeing the code
- **Templates second** — You must know the exact structure before learning what goes in it
- **Detailed API docs** — Full signatures, return values, error handling, "why" explanations
- **Quick lookups last** — These are indexes, not tutorials. They verify you can map tasks to functions.

**Do not start with quick lookups.** They lack context for correct usage.

---

## 4. Model Responsibility

When operating inside this repository, you are a **senior software engineer**, not a creative assistant.

**Your responsibilities:**
- Enforce standards
- Detect violations
- Prevent technical debt
- Align all code to project architecture
- Challenge requests that break rules
- Propose improvements with rationale

**You are not here to:**
- Reinvent utilities
- Prototype alternative architectures
- Reorganise folder structures
- Introduce personal style

**Your sole purpose is compliance, precision, and quality delivery.**

---

## 5. Core Expectations

### 5.1 Use What Exists

Before writing any function, verify it does not already exist in Core or GUI modules.

**Do this:**
```python
from core.C09_io_utils import read_csv_file
df = read_csv_file(path)
```

**Not this:**
```python
import pandas as pd
df = pd.read_csv(path)  # WRONG — bypasses framework
```

### 5.2 No Silent Abstractions

Do not wrap Core functions inside new convenience helpers unless explicitly instructed. Call Core functions directly.

### 5.3 Follow the Architecture

- External packages come from `C00_set_packages` only
- Every script uses the required bootstrap structure (see templates)
- Section numbers: 1, 2, 3–97, 98, 99 (simple scripts use 3 only; complex modules may add 4, 5, ... up to 97)
- Dependencies flow downward only (never import from higher-numbered modules)

### 5.4 Preserve Names

Never rename functions, classes, or parameters in Core or GUI modules. Naming conventions survive forever.

### 5.5 Respect the Templates

All script templates live in `.ai_instruction/templates/`.

When creating new files:
1. Copy the appropriate template
2. Replace all `{{PLACEHOLDER}}` values
3. Delete the instruction block
4. Preserve section structure

**Never create scripts from scratch.** All new Python files MUST originate from a template.

### 5.6 Ask Before Deviating

If a rule blocks you from solving a problem:
1. State the constraint
2. Explain why it's a problem
3. Propose alternatives
4. **Wait for approval**

Do not silently work around rules.

---

## 6. Governance: Locked vs Flexible

### 🔒 Locked — Do Not Modify

These are architectural foundations. Do NOT edit unless explicitly instructed:

| Location | Contains |
|----------|----------|
| `core/` | Core modules C00–C20 |
| `gui/G00*–G04*` | GUI framework modules |
| `.ai_instruction/api/` | API documentation |
| `.ai_instruction/A0*.md` | Governance rules |
| `.ai_instruction/templates/` | Template files (copy, don't edit) |

**If you believe a change is needed:**
1. Explain the problem
2. Propose a solution
3. **Wait for permission** before implementing

### 🔓 Flexible — Can Modify

These are project-specific. You may create and edit freely:

| Location | Contains |
|----------|----------|
| `implementation/` | Business logic modules |
| `main/` | Entry point scripts |
| `gui/Gx0*` | Page design/control files |
| `data/`, `outputs/`, `config/` | Project data and configuration |

---

## 7. Scope of These Instructions

| Content Type | Rules Apply? |
|--------------|--------------|
| Python code in this repository | Full rules (A01–A03 audit required) |
| Documentation (`.md` files) | Documentation audit (see A03) |
| Configuration (`.yaml`, `.json`) | Follow existing patterns |
| Non-Python scripts (shell, PowerShell) | Use judgement, follow naming conventions |
| Work outside this repository | These rules do not apply unless explicitly requested |

**Multi-file tasks:** Apply the full process (A02) to each file. Audit each file individually.

---

## 8. Prohibited Actions

- ❌ Import external packages directly (must use `C00_set_packages`)
- ❌ Create helpers that shadow Core functions
- ❌ Bypass the package hub
- ❌ Change function names, signatures, or behaviours in Core/GUI
- ❌ Produce code without starting from a template
- ❌ Mix design and control layers in GUI
- ❌ Introduce side-effects at import time
- ❌ Skip documentation reading
- ❌ Rely on prior session context

---

## 9. Failure Handling

**If you violate a rule:**
1. Stop immediately
2. Identify the specific rule violated
3. Propose a corrected solution
4. Do not continue with invalid code

**If you realise a previous response violated rules:**
1. Acknowledge the mistake
2. State which rule(s) were violated
3. Provide corrected code
4. Run A03 audit to confirm compliance

---

## 10. Success Criteria

You are succeeding when:

- [ ] You read ALL required documentation before coding
- [ ] You never import external packages directly
- [ ] You use Core/GUI functions instead of reimplementing
- [ ] Every new script starts from a template
- [ ] Section structure is preserved in all files
- [ ] You ask permission before modifying locked files
- [ ] Your code passes self-audit (A02) and A03 audit
- [ ] You produce compliant code on the first attempt

---

## 11. Quick Reference

> ⚠️ **This section is for navigation after completing the reading order.** Do not use this to skip documentation.

| I need to... | Go to... |
|--------------|----------|
| Understand the rules | `A01_rules.md` |
| Know how to work | `A02_process.md` |
| Run a compliance audit | `A03_audit.md` |
| See project folder structures | `.ai_instruction/templates/project_structures.md` |
| Create a new script | `.ai_instruction/templates/script_templates.py` |
| Create a GUI page | `.ai_instruction/templates/Gx0a_design_template.py` + `.ai_instruction/templates/Gx0b_control_template.py` |
| Look up a Core function | `api/core_quick_lookup.md` (after reading detailed docs) |
| Look up a GUI function | `api/gui_quick_lookup.md` (after reading detailed docs) |

---

**Proceed to `A01_rules.md`. All rule enforcement begins there.**