# Python Execution Flow Tutor — Event Schema

## 1. Purpose

`EVENT_SCHEMA.md` mendefinisikan format standar event yang dihasilkan oleh Python Execution Engine.

Event merupakan komunikasi terstruktur mengenai sesuatu yang terjadi selama program dieksekusi.

Prinsip utama:

> **Every runtime fact exposed to the application must be represented by structured data.**

Frontend dan AI tidak boleh menebak execution state dari source code jika fakta tersebut tersedia dari execution engine.

---

# 2. Event Architecture

```text
Python Runtime
      ↓
Raw Trace
      ↓
Event Normalizer
      ↓
Normalized Event
      ↓
State Manager
      ↓
┌──────────────┬──────────────┐
│              │              │
▼              ▼              ▼
Frontend       AI          History
```

---

# 3. Base Event Structure

Semua event memiliki struktur dasar:

```json
{
  "event_id": "evt_001",
  "session_id": "exec_001",
  "sequence": 1,
  "type": "line",
  "timestamp": 1750000000,
  "line": 1
}
```

### Fields

| Field        | Type         | Required | Description             |
| ------------ | ------------ | -------: | ----------------------- |
| `event_id`   | string       |      yes | Unique event identifier |
| `session_id` | string       |      yes | Execution session       |
| `sequence`   | integer      |      yes | Event ordering          |
| `type`       | string       |      yes | Event type              |
| `timestamp`  | number       |      yes | Event creation time     |
| `line`       | integer/null |       no | Related source line     |

---

# 4. Event Ordering

`sequence` merupakan sumber utama untuk menentukan urutan event.

Contoh:

```json
[
  {
    "sequence": 1,
    "type": "program_start"
  },
  {
    "sequence": 2,
    "type": "line",
    "line": 1
  },
  {
    "sequence": 3,
    "type": "variable_created",
    "line": 1
  },
  {
    "sequence": 4,
    "type": "line",
    "line": 2
  }
]
```

Consumer tidak boleh mengandalkan timestamp untuk menentukan execution order.

---

# 5. Event Types

MVP event types:

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

Future:

```text
branch
loop_iteration
break
continue
```

Event tambahan tidak boleh mengubah makna event existing.

---

# 6. `program_start`

Menandakan execution dimulai.

```json
{
  "type": "program_start",
  "session_id": "exec_001",
  "sequence": 1,
  "line": null
}
```

State:

```text
status = RUNNING
```

---

# 7. `line`

Menandakan Python mencapai source line tertentu.

```json
{
  "type": "line",
  "line": 4,
  "frame_id": "frame_001",
  "sequence": 5
}
```

Frontend menggunakan event ini untuk:

```text
→ current line
highlight
execution timeline
```

`line` harus berasal dari runtime trace.

---

# 8. `variable_created`

Menandakan variable tersedia untuk pertama kali dalam suatu scope.

```json
{
  "type": "variable_created",
  "line": 1,
  "frame_id": "frame_001",
  "variable": "x",
  "value": {
    "type": "int",
    "repr": "10"
  }
}
```

### Required

```text
variable
value.type
value.repr
frame_id
line
```

---

# 9. `variable_updated`

Menandakan nilai variable berubah.

```json
{
  "type": "variable_updated",
  "line": 2,
  "frame_id": "frame_001",
  "variable": "x",
  "previous_value": {
    "type": "int",
    "repr": "10"
  },
  "new_value": {
    "type": "int",
    "repr": "20"
  }
}
```

Perubahan type juga harus terlihat.

Contoh:

```python
x = 10
x = "hello"
```

Event:

```text
int
 ↓
str
```

---

# 10. `input_requested`

Program sedang menunggu input.

```json
{
  "type": "input_requested",
  "line": 1,
  "prompt": "Name: "
}
```

Execution state:

```text
WAITING_FOR_INPUT
```

Frontend harus menampilkan input UI.

---

# 11. `input_received`

User memberikan input.

```json
{
  "type": "input_received",
  "line": 1,
  "value": "Diva"
}
```

Catatan:

`input()` Python selalu menghasilkan string sebelum diproses oleh program.

Contoh:

```python
age = int(input())
```

event input:

```json
{
  "value": "20"
}
```

sedangkan variable:

```json
{
  "type": "int",
  "repr": "20"
}
```

---

# 12. `output`

Menandakan program menghasilkan output.

```json
{
  "type": "output",
  "line": 4,
  "stream": "stdout",
  "value": "Hello"
}
```

Untuk error output:

```json
{
  "type": "output",
  "stream": "stderr",
  "value": "..."
}
```

---

# 13. `function_call`

Menandakan function invocation.

```json
{
  "type": "function_call",
  "line": 8,
  "function": "calculate",
  "frame_id": "frame_002",
  "arguments": {
    "a": {
      "type": "int",
      "repr": "10"
    },
    "b": {
      "type": "int",
      "repr": "20"
    }
  }
}
```

---

# 14. `function_return`

Menandakan function selesai dan menghasilkan return value.

```json
{
  "type": "function_return",
  "line": 4,
  "function": "calculate",
  "frame_id": "frame_002",
  "value": {
    "type": "int",
    "repr": "30"
  }
}
```

Jika function tidak memiliki explicit `return`:

```python
def hello():
    print("Hello")
```

Python menghasilkan:

```text
None
```

Event:

```json
{
  "type": "function_return",
  "value": {
    "type": "NoneType",
    "repr": "None"
  }
}
```

---

# 15. `exception`

Menandakan exception terjadi.

```json
{
  "type": "exception",
  "line": 4,
  "frame_id": "frame_001",
  "exception": {
    "type": "TypeError",
    "message": "unsupported operand type(s)..."
  }
}
```

Exception harus mempertahankan:

```text
type
message
line
frame
```

Execution state berubah menjadi:

```text
ERROR
```

---

# 16. `program_end`

Menandakan program selesai normal.

```json
{
  "type": "program_end",
  "status": "completed"
}
```

Tidak boleh ada execution event normal setelah `program_end`.

---

# 17. `timeout`

Menandakan execution dihentikan karena melewati batas waktu.

```json
{
  "type": "timeout",
  "limit_ms": 3000
}
```

State:

```text
TIMEOUT
```

---

# 18. `security_violation`

Menandakan sandbox menghentikan program karena operasi yang dilarang.

```json
{
  "type": "security_violation",
  "reason": "network_access_blocked"
}
```

State:

```text
SECURITY_VIOLATION
```

---

# 19. Value Representation

Raw Python objects tidak boleh dikirim langsung.

Gunakan safe value representation.

## Primitive

```json
{
  "type": "int",
  "repr": "42"
}
```

```json
{
  "type": "str",
  "repr": "'hello'"
}
```

```json
{
  "type": "bool",
  "repr": "True"
}
```

```json
{
  "type": "NoneType",
  "repr": "None"
}
```

---

# 20. Collection Representation

List:

```json
{
  "type": "list",
  "repr": "[1, 2, 3]",
  "length": 3
}
```

Dictionary:

```json
{
  "type": "dict",
  "repr": "{'name': 'Diva'}",
  "length": 1
}
```

Collection inspection harus memiliki batas ukuran.

Contoh:

```text
MAX_REPR_LENGTH
MAX_COLLECTION_ITEMS
MAX_NESTING_DEPTH
```

---

# 21. Object Representation

Object kompleks tidak boleh di-expand tanpa batas.

Contoh:

```json
{
  "type": "User",
  "repr": "<User object>",
  "inspectable": true
}
```

Object inspection dilakukan secara controlled.

Tujuannya:

- mencegah output terlalu besar;
- mencegah recursive structures;
- mencegah side effects;
- menjaga security.

---

# 22. Frame Schema

Execution frame:

```json
{
  "frame_id": "frame_001",
  "function": "calculate",
  "scope": "local",
  "line": 5,
  "variables": {
    "a": {
      "type": "int",
      "repr": "10"
    }
  }
}
```

Frame minimal memiliki:

```text
frame_id
function
scope
line
variables
```

---

# 23. Call Stack Schema

```json
{
  "call_stack": [
    {
      "frame_id": "frame_002",
      "function": "calculate",
      "line": 5,
      "scope": "local"
    },
    {
      "frame_id": "frame_001",
      "function": "<module>",
      "line": 8,
      "scope": "global"
    }
  ]
}
```

Urutan harus konsisten.

Frame paling atas merupakan currently active frame.

---

# 24. State Snapshot Schema

Current execution state:

```json
{
  "status": "PAUSED",
  "current_line": 5,
  "current_frame_id": "frame_002",
  "variables": {},
  "call_stack": [],
  "stdout": "",
  "stderr": "",
  "exception": null
}
```

State status:

```text
CREATED
STARTING
RUNNING
WAITING_FOR_INPUT
PAUSED
COMPLETED
ERROR
TIMEOUT
SECURITY_VIOLATION
```

---

# 25. Complete Event Example

Program:

```python
x = int(input("Number: "))
y = x + 10
print(y)
```

Execution sequence:

```json
[
  {
    "sequence": 1,
    "type": "program_start"
  },
  {
    "sequence": 2,
    "type": "line",
    "line": 1
  },
  {
    "sequence": 3,
    "type": "input_requested",
    "line": 1,
    "prompt": "Number: "
  },
  {
    "sequence": 4,
    "type": "input_received",
    "line": 1,
    "value": "20"
  },
  {
    "sequence": 5,
    "type": "variable_created",
    "line": 1,
    "variable": "x",
    "value": {
      "type": "int",
      "repr": "20"
    }
  },
  {
    "sequence": 6,
    "type": "line",
    "line": 2
  },
  {
    "sequence": 7,
    "type": "variable_created",
    "line": 2,
    "variable": "y",
    "value": {
      "type": "int",
      "repr": "30"
    }
  },
  {
    "sequence": 8,
    "type": "line",
    "line": 3
  },
  {
    "sequence": 9,
    "type": "output",
    "line": 3,
    "stream": "stdout",
    "value": "30"
  },
  {
    "sequence": 10,
    "type": "program_end",
    "status": "completed"
  }
]
```

---

# 26. Event vs State

Event:

> Sesuatu yang terjadi.

State:

> Kondisi program sekarang.

Contoh:

```text
EVENT:
x berubah dari 10 menjadi 20

STATE:
x sekarang 20
```

Keduanya harus dipisahkan.

---

# 27. AI Consumption

AI tidak perlu menerima semua metadata internal.

AI Context Builder dapat memilih:

```text
Current Event
+
Current State
+
Relevant History
+
Relevant Source Lines
+
Relevant Python Knowledge
```

Contoh:

```json
{
  "current_event": {
    "type": "exception",
    "line": 4
  },
  "current_state": {
    "variables": {
      "x": {
        "type": "int",
        "repr": "10"
      },
      "y": {
        "type": "str",
        "repr": "'5'"
      }
    }
  }
}
```

AI kemudian dapat menjelaskan error berdasarkan fakta tersebut.

---

# 28. Frontend Consumption

Frontend menggunakan event untuk:

```text
line
→ highlight current line

variable_created
→ add variable

variable_updated
→ animate state change

input_requested
→ show input field

output
→ append output

function_call
→ update call stack

function_return
→ pop call stack

exception
→ show error

program_end
→ show completed
```

---

# 29. Event Immutability

Setelah event dibuat, event tidak boleh diubah.

Contoh:

```text
event #5
x = 10
```

tetap menjadi fakta historis.

Ketika x menjadi 20:

```text
event #8
x = 20
```

Jangan mengubah event #5 menjadi 20.

Ini memungkinkan execution timeline direkonstruksi.

---

# 30. Event Sequence Integrity

Event sequence harus:

```text
1
2
3
4
5
...
```

Tidak boleh:

```text
1
2
7
3
```

Jika event diproses asynchronous, ordering harus tetap dapat direkonstruksi menggunakan `sequence`.

---

# 31. Schema Versioning

Event contract harus memiliki version.

Contoh:

```json
{
  "schema_version": "1.0",
  "type": "line",
  "line": 5
}
```

Jika schema berubah:

```text
1.0
1.1
2.0
```

Perubahan breaking harus menaikkan major version.

---

# 32. Error Contract

Error pada engine sendiri harus dibedakan dari Python exception user.

### User Python Exception

```text
TypeError
ValueError
NameError
```

### Engine Error

```text
ENGINE_ERROR
```

### Security Error

```text
SECURITY_VIOLATION
```

### Infrastructure Error

```text
SANDBOX_ERROR
TIMEOUT
```

AI harus mengetahui perbedaannya.

---

# 33. Source of Truth Rule

Untuk semua event:

```text
Runtime
    ↓
Event
    ↓
State
```

Bukan:

```text
Source Code
    ↓
LLM Guess
    ↓
Event
```

Event tidak boleh dibuat berdasarkan prediksi AI.

---

# 34. Definition of Done

Event schema dianggap valid apabila:

1. semua MVP execution events memiliki format;
2. event memiliki ordering;
3. variable state dapat direkonstruksi;
4. call stack dapat direkonstruksi;
5. input/output dapat direkonstruksi;
6. exception dapat direkonstruksi;
7. frontend dapat menggunakannya tanpa memahami Python internals;
8. AI dapat membuat context dari event;
9. event dapat disimpan dan diputar kembali;
10. schema dapat di-version.

---

# 35. Final Contract

```text
              EXECUTION ENGINE
                     │
                     │
              Normalized Events
                     │
                     ▼
             ┌───────────────┐
             │ EVENT SCHEMA  │
             └───────┬───────┘
                     │
          ┌──────────┼──────────┐
          ▼          ▼          ▼
      Frontend       AI       History
```

**Event = immutable record of something that happened.**

**State = current snapshot of the program.**

**Source code = what the user wrote.**

Ketiganya harus tetap dipisahkan.
