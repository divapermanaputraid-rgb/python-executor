# Python Execution Flow Tutor — Execution Engine Specification

## 1. Purpose

Execution Engine bertanggung jawab menjalankan Python code secara terkontrol dan menghasilkan representasi terstruktur mengenai apa yang terjadi selama program berjalan.

Tujuan utama bukan hanya mengetahui:

> "Baris mana yang sedang berjalan?"

tetapi:

> "Apa yang terjadi pada program ketika baris tersebut dijalankan?"

Execution Engine menjadi **source of truth** untuk runtime.

---

# 2. Core Responsibilities

Execution Engine harus mampu:

- menjalankan Python code;
- menghentikan execution pada execution point tertentu;
- melanjutkan execution;
- melakukan single-step execution;
- menangkap input;
- menangkap output;
- menangkap variable state;
- menangkap data type;
- menangkap function call;
- menangkap function return;
- menangkap exception;
- menangkap call stack;
- menghasilkan execution events;
- menghasilkan execution history;
- menghentikan execution ketika program selesai;
- menghentikan execution ketika timeout/security violation terjadi.

---

# 3. Non-Responsibilities

Execution Engine tidak bertanggung jawab untuk:

- menjelaskan kode kepada user;
- menghasilkan AI response;
- menentukan pedagogical strategy;
- menentukan pertanyaan;
- menentukan difficulty;
- menentukan materi belajar;
- melakukan UI rendering.

Boundary:

```text
Execution Engine
        ↓
"What happened?"
```

AI Tutor:

```text
"Why did it happen?"
"Can the learner predict what happens next?"
```

---

# 4. Execution Lifecycle

Setiap execution session memiliki lifecycle:

```text
CREATED
   ↓
STARTING
   ↓
RUNNING
   ↓
WAITING_FOR_INPUT
   ↓
PAUSED
   ↓
RUNNING
   ↓
COMPLETED
```

Jika terjadi error:

```text
RUNNING
   ↓
ERROR
```

Jika timeout:

```text
RUNNING
   ↓
TIMEOUT
```

Jika security violation:

```text
RUNNING
   ↓
SECURITY_VIOLATION
```

---

# 5. Execution Session

Setiap program execution memiliki session ID.

Contoh:

```json
{
  "session_id": "exec_01",
  "status": "running",
  "language": "python",
  "python_version": "3.x"
}
```

Session digunakan untuk:

- tracking execution;
- pause/resume;
- input;
- history;
- debugging;
- AI context.

---

# 6. Two-Layer Event Architecture

Execution Engine menggunakan dua jenis event.

## Layer 1 — Raw Runtime Events

Event yang berasal langsung dari mekanisme tracing/runtime.

Contoh:

```text
call
line
return
exception
```

Raw events berguna untuk debugging internal.

---

## Layer 2 — Normalized Execution Events

Raw events diterjemahkan menjadi event yang bermakna untuk user dan AI.

Contoh:

```text
program_start
line
variable_created
variable_updated
input_requested
input_received
output
function_call
function_return
exception
program_end
```

Architecture:

```text
Python Runtime
      ↓
Raw Trace
      ↓
Normalizer
      ↓
Normalized Event
      ↓
State Manager
      ↓
Frontend / AI
```

---

# 7. Why Normalization Exists

Jangan langsung expose raw Python tracing events ke frontend.

Contoh raw event:

```text
line
```

belum tentu cukup untuk menjelaskan:

```text
x = 10
```

kepada learner.

Normalized event dapat menjadi:

```json
{
  "type": "variable_created",
  "line": 1,
  "variable": "x",
  "value": 10,
  "data_type": "int"
}
```

Dengan demikian frontend dan AI tidak perlu memahami detail internal tracing Python.

---

# 8. Event Types

Minimal event types:

```text
program_start
line
variable_created
variable_updated
input_requested
input_received
output
function_call
function_return
exception
program_end
timeout
security_violation
```

---

# 9. Program Start

Ketika execution dimulai:

```json
{
  "type": "program_start",
  "session_id": "exec_01"
}
```

State awal:

```text
status = RUNNING
variables = {}
call_stack = []
stdout = ""
```

---

# 10. Line Event

Ketika execution mencapai line tertentu:

```json
{
  "type": "line",
  "line": 4,
  "frame_id": "frame_01"
}
```

Line event digunakan untuk:

- current-line arrow;
- code highlighting;
- stepping;
- execution timeline.

Line event tidak otomatis berarti variable berubah.

---

# 11. Variable Created

Ketika variable pertama kali dibuat:

```python
x = 10
```

Event:

```json
{
  "type": "variable_created",
  "line": 1,
  "variable": "x",
  "value": 10,
  "data_type": "int"
}
```

State:

```text
x
value = 10
type = int
```

---

# 12. Variable Updated

Jika:

```python
x = 10
x = 20
```

Event kedua:

```json
{
  "type": "variable_updated",
  "line": 2,
  "variable": "x",
  "previous_value": 10,
  "new_value": 20,
  "previous_type": "int",
  "new_type": "int"
}
```

Tujuan:

```text
10
 ↓
20
```

User dapat melihat state transition.

---

# 13. Input Requested

Ketika execution mencapai:

```python
name = input("Nama: ")
```

Engine menghasilkan:

```json
{
  "type": "input_requested",
  "line": 1,
  "prompt": "Nama: "
}
```

Execution state:

```text
WAITING_FOR_INPUT
```

Execution harus berhenti sampai input tersedia.

---

# 14. Input Received

User memasukkan:

```text
Diva
```

Engine menghasilkan:

```json
{
  "type": "input_received",
  "line": 1,
  "value": "Diva"
}
```

Kemudian execution dilanjutkan.

---

# 15. Output Event

Untuk:

```python
print("Hello")
```

Engine menghasilkan:

```json
{
  "type": "output",
  "line": 1,
  "value": "Hello",
  "stream": "stdout"
}
```

Output harus tetap dipisahkan dari internal execution state.

---

# 16. Function Call

Untuk:

```python
def add(a, b):
    return a + b

x = add(10, 20)
```

Ketika function dipanggil:

```json
{
  "type": "function_call",
  "line": 4,
  "function": "add",
  "arguments": {
    "a": 10,
    "b": 20
  },
  "frame_id": "frame_02"
}
```

Call stack:

```text
add()
global
```

---

# 17. Function Return

Ketika:

```python
return a + b
```

engine menghasilkan:

```json
{
  "type": "function_return",
  "line": 2,
  "function": "add",
  "return_value": 30,
  "return_type": "int"
}
```

Call stack kembali:

```text
global
```

Kemudian assignment:

```text
x = 30
```

dapat menghasilkan:

```json
{
  "type": "variable_created",
  "line": 4,
  "variable": "x",
  "value": 30,
  "data_type": "int"
}
```

---

# 18. Exception Event

Jika:

```python
x = 10
y = "5"

print(x + y)
```

engine menghasilkan:

```json
{
  "type": "exception",
  "line": 4,
  "exception_type": "TypeError",
  "message": "unsupported operand type(s)..."
}
```

Execution state:

```text
ERROR
```

Exception harus mempertahankan:

- exception type;
- message;
- line;
- frame;
- relevant variables;
- call stack.

---

# 19. Program End

Jika execution selesai normal:

```json
{
  "type": "program_end",
  "status": "completed"
}
```

Final state:

```text
status = COMPLETED
```

---

# 20. Execution State

Event history bukan satu-satunya data.

Engine juga mempertahankan current state.

Contoh:

```json
{
  "status": "PAUSED",
  "current_line": 5,
  "variables": {
    "x": {
      "value": 20,
      "type": "int"
    },
    "name": {
      "value": "Diva",
      "type": "str"
    }
  },
  "call_stack": [
    {
      "function": "<module>",
      "line": 5
    }
  ],
  "stdout": "",
  "exception": null
}
```

Current state adalah snapshot kondisi program saat ini.

---

# 21. Execution History

History menyimpan event yang telah terjadi.

Contoh:

```json
[
  {
    "type": "program_start"
  },
  {
    "type": "input_requested",
    "line": 1
  },
  {
    "type": "input_received",
    "line": 1,
    "value": "20"
  },
  {
    "type": "variable_created",
    "line": 1,
    "variable": "x",
    "value": 20,
    "data_type": "int"
  },
  {
    "type": "line",
    "line": 2
  }
]
```

History digunakan oleh:

- frontend timeline;
- AI context;
- debugging;
- learning analytics.

---

# 22. Step Execution

Ketika user menekan:

```text
STEP
```

Engine harus:

1. resume execution;
2. menjalankan execution sampai execution point berikutnya;
3. pause;
4. menghasilkan current state;
5. mengirim event/state ke backend.

Contoh:

```text
STEP
 ↓
line 1
 ↓
PAUSED
```

Tekan Step lagi:

```text
STEP
 ↓
line 2
 ↓
PAUSED
```

---

# 23. Continue Execution

`Continue` menjalankan program sampai:

- input diperlukan;
- breakpoint/execution point;
- exception;
- program selesai;
- timeout;
- security violation.

---

# 24. Breakpoint

MVP dapat menyediakan automatic execution points tanpa custom breakpoint.

Future version dapat mendukung:

```text
User clicks line 7
        ↓
Breakpoint created
        ↓
Continue
        ↓
Execution pauses at line 7
```

Custom breakpoint bukan requirement MVP.

---

# 25. State Snapshot

Setiap meaningful execution event dapat menghasilkan snapshot.

Contoh:

```text
EVENT
↓
State Snapshot
↓
Event History
```

Snapshot minimal berisi:

```text
current line
variables
types
call stack
stdout
exception
status
```

---

# 26. Value Representation

Tidak semua Python object dapat langsung diserialisasi sebagai JSON.

Karena itu engine tidak boleh mengirim arbitrary object secara mentah.

Gunakan safe representation:

```json
{
  "type": "int",
  "repr": "20"
}
```

Untuk string:

```json
{
  "type": "str",
  "repr": "'Diva'"
}
```

Untuk list:

```json
{
  "type": "list",
  "repr": "[1, 2, 3]",
  "length": 3
}
```

Untuk object kompleks:

```json
{
  "type": "MyClass",
  "repr": "<MyClass object>",
  "inspectable": true
}
```

Value inspection harus dibatasi untuk mencegah side effects dan security problems.

---

# 27. Variable Scope

Variable harus dikaitkan dengan frame.

Contoh:

```text
global
  x = 10

add()
  a = 20
  b = 30
```

Representation:

```json
{
  "frames": [
    {
      "id": "frame_global",
      "scope": "global",
      "variables": {}
    },
    {
      "id": "frame_add",
      "scope": "local",
      "function": "add",
      "variables": {
        "a": 20,
        "b": 30
      }
    }
  ]
}
```

Ini penting untuk menjelaskan scope.

---

# 28. Loop Execution

Untuk:

```python
for i in range(3):
    print(i)
```

Engine tidak perlu membuat event internal untuk setiap mekanisme interpreter.

Yang penting bagi learner:

```text
iteration 1
i = 0

iteration 2
i = 1

iteration 3
i = 2
```

Normalized events dapat menyediakan metadata:

```json
{
  "type": "line",
  "line": 2,
  "loop": {
    "iteration": 2
  }
}
```

Detail loop harus ditambahkan hanya jika dapat diperoleh secara reliable.

Engine tidak boleh mengarang iteration metadata.

---

# 29. Conditional Execution

Untuk:

```python
if x > 10:
    print("Large")
else:
    print("Small")
```

Engine harus menghasilkan execution history yang menunjukkan branch yang benar-benar dijalankan.

Contoh:

```text
line 1
condition evaluated
line 2
```

Jika branch metadata tersedia:

```json
{
  "type": "branch",
  "line": 1,
  "condition": "x > 10",
  "result": true,
  "branch": "if"
}
```

Branch event hanya boleh digunakan jika nilai condition dapat ditentukan secara reliable.

---

# 30. Execution Invariants

Engine harus mempertahankan aturan berikut.

### Invariant 1

Current line harus berasal dari execution trace.

### Invariant 2

Variable state harus berasal dari runtime.

### Invariant 3

Exception harus berasal dari runtime.

### Invariant 4

Engine tidak boleh memprediksi execution.

### Invariant 5

AI tidak boleh mengubah execution state.

### Invariant 6

Frontend tidak boleh menjadi source of truth.

---

# 31. Determinism

Untuk educational execution, engine harus sebisa mungkin menghasilkan execution yang reproducible.

Environment sebaiknya dikontrol:

```text
Python version
Environment variables
Working directory
Installed packages
Timezone
Randomness
Network
Filesystem
```

Program yang bergantung pada random/time/network harus mendapat perlakuan khusus.

---

# 32. Timeout

Program yang tidak berhenti:

```python
while True:
    pass
```

harus dihentikan.

Contoh:

```text
Execution timeout
       ↓
Terminate sandbox
       ↓
Emit timeout event
       ↓
Show error state
```

AI kemudian dapat menjelaskan berdasarkan event:

```text
type = timeout
```

bukan mengarang bahwa program "mungkin infinite loop".

---

# 33. Security Violation

Jika user mencoba akses yang dilarang:

```python
import subprocess
subprocess.run(...)
```

sandbox menghentikan execution.

Event:

```json
{
  "type": "security_violation",
  "reason": "process_creation_not_allowed"
}
```

Security event memiliki prioritas lebih tinggi daripada AI explanation.

---

# 34. Engine API Concept

Interface konseptual:

```text
create_session(code)
start(session_id)
step(session_id)
continue(session_id)
provide_input(session_id, input)
pause(session_id)
reset(session_id)
get_state(session_id)
get_history(session_id)
terminate(session_id)
```

Implementasi API final ditentukan kemudian.

---

# 35. Engine Output Contract

Execution Engine harus menghasilkan dua output utama:

```text
Execution Event
+
Current Execution State
```

Contoh:

```json
{
  "event": {
    "type": "variable_created",
    "line": 1,
    "variable": "x"
  },
  "state": {
    "status": "PAUSED",
    "current_line": 1,
    "variables": {
      "x": {
        "type": "int",
        "repr": "10"
      }
    }
  }
}
```

---

# 36. AI Boundary

AI menerima:

```text
source code
+
current state
+
relevant execution history
+
relevant Python knowledge
```

AI tidak menerima akses langsung untuk:

```text
execute code
modify variables
resume execution
terminate sandbox
```

AI hanya memberikan pedagogical response.

---

# 37. Testing Requirements

Execution Engine harus memiliki test cases untuk:

### Basic

```text
assignment
print
input
arithmetic
```

### Control Flow

```text
if
else
for
while
```

### Functions

```text
function call
parameters
return
nested calls
```

### State

```text
variable creation
variable update
scope
type changes
```

### Errors

```text
SyntaxError
NameError
TypeError
ValueError
ZeroDivisionError
```

### Runtime

```text
timeout
input waiting
program completion
```

### Security

```text
filesystem
network
subprocess
resource exhaustion
```

---

# 38. Definition of Done

Execution Engine MVP dianggap selesai apabila program berikut dapat dieksekusi secara reliable:

```python
name = input("Name: ")
age = int(input("Age: "))

if age >= 18:
    status = "adult"
else:
    status = "minor"

print(name, status)
```

Engine harus mampu:

- start execution;
- pause pada input;
- menerima input;
- menghasilkan variable state;
- mengetahui type;
- menunjukkan current line;
- menunjukkan branch yang dijalankan;
- menghasilkan output;
- menghasilkan execution history;
- menghasilkan final state;
- menangani basic exception.

---

# 39. Final Execution Architecture

```text
                 USER CODE
                     │
                     ▼
              ┌─────────────┐
              │   SANDBOX   │
              └──────┬──────┘
                     │
                     ▼
             Python Runtime
                     │
                     ▼
              Raw Trace Events
                     │
                     ▼
            ┌─────────────────┐
            │ Event Normalizer│
            └────────┬────────┘
                     │
             ┌───────┴────────┐
             ▼                ▼
       Current State      Event History
             │                │
             └───────┬────────┘
                     ▼
                 Backend
                     │
           ┌─────────┴─────────┐
           ▼                   ▼
       Frontend            AI Context
                               │
                               ▼
                           AI Tutor
```

**Core rule:**

> The execution engine observes and records reality. It does not interpret reality pedagogically.

Interpretation belongs to the AI Tutor.
