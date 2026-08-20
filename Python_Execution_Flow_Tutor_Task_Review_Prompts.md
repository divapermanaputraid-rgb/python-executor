# Python Execution Flow Tutor — Task Review Prompts

## Purpose

This file contains review prompts for TASK 01–30 of the Python Execution Flow Tutor project.

Each completed task must be reviewed before moving to the next task.

The review process uses three review perspectives:

1. `/code-review` — correctness, maintainability, architecture, regressions
2. `/security-review` — sandbox, isolation, resource abuse, secrets, trust boundaries
3. `/feature-dev` — feature completeness, integration, behavior against the specification

## Global Review Rules

- Review the actual repository, not an imagined implementation.
- Read the relevant project documentation before reviewing.
- Inspect the diff and existing code.
- Do not rewrite the implementation during review.
- Do not silently fix findings.
- Do not assume a feature works because code exists.
- Run appropriate tests/checks when possible.
- If a required fact cannot be verified, mark it `UNKNOWN`.
- Never invent test results.
- Distinguish:
  - BUG
  - SECURITY ISSUE
  - ARCHITECTURAL ISSUE
  - MISSING REQUIREMENT
  - TEST GAP
  - STYLE / MAINTAINABILITY
  - ACCEPTABLE TRADE-OFF
- Review only the scope of the active task, but identify critical regressions outside the scope.
- Do not approve a task merely because the code compiles.
- A task is PASS only when its Definition of Done is actually demonstrated.

## Required Review Output

Every review must use:

```text
# TASK XX REVIEW

## Scope
What this task was supposed to implement.

## Files Reviewed
List files actually inspected.

## Documentation Reviewed
List relevant documents.

## /code-review
Findings:
- [CRITICAL]
- [HIGH]
- [MEDIUM]
- [LOW]

## /security-review
Findings:
- [CRITICAL]
- [HIGH]
- [MEDIUM]
- [LOW]

## /feature-dev
Findings:
- [MISSING]
- [INCORRECT]
- [INCOMPLETE]
- [PASS]

## Tests Executed
List exact commands/checks.

## Evidence
Explain what proves the implementation works.

## Regression Check
Mention whether existing behavior appears affected.

## Verdict
PASS / PASS WITH WARNINGS / FAIL / BLOCKED

## Required Fixes
Only concrete fixes required before approval.

## Optional Improvements
Non-blocking improvements.

## Next Task
State the next task number, but DO NOT implement it.
```

---

# TASK 01 — Repository Audit

Review goal:
Verify that the repository audit correctly describes the actual repository.

Check:
- architecture findings are evidence-based;
- technology stack is accurate;
- missing components are correctly identified;
- no implementation was accidentally added;
- documentation status is accurate.

Expected:
Audit only. No feature implementation.

Verdict requirement:
PASS only if the audit is factual and complete enough to safely begin implementation.

---

# TASK 02 — Project Skeleton

Review with:

`/code-review`
- directory boundaries;
- configuration quality;
- unnecessary files;
- separation of frontend/backend/execution concerns.

`/security-review`
- no accidental exposure of secrets;
- no unsafe default execution mechanism;
- no user code execution path yet.

`/feature-dev`
- required project structure exists;
- application starts;
- no premature feature implementation.

Definition of Done:
Project structure exists and application starts.

---

# TASK 03 — Domain Types

Review:
- ExecutionSession;
- ExecutionStatus;
- ExecutionEvent;
- ExecutionState;
- ValueRepresentation.

`/code-review`
Check type consistency and responsibility boundaries.

`/security-review`
Check whether types accidentally expose sensitive runtime information.

`/feature-dev`
Compare types against EVENT_SCHEMA.md.

Definition of Done:
Types compile successfully.

---

# TASK 04 — Event Schema Implementation

Review:
- event base structure;
- event type validation;
- schema version;
- required fields;
- invalid event handling.

`/code-review`
Check whether validation is centralized and maintainable.

`/security-review`
Check malformed input handling and unsafe data propagation.

`/feature-dev`
Verify schema matches EVENT_SCHEMA.md.

Definition of Done:
Valid events pass; invalid events fail.

---

# TASK 05 — Python Execution Prototype

Review:
- Python execution mechanism;
- process boundary;
- stdout return;
- lifecycle handling.

`/code-review`
Check separation between backend and execution process.

`/security-review`
CRITICAL FOCUS:
- Is user code executed inside the backend process?
- Can user code access host resources?
- Is the execution boundary real or simulated?

`/feature-dev`
Verify:

print("hello")

actually executes and returns output.

Definition of Done:
Python executes outside the main backend process.

---

# TASK 06 — Execution Session

Review:
- session ID;
- lifecycle;
- status;
- cleanup.

`/code-review`
Check state ownership and lifecycle design.

`/security-review`
Check session isolation and cleanup on failure.

`/feature-dev`
Verify create → execute → complete → cleanup.

Definition of Done:
Session lifecycle works.

---

# TASK 07 — Runtime Line Tracing

Review:
- actual Python tracing mechanism;
- line events;
- event ordering.

`/code-review`
Check tracing implementation and coupling.

`/security-review`
Check tracing cannot bypass execution isolation.

`/feature-dev`
Verify actual execution:

x = 10
y = x + 5
print(y)

Expected lines:
1, 2, 3.

Reject simulated line movement.

Definition of Done:
Actual runtime lines are captured.

---

# TASK 08 — Program Lifecycle Events

Review:
- program_start;
- program_end;
- exception;
- ordering;
- abnormal termination.

`/code-review`
Check lifecycle ownership.

`/security-review`
Check exceptions do not leak host internals.

`/feature-dev`
Compare behavior against EVENT_SCHEMA.md.

Definition of Done:
Normal and failed programs produce correct lifecycle events.

---

# TASK 09 — Variable State Tracking

Review:
- variable creation;
- variable update;
- value representation;
- scope handling.

`/code-review`
Check whether variable tracking is isolated from tracing logic.

`/security-review`
Check safe representation:
- no arbitrary object execution;
- no dangerous introspection;
- bounded output.

`/feature-dev`
Test:

x = 10
x = 20

Expected:
created x=10
updated x=20

Definition of Done:
Actual variable transitions are observable.

---

# TASK 10 — Input Handling

Review:
- input_requested;
- WAITING_FOR_INPUT;
- input_received;
- resume behavior.

`/code-review`
Check concurrency/state handling.

`/security-review`
Check input size limits and session isolation.

`/feature-dev`
Test:

name = input("Name: ")
print(name)

Definition of Done:
Execution pauses and resumes correctly.

---

# TASK 11 — Output Capture

Review:
- stdout;
- stderr;
- output events;
- output ordering.

`/code-review`
Check stream handling and cleanup.

`/security-review`
Check output limits and log leakage.

`/feature-dev`
Test normal output and error output.

Definition of Done:
Output is captured without corrupting execution state.

---

# TASK 12 — Function Call Tracking

Review:
- function_call;
- function_return;
- arguments;
- return values.

`/code-review`
Check frame ownership and event consistency.

`/security-review`
Check safe value representation of arguments/returns.

`/feature-dev`
Test:

def add(a, b):
    return a + b

result = add(2, 3)

Definition of Done:
Calls and returns are accurate.

---

# TASK 13 — Call Stack State

Review:
- frame IDs;
- function names;
- current line;
- scope;
- variables;
- stack ordering.

`/code-review`
Check whether stack state is derived from runtime facts.

`/security-review`
Check sensitive locals are not leaked unnecessarily.

`/feature-dev`
Verify stack reconstruction.

Definition of Done:
Current call stack is accurate.

---

# TASK 14 — Exception State

Review:
- exception type;
- message;
- line;
- frame;
- traceback.

`/code-review`
Check error model consistency.

`/security-review`
CRITICAL:
Ensure internal paths, environment variables, secrets, and infrastructure details are not exposed.

`/feature-dev`
Verify exact error location and type.

Definition of Done:
Frontend/AI can identify why execution failed.

---

# TASK 15 — Resource Limits

Review:
- timeout;
- output limit;
- source size limit;
- input size limit;
- memory/resource policy.

`/code-review`
Check resource limits are enforced at the correct layer.

`/security-review`
CRITICAL FOCUS:
Test infinite loops and resource exhaustion.

Test:

while True:
    pass

Also inspect whether limits can be bypassed.

`/feature-dev`
Verify timeout event and safe termination.

Definition of Done:
Abusive execution is terminated safely.

---

# TASK 16 — Filesystem Isolation

Review:
- working directory;
- path restrictions;
- cleanup;
- host filesystem boundary.

`/code-review`
Check filesystem handling.

`/security-review`
CRITICAL FOCUS:
Attempt access to host paths.

Test:
open("/etc/passwd")

Also test:
- path traversal;
- symlinks where relevant;
- parent directory access.

`/feature-dev`
Verify safe temporary file operations work.

Definition of Done:
User code cannot escape its filesystem boundary.

---

# TASK 17 — Environment Isolation

Review:
- environment passed to Python;
- secret handling;
- inherited environment.

`/code-review`
Check explicit environment construction.

`/security-review`
CRITICAL FOCUS:
Run:

import os
print(os.environ)

Verify application secrets are unavailable.

`/feature-dev`
Verify normal Python environment behavior remains usable.

Definition of Done:
Secrets are not exposed.

---

# TASK 18 — Network / Process Restrictions

Review:
- network policy;
- subprocess policy;
- process spawning;
- OS command execution.

`/code-review`
Check restrictions are implemented at the correct architectural boundary.

`/security-review`
CRITICAL FOCUS:
Test:
- socket;
- subprocess;
- os.system;
- child process creation;
- network access.

Do not accept an import blacklist as the sole security boundary.

`/feature-dev`
Verify legitimate educational Python still works.

Definition of Done:
Arbitrary network/process access is prevented.

---

# TASK 19 — Execution Service API

Review:
- create execution;
- submit input;
- stop execution;
- retrieve state/events.

`/code-review`
Check endpoint/service separation and validation.

`/security-review`
Check:
- input validation;
- authorization boundary if applicable;
- session ownership;
- abuse limits.

`/feature-dev`
Verify API operations work end-to-end.

Definition of Done:
Execution is controllable through the service layer.

---

# TASK 20 — Event Stream

Review:
- incremental events;
- ordering;
- reconnect behavior if implemented;
- completion;
- disconnect handling.

`/code-review`
Check event transport abstraction.

`/security-review`
Check cross-session event leakage.

`/feature-dev`
Verify frontend can receive events before execution completes.

Definition of Done:
Events are available incrementally.

---

# TASK 21 — Minimal Frontend Shell

Review:
- four required sections;
- component boundaries;
- no unnecessary feature work.

`/code-review`
Check UI architecture.

`/security-review`
Check frontend does not execute arbitrary Python locally unless explicitly designed and isolated.

`/feature-dev`
Required sections:
1. Code
2. Execution
3. State/Result
4. AI Tutor

Definition of Done:
Four-section interface renders.

---

# TASK 22 — Code Editor

Review:
- Python editing;
- line numbers;
- syntax highlighting;
- run control;
- code submission.

`/code-review`
Check editor component isolation.

`/security-review`
Check code submission is treated as untrusted input.

`/feature-dev`
Verify user can write and submit Python.

Definition of Done:
Code editing and submission work.

---

# TASK 23 — Execution Visualization

Review:
- current line;
- arrow;
- highlight;
- status.

`/code-review`
Check UI consumes runtime events/state rather than duplicating execution logic.

`/security-review`
Check untrusted runtime data is safely rendered.

`/feature-dev`
CRITICAL:
Arrow must follow actual runtime events.

Reject timer-based fake execution.

Definition of Done:
Arrow moves according to real execution.

---

# TASK 24 — State Visualization

Review:
- variables;
- types;
- values;
- call stack;
- stdout;
- stderr;
- errors.

`/code-review`
Check state rendering boundaries.

`/security-review`
Check dangerous values cannot cause client-side execution or injection.

`/feature-dev`
Verify state updates from runtime events.

Definition of Done:
Runtime state is visible and accurate.

---

# TASK 25 — Interactive Input UI

Review:
- input request handling;
- input field;
- submit;
- execution resume.

`/code-review`
Check UI/backend state synchronization.

`/security-review`
Check input limits and session isolation.

`/feature-dev`
Verify end-to-end input flow.

Definition of Done:
Interactive input works.

---

# TASK 26 — Execution Controls

Review:
- Run;
- Step;
- Continue;
- Stop;
- valid state transitions.

`/code-review`
Check controls are driven by execution state.

`/security-review`
Check Stop actually terminates the sandbox and cleans resources.

`/feature-dev`
Verify every control against its intended semantics.

Definition of Done:
Controls correctly affect execution.

---

# TASK 27 — AI Context Builder

Review:
- source;
- current line;
- event;
- state;
- history;
- error;
- prediction.

`/code-review`
Check deterministic context construction and separation from AI provider logic.

`/security-review`
CRITICAL:
- source code is untrusted;
- stdout is untrusted;
- no secrets enter AI context;
- prompt injection boundaries are preserved.

`/feature-dev`
Verify context contains actual runtime facts.

Definition of Done:
AI receives deterministic structured context.

---

# TASK 28 — AI Tutor

Review:
- question;
- hint;
- explanation;
- error explanation;
- summary.

`/code-review`
Check AI integration boundary and error handling.

`/security-review`
CRITICAL:
- prompt injection;
- secret leakage;
- malicious stdout;
- malicious source comments;
- provider key exposure.

`/feature-dev`
Test:

x = 10
y = "5"
print(x + y)

AI must explain the actual TypeError using runtime state.

Reject hallucinated values.

Definition of Done:
AI explains execution without inventing runtime facts.

---

# TASK 29 — Learning Flow

Review:

USER CODE
↓
PREDICTION
↓
EXECUTION
↓
OBSERVATION
↓
USER EXPLANATION
↓
AI FEEDBACK
↓
NEXT STEP

`/code-review`
Check orchestration boundaries.

`/security-review`
Check user-controlled prediction/source/output cannot override system instructions.

`/feature-dev`
Verify the complete educational interaction.

Do not approve if it is merely a chatbot attached to a code editor.

Definition of Done:
User can predict, execute, observe, and receive feedback.

---

# TASK 30 — Integration, Testing & Hardening

This is the final review.

Use all three:

`/code-review`
`/security-review`
`/feature-dev`

Test:

1. basic assignment
2. variable update
3. input
4. output
5. function call
6. function return
7. loop
8. exception
9. timeout
10. memory/resource abuse
11. filesystem access
12. environment access
13. subprocess access
14. network access
15. AI explanation
16. execution arrow
17. stop execution
18. cleanup

Then audit:

- architecture;
- security boundaries;
- event correctness;
- state correctness;
- frontend synchronization;
- AI hallucination risks;
- duplicated logic;
- dead code;
- unnecessary dependencies;
- debug logs;
- temporary hacks;
- error handling;
- test coverage.

Final review must explicitly answer:

1. Can user code escape the sandbox?
2. Can user code access secrets?
3. Can user code consume unbounded resources?
4. Is the execution arrow based on real runtime state?
5. Are events actual runtime facts?
6. Can execution work without AI?
7. Can AI explain runtime state without guessing?
8. Are frontend and execution responsibilities separated?
9. Can execution sessions interfere with each other?
10. Can the system recover from timeout/error/cancellation?

Final Verdict:

PASS
PASS WITH WARNINGS
FAIL
BLOCKED

A final PASS requires all critical security issues to be resolved.

---

# REVIEW COMMAND

When the user says:

REVIEW TASK XX

perform only that task's review.

When the user says:

REVIEW ALL

review TASK 01–30 sequentially, but do not modify code unless explicitly requested.

When the user says:

FIX REVIEW

only fix issues identified by the most recent review.
Do not introduce unrelated features.

When the user says:

SECURITY REVIEW TASK XX

focus primarily on `/security-review`.

When the user says:

CODE REVIEW TASK XX

focus primarily on `/code-review`.

When the user says:

FEATURE REVIEW TASK XX

focus primarily on `/feature-dev`.

---

# Final Principle

The review system must enforce:

    IMPLEMENT
        ↓
    TEST
        ↓
    REVIEW
        ↓
    FIX
        ↓
    REVIEW AGAIN
        ↓
    NEXT TASK

Never:

    IMPLEMENT EVERYTHING
        ↓
    HOPE IT WORKS
