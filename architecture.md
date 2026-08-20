# Python Execution Flow Tutor — System Architecture

## 1. Architecture Overview

Python Execution Flow Tutor menggunakan arsitektur modular dengan pemisahan tegas antara:

1. **Frontend** — menampilkan kode, execution flow, state, dan penjelasan.
2. **Backend/API** — mengatur session, execution lifecycle, dan komunikasi antar-komponen.
3. **Python Execution Engine** — menjalankan kode dan menghasilkan fakta runtime.
4. **AI Tutor** — menjelaskan execution state dan membimbing proses belajar.
5. **Knowledge Layer** — menyediakan referensi Python yang relevan untuk AI.
6. **Learning Engine** — mengelola prediction, feedback, recall, dan learner progress.

Prinsip utama:

> **Execution Engine determines what happened. AI Tutor explains what happened.**

AI tidak menjadi sumber kebenaran mengenai runtime.

---

# 2. High-Level Architecture

```text
                         USER
                          │
                          ▼
                ┌───────────────────┐
                │     FRONTEND      │
                │                   │
                │ ┌─────┐ ┌───────┐ │
                │ │Code │ │Execute│ │
                │ └─────┘ └───────┘ │
                │                   │
                │ ┌─────┐ ┌───────┐ │
                │ │State│ │ Tutor │ │
                │ └─────┘ └───────┘ │
                └─────────┬─────────┘
                          │
                          ▼
                ┌───────────────────┐
                │      BACKEND      │
                │                   │
                │ Execution Manager │
                │ Session Manager   │
                │ Context Builder   │
                └───────┬───────────┘
                        │
              ┌─────────┴─────────┐
              │                   │
              ▼                   ▼
     ┌─────────────────┐  ┌─────────────────┐
     │ PYTHON EXECUTION │  │    AI TUTOR     │
     │      ENGINE      │  │                 │
     │                  │  │ Explain         │
     │ Execute          │  │ Question        │
     │ Trace            │  │ Hint            │
     │ State            │  │ Feedback        │
     │ Exception        │  │                 │
     └────────┬─────────┘  └────────┬────────┘
              │                     │
              │ Runtime State       │
              │                     │
              ▼                     ▼
       ┌──────────────┐      ┌──────────────┐
       │ Event Stream │      │ Knowledge    │
       │ / State      │      │ Layer        │
       └──────────────┘      └──────────────┘
```

---

# 3. Component Responsibilities

## 3.1 Frontend

Frontend bertanggung jawab terhadap **visualisasi dan interaksi user**.

### Responsibilities

- code editor;
- execution controls;
- current-line indicator;
- execution highlighting;
- input interface;
- output display;
- variable state;
- data types;
- call stack;
- exception display;
- execution timeline;
- AI explanation;
- prediction interface.

Frontend tidak menentukan apakah suatu line benar-benar dieksekusi.

Frontend hanya menerima execution event/state dari backend.

---

# 4. Backend / API

Backend menjadi orchestration layer.

### Responsibilities

- membuat execution session;
- menerima source code;
- mengirim code ke execution engine;
- menerima execution events;
- menyimpan execution state;
- mengatur pause/resume/step;
- membangun AI context;
- mengirim context ke AI Tutor;
- mengirim response AI ke frontend;
- menyimpan learner progress.

Backend **tidak mengeksekusi Python secara langsung**.

Execution dilakukan oleh sandbox/execution engine.

---

# 5. Python Execution Engine

Execution Engine merupakan **source of truth untuk runtime**.

### Responsibilities

- menjalankan Python code;
- tracing execution;
- menentukan current line;
- menangkap variable state;
- menangkap data type;
- menangkap input;
- menangkap output;
- menangkap function call;
- menangkap return;
- menangkap exception;
- menghasilkan execution events;
- menghentikan dan melanjutkan execution.

Contoh output engine:

```json
{
  "event": "line",
  "line": 7,
  "locals": {
    "x": {
      "value": 20,
      "type": "int"
    }
  },
  "call_stack": [
    {
      "function": "<module>",
      "line": 7
    }
  ],
  "stdout": "",
  "exception": null
}
```

Engine tidak bertugas menjelaskan kode kepada user.

---

# 6. AI Tutor

AI Tutor bertanggung jawab terhadap **pedagogical reasoning**.

### Responsibilities

- menjelaskan execution;
- membuat prediction question;
- memberikan hint;
- memberikan feedback;
- menjelaskan error;
- menyesuaikan tingkat penjelasan;
- menghubungkan runtime state dengan konsep Python;
- membantu user membangun mental model.

AI menerima data dari execution engine.

AI tidak boleh mengubah runtime state.

---

# 7. Knowledge Layer

Knowledge Layer menyediakan referensi Python untuk AI.

Sumber utama:

- Python Language Reference;
- Python Tutorial;
- Python execution model;
- Python exceptions;
- Python debugging/tracing documentation.

Knowledge Layer menggunakan retrieval berdasarkan konsep yang sedang dieksekusi.

Contoh:

Jika current line:

```python
if age >= 18:
```

knowledge retrieval dapat mengambil:

```text
if statement
comparison
boolean expression
conditional execution
```

Tidak perlu mengirim seluruh dokumentasi Python kepada AI.

---

# 8. Learning Engine

Learning Engine menangani aspek pembelajaran.

### Responsibilities

- prediction-first interaction;
- difficulty adjustment;
- error pattern tracking;
- weak-topic detection;
- spaced recall;
- interleaving;
- learner progress.

Contoh:

```text
User repeatedly fails
        ↓
type conversion
        ↓
Learning Engine records weakness
        ↓
Future exercises include
type conversion
        ↓
AI asks targeted prediction
```

Learning Engine tidak menentukan runtime behavior.

---

# 9. Execution Flow

## Normal Execution

```text
User writes code
      ↓
Frontend
      ↓
Backend
      ↓
Execution Manager
      ↓
Python Sandbox
      ↓
Python Execution Engine
      ↓
Execution Event
      ↓
Backend
      ↓
Frontend
```

Contoh:

```text
line = 4
x = 20
type = int
```

Frontend kemudian menampilkan:

```text
→ line 4
```

---

# 10. Execution + AI Flow

Ketika AI diperlukan:

```text
Python Engine
      ↓
Runtime State
      ↓
Execution Manager
      ↓
AI Context Builder
      ↓
Relevant Knowledge Retrieval
      ↓
AI Tutor
      ↓
Prediction / Explanation / Hint
      ↓
Frontend
```

AI context harus berasal dari state aktual.

---

# 11. Input Flow

Ketika Python menjalankan:

```python
name = input("Nama: ")
```

Execution Engine menghasilkan:

```text
WAITING_FOR_INPUT
```

Frontend menampilkan input UI.

```text
User
 ↓
"John"
 ↓
Frontend
 ↓
Backend
 ↓
Execution Engine
 ↓
Python resumes
```

Execution Engine kemudian melanjutkan execution.

AI tidak mengintersep input sebagai sumber runtime.

---

# 12. Error Flow

Contoh:

```python
x = 10
y = "5"

print(x + y)
```

Execution Engine mendeteksi:

```text
event = exception
line = 4
exception_type = TypeError
```

State dikirim ke Backend.

Backend membangun context:

```text
Source Code
+
Current Line
+
Variables
+
Types
+
Exception
+
Execution History
```

AI Tutor kemudian melakukan:

```text
Show relevant state
        ↓
Ask hypothesis
        ↓
User attempts
        ↓
Hint
        ↓
Explanation
```

AI tidak menentukan bahwa error terjadi.

Execution Engine yang menentukan.

---

# 13. Function Call Flow

Ketika:

```python
result = calculate(10, 20)
```

Execution Engine menghasilkan event:

```text
call
```

Call stack:

```text
global
  ↓
calculate()
```

Ketika:

```python
return result
```

Engine menghasilkan:

```text
return
```

Call stack kembali:

```text
calculate()
  ↓
global
```

AI kemudian menjelaskan berdasarkan event tersebut.

---

# 14. Source of Truth Hierarchy

Ketika terdapat konflik informasi, sistem harus mengikuti prioritas:

```text
1. Runtime State
        ↓
2. Execution History
        ↓
3. Python Documentation
        ↓
4. AI Inference
```

AI inference memiliki prioritas paling rendah.

Contoh:

Jika AI memperkirakan:

```text
x = str
```

tetapi runtime mengatakan:

```text
x = int
```

maka:

```text
Runtime State wins.
```

AI harus mengikuti runtime.

---

# 15. Component Boundaries

### Frontend

**Owns:**

```text
UI
Interaction
Visualization
```

**Does not own:**

```text
Python execution
Runtime truth
AI reasoning
```

### Execution Engine

**Owns:**

```text
Python execution
Runtime state
Execution events
Exceptions
```

**Does not own:**

```text
UI
Learning strategy
AI explanation
```

### AI Tutor

**Owns:**

```text
Explanation
Questions
Hints
Pedagogy
```

**Does not own:**

```text
Runtime state
Code execution
Security sandbox
```

### Learning Engine

**Owns:**

```text
Learner model
Difficulty
Recall
Weak topics
```

**Does not own:**

```text
Python execution
```

---

# 16. Security Boundary

Python code dari user dianggap **untrusted code**.

Architecture:

```text
User Code
    ↓
Backend
    ↓
Sandbox Boundary
    ↓
Python Runtime
```

Execution Engine tidak boleh memiliki akses bebas terhadap host system.

Minimal isolation:

- filesystem;
- network;
- subprocess;
- CPU;
- memory;
- execution time.

Security menjadi boundary independen dari AI.

---

# 17. Communication Contracts

Komponen tidak boleh bergantung pada implementasi internal komponen lain.

Komunikasi menggunakan structured events.

Contoh:

```json
{
  "type": "execution.line",
  "line": 5,
  "frame_id": "frame-01",
  "locals": {},
  "call_stack": [],
  "stdout": "",
  "exception": null
}
```

Dengan demikian:

```text
Execution Engine
        ↓
Execution Event Contract
        ↓
Backend
        ↓
Frontend / AI
```

Jika execution engine diganti, selama contract tetap kompatibel, frontend dan AI tidak perlu ditulis ulang.

---

# 18. Extensibility

Architecture harus memungkinkan dukungan bahasa lain di masa depan.

Target potensial:

```text
Python Engine
JavaScript Engine
TypeScript Engine
```

Semua dapat menghasilkan execution event dengan abstraction yang serupa.

```text
Language Runtime
       ↓
Execution Adapter
       ↓
Normalized Execution Events
       ↓
Tutor System
```

Namun **MVP hanya mendukung Python**.

Jangan mengimplementasikan multi-language support sebelum Python execution model stabil.

---

# 19. Architectural Principle

Project mengikuti lima prinsip utama:

### 1. Runtime Truth First

Runtime menentukan fakta.

### 2. AI Is Not The Runtime

AI menjelaskan runtime, bukan menggantikannya.

### 3. Separation of Concerns

Execution, visualization, AI, dan learning memiliki boundary berbeda.

### 4. Structured State Over Raw Text

AI dan frontend menerima structured execution state.

### 5. Build The Engine Before The Tutor

Execution engine harus stabil sebelum AI tutor dibuat kompleks.

---

# 20. Initial Technology Direction

Prototype awal dapat menggunakan:

```text
Frontend
→ React / Next.js

Backend
→ Python API

Execution Engine
→ Python subprocess / isolated runtime
→ sys.settrace atau mekanisme tracing yang sesuai

AI
→ LLM API

Knowledge
→ Python official documentation

State
→ JSON execution events

Storage
→ PostgreSQL atau SQLite untuk MVP
```

Teknologi final belum dikunci dalam architecture ini.

Yang dikunci adalah **boundary dan responsibility**, bukan framework.

---

# 21. Architecture Success Criteria

Architecture dianggap valid apabila:

1. Python dapat dieksekusi tanpa AI.
2. Execution state dapat diperoleh tanpa AI.
3. Frontend dapat menampilkan execution state tanpa AI.
4. AI dapat dijalankan tanpa mengambil alih execution.
5. AI dapat diganti tanpa mengubah execution engine.
6. Execution engine dapat diganti tanpa mengubah pedagogical logic.
7. User code tetap terisolasi dari host system.
8. Runtime facts selalu dapat ditelusuri kembali ke execution event.

---

# 22. Final Architecture

```text
                         USER
                          │
                          ▼
                 ┌─────────────────┐
                 │    FRONTEND     │
                 │                 │
                 │ Code            │
                 │ Execution       │
                 │ State           │
                 │ Explanation     │
                 └────────┬────────┘
                          │
                          ▼
                 ┌─────────────────┐
                 │     BACKEND     │
                 │                 │
                 │ Session         │
                 │ Execution Mgmt  │
                 │ Context Builder │
                 └───────┬─────────┘
                         │
              ┌──────────┴──────────┐
              │                     │
              ▼                     ▼
     ┌─────────────────┐    ┌─────────────────┐
     │ PYTHON ENGINE   │    │    AI TUTOR     │
     │                 │    │                 │
     │ Execute         │    │ Predict         │
     │ Trace           │    │ Explain         │
     │ State           │    │ Hint            │
     │ Error           │    │ Feedback        │
     └────────┬────────┘    └────────┬────────┘
              │                      │
              ▼                      ▼
       Execution Events        Knowledge Layer
                                      │
                                      ▼
                              Python References

                 ┌─────────────────┐
                 │ LEARNING ENGINE │
                 │                 │
                 │ Recall          │
                 │ Interleaving    │
                 │ Difficulty      │
                 │ Weak Topics     │
                 └─────────────────┘
```

**Core boundary:**

```text
Python Engine → FACT
AI Tutor      → MEANING
Frontend      → VISUALIZATION
Learning      → ADAPTATION
Backend       → ORCHESTRATION
```
