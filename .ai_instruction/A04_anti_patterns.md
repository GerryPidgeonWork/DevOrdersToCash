# A04 — Anti-Patterns

> **Diagnostic indicators of architectural drift and governance erosion.**
> Anti-patterns are not hard failures by default; they signal increased risk and require conscious response.

---

## Scope and Intent

This document:

* Describes **patterns that indicate drift** from intended architecture or governance
* Complements, but does not replace, **rules (A01)** or **audit checks (A03)**
* Is intended for use during **A02 Step 5 — Pre-Delivery Verification**

This document does **not**:

* Define new prohibitions
* Override A01 rules
* Duplicate A03 mechanical checks

> **If an item here conflicts with A01 or A03, A01/A03 take precedence.**

---

## How to Use This Document

When an anti-pattern is detected:

1. **Pause** — do not ignore it
2. **Identify cause** — why did this pattern appear?
3. **Choose a response**, based on guidance below:

   * Refactor immediately
   * Escalate to the user for approval
   * Proceed with explicit justification

Anti-patterns are grouped by **risk domain**, not by file or module.

---

## Architectural Drift

### AP-01: Direct Imports Bypassing Hubs or Facades

**Pattern:**

* Direct import of external or standard-library packages
* Direct `tkinter` imports outside permitted layers

**Why it matters:**

* Bypasses central dependency control
* Breaks replaceability and audit assumptions

**Recommended response:**

* Refactor to use the appropriate hub or facade
* If refactoring is not possible, escalate to the user

---

### AP-02: Logic Executing at Import Time

**Pattern:**

* Function calls or object instantiation at module scope
* Side-effects triggered on import

**Why it matters:**

* Breaks determinism
* Causes unpredictable runtime behaviour

**Recommended response:**

* Move logic into `main()` or a callable function
* Re-run pre-delivery verification

---

### AP-03: Layer Boundary Leakage

**Pattern:**

* Lower layers importing from higher layers
* Pages importing directly from G00/G01 instead of G02a

**Why it matters:**

* Creates hidden coupling
* Prevents safe refactoring

**Recommended response:**

* Reroute imports through the correct facade
* Escalate if no facade exists

---

## Process Smells

### AP-04: Template Drift

**Pattern:**

* Section numbers modified
* Instruction blocks partially retained
* Protected regions edited

**Why it matters:**

* Breaks audit assumptions
* Introduces inconsistency

**Recommended response:**

* Recreate the file from the correct template
* Reapply logic cleanly

---

### AP-05: Silent Assumptions

**Pattern:**

* Behaviour depends on assumptions not stated explicitly
* Implicit decisions about structure, imports, or placement

**Why it matters:**

* Violates transparency
* Makes maintenance fragile

**Recommended response:**

* State assumptions explicitly
* If architectural, escalate to the user

---

## Maintainability Risks

### AP-06: Shadowing Core or GUI Functionality

**Pattern:**

* Local helper functions duplicating Core/GUI behaviour
* Wrapper functions with identical signatures

**Why it matters:**

* Splits authority
* Encourages divergence

**Recommended response:**

* Remove duplicate logic
* Use the existing Core/GUI function directly

---

### AP-07: Over-Generalisation

**Pattern:**

* Abstract helper created "for future use" without a concrete need
* Framework-like code in implementation layer

**Why it matters:**

* Adds unnecessary complexity
* Encourages premature architecture

**Recommended response:**

* Inline logic where used
* Defer abstraction until justified

---

## Governance Signals

### AP-08: Repeated Minor Violations

**Pattern:**

* Same minor issues appearing across multiple files
* Frequent justifications for exceptions

**Why it matters:**

* Indicates systemic drift
* Often precedes major violations

**Recommended response:**

* Pause and reassess approach
* Escalate to the user with summary of findings

---

## Severity Guidance

Anti-patterns fall into three practical response categories:

* **Refactor Immediately** — correct before delivery
* **Escalate** — requires user awareness or approval
* **Proceed with Justification** — acceptable with explicit explanation

Severity is contextual; use judgement aligned with A00–A03.

---

## Notes on Longevity

This list is intentionally:

* **Additive** — new anti-patterns may be appended
* **Stable** — existing items should not be weakened
* **Descriptive** — focused on signals, not enforcement

Avoid converting anti-patterns into hard rules unless they are promoted formally to A01 or A03.
