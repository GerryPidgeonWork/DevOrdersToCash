# A02 — Process

> **Operational workflow for producing compliant work inside the governance system.**
> This document defines *how* work is performed, not *what* is permitted or *when* work may begin.

---

## Scope and Authority

This document:

* Defines the **operational workflow** for completing tasks
* Assumes all **authority, traversal, lifecycle, and failure-handling rules** defined in `A00_start_here.md`
* Assumes all **invariant rules and prohibitions** defined in `A01_rules.md`

This document does **not**:

* Grant permission to start work
* Override governance rules
* Define audit criteria

> **If there is any conflict between this document and A00, A00 takes precedence.**

---

## Process Overview

Every task follows the same structured flow:

### Execution Steps

1. Understand the request
2. Locate existing functionality
3. Plan before writing code
4. Implement in a compliant manner

### Decision Frameworks (Apply Throughout Execution)

* Ask vs Proceed
* Blocked or Partial Work

### Completion Steps

5. Pre-delivery verification
6. Delivery or halt

Each step or framework below maps to a **discrete, verifiable action**.

---

## Step 1 — Understand the Request

**Objective:** Ensure the task is fully understood before any design or implementation.

Actions:

* Identify the task goal in one sentence
* Identify the task type (new file, modification, audit, explanation)
* Identify affected layers (core, gui, implementation, documentation)

If any part of the request is unclear:

* Apply the **Ask vs Proceed** framework
* Do NOT guess or infer architectural intent

---

## Step 2 — Locate Existing Functionality

**Objective:** Prevent duplication and ensure reuse.

Actions (in order):

1. Search Core modules for existing functions
2. Search GUI framework modules if applicable
3. Search project implementation modules
4. Consult quick lookup documents *only after* reading full API docs

If a suitable function exists:

* Use it directly
* Do NOT wrap or reimplement it

If no suitable function exists:

* Proceed to planning

---

## Step 3 — Plan Before Writing Code

**Objective:** Make intent explicit before implementation.

Actions:

* Identify which files will be created or modified
* Identify which templates will be used
* Identify which Core / GUI functions will be called
* Identify any assumptions

A task is considered **non-trivial** if it:

* Modifies existing files, or
* Involves more than one file, or
* Introduces new behaviour

For non-trivial tasks, present a short plan (table or bullets) **before writing code**.

---

## Step 4 — Implement

**Objective:** Write compliant code following templates and rules.

Actions:

* Start from the correct template
* Preserve Section numbering exactly
* Implement logic only in Sections 3–97
* Declare public API in Section 98
* Place all executable logic inside `main()` in Section 99
* Ensure **no code executes at import time**

Do NOT:

* Introduce side-effects at import
* Bypass Core or GUI facades
* Change protected regions

---

## Decision Framework — Ask vs Proceed

This framework governs behaviour **throughout Steps 1–4**.

### You MUST ask before proceeding if:

* The task involves **architecture**, **structure**, or **layer placement**
* The task requires deviating from templates or rules
* The task conflicts with governance documents
* Required inputs or constraints are missing

### You MAY proceed without asking only if:

* The uncertainty is **non-architectural**
* The assumption is **reversible**
* The assumption will not affect imports, structure, or audit outcomes

If you proceed under an assumption:

* State the assumption **explicitly before presenting code**

> **If there is any conflict between this framework and A00 failure-handling rules, A00 takes precedence.**

---

## Decision Framework — Blocked or Partial Work

If you encounter a blocker at any point, follow the **Blocked or Partial Work** protocol defined in:

> `A00_start_here.md` — Section 9

This framework applies **at all times** and is not a sequential step.

---

## Step 5 — Pre-Delivery Verification

**Objective:** Perform a pre-audit self-check before delivery.

Actions:

* Manually verify compliance with A01 rules
* Check for known A04 anti-patterns
* Confirm that all executable code is confined to Section 99
* Confirm that imports conform to hub/facade rules

This step is a **pre-audit self-check**.

Formal audit criteria and enforcement are defined in `A03_audit.md`.

---

## Step 6 — Delivery or Halt

Before delivery, the work MUST be evaluated against the audit criteria defined in `A03_audit.md`.

If all checks pass:

* Deliver the work

If any CRITICAL or MAJOR issues remain:

* Do NOT deliver
* Explain the issue and required resolution

---

## Notes on Step Granularity

Each step or framework in this process corresponds to a **specific, confirmable action**.

If a step or framework cannot be truthfully confirmed as satisfied, you must not proceed.

This prevents drift, premature implementation, and audit failures.
