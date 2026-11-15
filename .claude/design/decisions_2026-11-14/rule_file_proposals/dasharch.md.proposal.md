# Proposal: `.claude/rules/dasharch.md`

Status: PROPOSAL for Eve's double confirmation. No rule file was edited. Checked: paths and file names named in the file against the tree.

## 1. Line 19, `integrity_report.txt` (FACT; CHANGES A RULE if replaced)
Today: `4. **Integrity Guardian:** Enforce Test CLI Standards & Naming Laws. Always check \`integrity_report.txt\` generation before writing new code to prevent regressions.`
Evidence: no tracked file is named `integrity_report.txt` (`git ls-files | grep -c integrity_report` gives 0) and no Python file writes it (`grep -rn integrity_report --include=*.py` finds only the three `*_integrity_suite.py` file names, which match on their own name).
Proposed: `4. **Integrity Guardian:** Enforce Test CLI Standards & Naming Laws (\`rules_verification_testing.md\`). Run the tests of the library you change before writing new code, and again after, to prevent regressions.`
CHANGES A RULE (the check named is replaced by the real gate: pytest). Alternative: delete the sentence; Eve decides.

## 2. Line 41, verification protocol path (FACT)
Today: `Strictly adhere to ./agents/workflows/verification_protocol.md for all code implementations.`
Proposed: `... to .claude/workflows/verification_protocol.md ...`
Why: `.claude/workflows/verification_protocol.md` exists; `agents/` does not appear in the tree (`ls agents` not run; the file at the old path is not tracked: the new path was found by `ls`).

## 3. Line 22, Data Contract Specialist (no change)
Not checked beyond: `MLST`, AMR genes are metadata examples only.

## Not settled
None.
