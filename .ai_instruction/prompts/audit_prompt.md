  ---
  ## FULL A03/A04 COMPLIANCE AUDIT

  Audit the file: [FILE_PATH]

  **MANDATORY PROCESS — Do not skip any step.**

  ---

  ### STEP 1: Read Reference Documents
  Read these files IN FULL before proceeding:
  - `.ai_instruction/A03_audit.md`
  - `.ai_instruction/A04_anti_patterns.md`

  ---

  ### STEP 2: Read Target File
  Read the complete file to be audited.

  ---

  ### STEP 3: Determine File Depth
  - Count folders from project root to file
  - If in `implementation/subfolder/` → nested (3 parent) → requires `# Note:` comment
  - If in `implementation/` or `core/` → standard (2 parent)

  ---

  ### STEP 4: Execute Pass 1 — Mechanical Checks
  Using the tables in A03 "Section 1 Required Lines", "Section 2 Required Lines", and "Section 98/99 Required Patterns":

  - Grep for EVERY required pattern
  - Report count found for each
  - Missing ANY required pattern = CRITICAL

  Then check "Immediate Fail Conditions" table:
  - Grep for EVERY fail pattern
  - Any found = CRITICAL

  **Output as a table showing pattern → expected → found.**

  ---

  ### STEP 5: Execute Pass 2 — Anti-Pattern Scan
  Using A04_anti_patterns.md:

  - Grep for EVERY anti-pattern listed (all modules C00-C20)
  - For each pattern found, note line number and required replacement
  - Any found = MAJOR (unless A04 specifies otherwise)

  **Output as a table showing pattern → lines found → replacement.**

  ---

  ### STEP 6: Check Docstrings & Type Hints
  - List all functions in `__all__`
  - Verify each has a docstring with Description section
  - Check type hints on parameters and return values
  - Missing docstring on public function = MAJOR
  - Missing type hints = MINOR

  ---

  ### STEP 7: Generate Audit Report

  ════════════════════════════════════════════════════════════════
  AUDIT REPORT: [FILENAME]
  ════════════════════════════════════════════════════════════════

  FILE DEPTH: [standard/nested] → [2/3] parent levels
  NOTE COMMENT: [present/missing/not-required]

  ────────────────────────────────────────────────────────────────
  PASS 1: MECHANICAL CHECKS
  ────────────────────────────────────────────────────────────────
  Section 1 Required Lines: [X/11] or [X/12 if nested]
  Section 2 Required Lines: [X/8]
  Section 98/99 Required:   [X/5]
  Immediate Fail Patterns:  [X found]

  Violations:
  • [Line X: description] — CRITICAL/MAJOR/MINOR
  • ...or "None"

  ────────────────────────────────────────────────────────────────
  PASS 2: SEMANTIC CHECKS
  ────────────────────────────────────────────────────────────────
  A04 Anti-patterns Found: [X]
  Docstrings Missing:      [X]
  Type Hints Missing:      [X]

  Violations:
  • [Line X: pattern found → use replacement instead] — MAJOR
  • ...or "None"

  ────────────────────────────────────────────────────────────────
  SUMMARY
  ────────────────────────────────────────────────────────────────
  CRITICAL: [count]
  MAJOR:    [count]
  MINOR:    [count]

  VERDICT: [PASS / FAIL]
  ════════════════════════════════════════════════════════════════

  ---

  ### STEP 8: If FAIL
  - Fix all CRITICAL and MAJOR violations
  - After fixes, re-run Steps 4-7 to confirm PASS
  - Only deliver when VERDICT = PASS

  ---

  **DO NOT SKIP ANY STEP. DO NOT SUMMARISE A04 — CHECK EVERY PATTERN.**