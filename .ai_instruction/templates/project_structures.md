# Project Folder Structure — Roles & Rules

> **Purpose:** Defines all folders in the project tree with precise descriptions, rules, and intent.
> This document is the authoritative reference for where files belong.

---

## 1. Quick Placement Guide

| I need to create... | Put it in... |
|---------------------|--------------|
| A reusable utility function | `core/` |
| A data processing pipeline | `implementation/` |
| A new GUI page | `gui/` (Gx0a design + Gx0b controller) |
| A styled widget or layout pattern | `gui/` (G02–G03) |
| Navigation/state/AppShell logic | `gui/` (G04) |
| A one-off test script | `scratchpad/` |
| An exported report or deliverable | `outputs/` |
| A SQL query | `sql/` |
| App config settings | `config/` |
| The main launcher | `main/` |
| Automated tests | `tests/` |
| Internal documentation | `tech_docs/` |
| User-facing guides | `user_guides/` |
| AI governance rules | `.ai_instruction/` |
| Script templates | `templates/` |

---

## 2. Folder Requirements

| Folder | Required | Created When | Notes |
|--------|:--------:|-----------|-------|
| `.ai_instruction/` | ✅ | Project init | AI governance |
| `.venv/` | ✅ | Project init | Never committed |
| `core/` | ✅ | Project init | C00–C20 modules |
| `config/` | ✅ | Project init | Settings, schemas |
| `logs/` | ✅ | Runtime (auto) | Log files |
| `main/` | ✅ | Project init | Entry points |
| `implementation/` | ✅ | Project init | Business logic |
| `outputs/` | ✅ | Project init | Final deliverables |
| `data/` | ✅ | Project init | Input/output data |
| `templates/` | ✅ | Project init | Script templates |
| `gui/` | ⬜ | If GUI project | G00–G04, pages |
| `sql/` | ⬜ | If database project | Query files |
| `tests/` | ⬜ | If testing required | pytest modules |
| `tech_docs/` | ⬜ | As needed | Internal docs |
| `user_guides/` | ⬜ | As needed | Stakeholder docs |
| `credentials/` | ⬜ | If auth required | Always .gitignore |
| `cache/` | ⬜ | Runtime (auto) | Ephemeral |
| `binary_files/` | ⬜ | If PyInstaller used | Compiled outputs |
| `scratchpad/` | ⬜ | Developer choice | Disposable |

---

## 3. GUI Layer Mapping

For GUI projects, layers map to folders as follows:

| Layer | Location | Contains |
|-------|----------|----------|
| G00 | `gui/` | `G00a_gui_packages.py` — tk/ttk import hub |
| G01 | `gui/` | `G01a_style_config.py`, `G01b_style_base.py`, `G01c_text_styles.py`, `G01d_container_styles.py`, `G01e_input_styles.py`, `G01f_control_styles.py` |
| G02 | `gui/` | `G02a_widget_primitives.py` (facade), `G02b_layout_utils.py`, `G02c_gui_base.py` |
| G03 | `gui/` | `G03a_layout_patterns.py`, `G03b_container_patterns.py`, `G03c_form_patterns.py`, `G03d_table_patterns.py`, `G03e_widget_components.py`, `G03f_renderer.py` |
| G04 | `gui/` | `G04a_app_state.py`, `G04b_navigator.py`, `G04c_app_menu.py`, `G04d_app_shell.py` |
| Gx0a | `gui/` | `Gx#a_name_design.py` (e.g., `G10a_main_design.py`) |
| Gx0b | `gui/` | `Gx#b_name_controller.py` (e.g., `G10b_main_controller.py`) |
| C00–C20 | `core/` | Shared utilities, logging, validation |

**Numbering scheme for pages:**
- `G1x` = GUI 1 pages (G10a/b, G11a/b, G12a/b, ...)
- `G2x` = GUI 2 pages (G20a/b, G21a/b, G22a/b, ...)
- Up to `G9x` = GUI 9 pages

---

## 4. Folder Descriptions

### `.ai_instruction/`

AI governance and behavioural rules for all AI assistants working in this repository.

- `A00_start_here.md` — Entry point and orientation
- `A01_rules.md` — Non-negotiable principles and hard rules
- `A02_process.md` — Workflow and audit procedures
- `api/` — Function reference documentation:
  - `core_foundation.md`, `core_utilities.md`, `core_integrations.md` — Core API docs
  - `core_quick_lookup.md` — Task-based Core function index
  - `gui_foundation.md`, `gui_patterns.md`, `gui_orchestration.md`, `gui_pages.md` — GUI API docs
  - `gui_quick_lookup.md` — Task-based GUI function index
- `architecture/` — Dependency rules, layer definitions, protocols
- `rules/` — Coding rules, style rules, audit prompts
- `templates/` — Script templates

**Rules:**
- Locked — do not modify without explicit permission
- All AI assistants must read before writing code
- Single source of truth for rules and behaviours

---

### `.venv/`

Local Python virtual environment.

- Never committed to Git
- Contains interpreter and installed packages
- No project files stored here

---

### `binary_files/`

Compiled or frozen application outputs — primarily **PyInstaller results**.

- `.exe`, `.app`, `dist/`, support binaries
- Ephemeral and replaceable
- Do not store PDFs/data here

---

### `cache/`

Temporary runtime artefacts that can be deleted safely:

- Downloaded temp files
- Cached API responses
- Intermediate CSV/JSON snapshots

**Rules:**
- No handwritten files
- No source code

---

### `config/`

Static configuration inputs:

- YAML/JSON config files
- Application settings
- Schema definitions

**Rules:**
- No code
- No credentials

---

### `core/`

Permanent, reusable, architecture-locked library modules (`C00–C20`).

- Shared utilities
- Logging, IO, validation
- Datetime, strings, audit, Snowflake, automation

**Rules:**
- No project-specific hacks
- No GUI logic
- Modules must be generic and reusable
- `core/` never imports from `gui/` or `implementation/`

---

### `credentials/`

Secret authentication material:

- OAuth files
- Service account JSON
- Connection secrets

**Rules:**
- Always `.gitignore`
- Never hard-coded
- Never referenced directly in commits

---

### `data/`

Project input-output data:

- Raw CSV/XLSX drops
- Interim data exports
- Curated datasets

**Rules:**
- No code
- Not a general binary store

---

### `gui/`

Primary location for **GUI design and project UI**, including G00–G04 framework modules:

- G00: Package hub (tk/ttk imports)
- G01: Design tokens, style engine
- G02: Widget factories, layout utilities — **G02a is the facade for Gx0+ pages**
- G03: Layout patterns, form patterns, table patterns, renderer
- G04: AppShell, navigation, state management

**Rules:**
- No business logic
- No file processing
- Visual and interaction layer only
- G00–G04 framework modules and Gx0a/Gx0b pages coexist in flat structure
- **Gx0+ pages import from G02a only** — never from G00a directly
- `gui/` may depend on `core/`, but never on `implementation/`
- No modules outside `gui/` may import `gui/` — GUI is self-contained

---

### `implementation/`

All **project execution logic** that is not GUI and not part of `core/`.
This is the operational backbone of the project.

Contains:

- Ingestion/transformation pipelines
- Reconciliation logic
- Business workflows
- Data automation
- Project utilities

**Rules:**
- If something becomes generic → promote to `core/`
- `implementation/` may depend on `core/` only
- `implementation/` must never import from `gui/`

---

### `logs/`

Runtime log files generated by the logging system.

- Daily log files (e.g., `2025-01-15.log`)
- Exception traces
- Execution audit trails

**Rules:**
- Auto-created by `C01_logging_handler.py`
- Do not store manually-written files here
- Can be cleared safely (ephemeral)

---

### `main/`

Application entry points only:

- CLI launchers
- GUI bootstrap scripts
- Orchestration wrappers

**Rules:**
- No business logic here
- Thin wrappers that call into `implementation/` or `gui/`

---

### `outputs/`

Permanent, saved project artefacts:

- Exported reports
- XLSX/CSV deliverables
- PDFs generated by the project

**Rules:**
- Not ephemeral — this is the "final deliverables" space
- User-facing outputs only

---

### `scratchpad/`

Developer sandbox for experiments:

- Prototype code
- Quick tests
- Throwaway utilities
- Notebooks

**Rules:**
- Not imported anywhere
- No standards required
- Disposable
- Nothing in `scratchpad/` is ever imported by production code

---

### `sql/`

SQL assets:

- Snowflake query files
- DDL/DML
- Transformation logic

**Rules:**
- No CSV/XML here
- Credentials never embedded

---

### `tech_docs/`

Internal engineering documentation:

- Architecture briefs
- Standards
- Diagrams
- Development guides

**Rules:**
- Not user-facing
- Written for engineers
- Not a dumping ground for undocumented schema — schema lives in `sql/`

---

### `templates/`

Script templates for creating new Python files.

- `script_templates.py` — General non-GUI scripts

**GUI templates in `gui/` folder:**
- `Gx0a_design_template.py` — GUI design layer template (copy for new pages)
- `Gx0b_control_template.py` — GUI control layer template (copy for new pages)

**Rules:**
- Copy templates, do not edit originals
- All new Python files must originate from a template
- See `A01_rules.md` Rule T-1

---

### `tests/`

Automated testing suite:

- pytest modules
- Fixtures
- Coverage configuration

**Rules:**
- No production code

---

### `user_guides/`

Business-facing documentation:

- How-to instructions
- Process guides
- Screenshots
- "Steps to run" notes

**Rules:**
- Written for stakeholders, not engineers

---

## 5. Project Initialisation

### 5.1 Minimal Project (Non-GUI)

```bash
mkdir -p .ai_instruction/api core config data implementation logs main outputs templates tests
touch core/__init__.py
touch implementation/__init__.py
touch main/__init__.py
```

### 5.2 Full Project (With GUI)

```bash
mkdir -p .ai_instruction/api core config data gui implementation logs main outputs sql tech_docs templates tests user_guides
touch core/__init__.py
touch gui/__init__.py
touch implementation/__init__.py
touch main/__init__.py
```

### 5.3 Required Base Files

After folder creation, copy these from the boilerplate:

| File | Location | Purpose |
|------|----------|---------|
| `A00_start_here.md` | `.ai_instruction/` | AI entry point |
| `A01_rules.md` | `.ai_instruction/` | AI governance rules |
| `A02_process.md` | `.ai_instruction/` | AI workflow process |
| `api/*.md` | `.ai_instruction/api/` | API documentation |
| `C00_set_packages.py` | `core/` | External package hub |
| `C01_logging_handler.py` | `core/` | Logging infrastructure |
| `script_templates.py` | `templates/` | General script template |
| `G00a_gui_packages.py` | `gui/` | GUI package hub (if GUI project) |
| `G01*–G04*` | `gui/` | GUI framework modules (if GUI project) |

---

## 6. Script Section Numbers

**Standard structure:** 1, 2, 3, 98, 99 (simple scripts)

**Extended structure:** 1, 2, 3–97, 98, 99 (complex modules)

- Sections 1, 2, 98, 99 are LOCKED (exact structure required)
- Section 3 is the minimum implementation section
- Sections 4–97 are OPTIONAL for complex modules requiring logical separation
- See `A01_rules.md` for section format requirements

---

## 7. Anti-Patterns — Common Misplacements

| Wrong | Right | Why |
|-------|-------|-----|
| Utility function in `implementation/` | Move to `core/` | If reusable, it belongs in core |
| Business logic in `gui/` | Move to `implementation/` | GUI is presentation only |
| Credentials in `config/` | Move to `credentials/` | Secrets must be isolated |
| Test script in `core/` | Move to `tests/` or `scratchpad/` | Core is production code only |
| Entry point logic in `main/` | Move to `implementation/` | Main is thin wrappers only |
| AI rules in `tech_docs/` | Move to `.ai_instruction/` | AI governance is separate |
| Templates in `core/` | Move to `templates/` | Templates are not runtime code |

---

## 8. Summary Table

| Folder | Purpose |
|--------|---------|
| `.ai_instruction` | AI governance and rules |
| `.venv` | Virtual environment |
| `binary_files` | PyInstaller outputs |
| `cache` | Runtime temp data |
| `config` | Static config files |
| `core` | Global reusable library (C00–C20) |
| `credentials` | Secrets storage |
| `data` | Project datasets |
| `gui` | Project UI layer (G00–G04, Gx0a/Gx0b) |
| `implementation` | Operational project logic |
| `logs` | Runtime log files |
| `main` | Entry-point orchestration |
| `outputs` | Final artefacts |
| `scratchpad` | Prototype sandbox |
| `sql` | SQL assets |
| `tech_docs` | Internal engineering docs |
| `templates` | Script templates |
| `tests` | Automated testing |
| `user_guides` | Stakeholder documentation |