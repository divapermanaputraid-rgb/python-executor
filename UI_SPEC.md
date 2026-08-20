# Python Execution Flow Tutor — UI Specification

## 1. Purpose

UI dirancang untuk membantu learner memahami **alur eksekusi Python secara visual**.

Tujuan utama:

> User dapat melihat kode yang ditulis, melihat bagian yang sedang dieksekusi, melihat perubahan state, melihat output, dan memahami alasan terjadinya sesuatu.

UI bukan IDE penuh.

UI bukan debugger profesional.

UI adalah **learning interface untuk execution flow**.

---

# 2. Core Learning Experience

User menulis:

```python
x = 10
y = x + 5
print(y)
```

Kemudian menekan:

```text
RUN
```

Program berjalan dan UI menunjukkan:

```text
→ x = 10
```

kemudian:

```text
→ y = x + 5
```

kemudian:

```text
→ print(y)
```

Sambil menunjukkan perubahan:

```text
x = 10
y = 15
```

Tujuan akhirnya:

```text
User
 ↓
Predict
 ↓
Execute
 ↓
Observe
 ↓
Explain
 ↓
Understand
```

---

# 3. Main Layout

MVP menggunakan 4 primary sections:

```text
┌───────────────────────────────┬───────────────────────────────┐
│                               │                               │
│          CODE                │         EXECUTION             │
│                               │                               │
│      Python Editor            │     Current Execution         │
│                               │     Timeline / Controls       │
│                               │                               │
├───────────────────────────────┼───────────────────────────────┤
│                               │                               │
│        STATE / RESULT         │         AI EXPLANATION        │
│                               │                               │
│ Variables                     │ Explanation                  │
│ Call Stack                    │ Hint                         │
│ Output                        │ Prediction                   │
│ Errors                        │ Question                     │
│                               │                               │
└───────────────────────────────┴───────────────────────────────┘
```

---

# 4. Section 1 — Code

Code panel merupakan area untuk menulis Python.

Contoh:

```text
1 │ x = 10
2 │ y = x + 5
3 │ print(y)
```

Features MVP:

- syntax highlighting;
- line numbers;
- editable code;
- current-line indicator;
- current-line highlight;
- read-only mode saat execution tertentu jika diperlukan.

---

# 5. Current Line Indicator

Current line harus sangat jelas.

Contoh:

```text
1 │ x = 10
2 │ → y = x + 5
3 │ print(y)
```

Arrow:

```text
→
```

merupakan representasi visual dari:

```text
state.current_line
```

Arrow tidak boleh ditentukan frontend berdasarkan tebakan.

Backend/Execution Engine menentukan current line.

---

# 6. Current Line Highlight

Current line diberi visual emphasis.

Contoh:

```text
1 │ x = 10
2 │ [ y = x + 5 ]
3 │ print(y)
```

Highlight harus tetap terlihat ketika:

- step;
- continue;
- function call;
- loop;
- exception.

---

# 7. Execution Controls

Control bar:

```text
┌─────────────────────────────────────┐
│ ▶ Run │ ⏭ Step │ ▶ Continue │ ■ Stop │
└─────────────────────────────────────┘
```

MVP:

### Run

Memulai execution dari awal.

### Step

Menjalankan execution ke execution point berikutnya.

### Continue

Melanjutkan execution sampai execution point berikutnya yang relevan.

### Stop

Menghentikan execution.

---

# 8. Execution Modes

State UI:

```text
IDLE
RUNNING
PAUSED
WAITING_FOR_INPUT
COMPLETED
ERROR
STOPPED
```

Control availability harus bergantung pada state.

Contoh:

```text
IDLE
→ Run enabled

RUNNING
→ Stop enabled

PAUSED
→ Step
→ Continue
→ Stop

WAITING_FOR_INPUT
→ Input required

COMPLETED
→ Run
```

---

# 9. Execution Timeline

Execution section menampilkan perjalanan program.

Contoh:

```text
Execution Timeline

● Program started
│
● Line 1
│
● x created = 10
│
● Line 2
│
● y created = 15
│
● Line 3
│
● Output = 15
│
● Program completed
```

Timeline berasal dari execution events.

---

# 10. Event Detail

User dapat memilih event.

Contoh:

```text
● variable_updated
```

UI dapat menampilkan:

```text
Variable
x

Previous
10

Current
20

Type
int → int

Line
4
```

Tujuannya membuat perubahan state eksplisit.

---

# 11. Section 2 — Execution

Execution panel menunjukkan:

```text
Current Line
Execution Status
Timeline
Controls
```

Contoh:

```text
STATUS
PAUSED

CURRENT
Line 4

EVENT
variable_updated

x
10 → 20
```

---

# 12. Input State

Ketika Python menjalankan:

```python
name = input("Name: ")
```

Execution panel berubah:

```text
WAITING FOR INPUT

Name:
┌──────────────────────┐
│                      │
└──────────────────────┘

[Submit]
```

Execution harus berhenti sampai user mengirim input.

---

# 13. Input Validation

Input tidak boleh dikirim tanpa execution session yang valid.

Frontend mengirim:

```text
session_id
input_value
```

Backend meneruskan ke execution engine.

---

# 14. Section 3 — State / Result

Section ini menunjukkan keadaan program saat ini.

Minimal:

```text
Variables
Call Stack
Output
Errors
```

---

# 15. Variables

Contoh:

```text
VARIABLES

x
10
int

y
15
int
```

Jika variable berubah:

```text
x
10 → 20
```

UI harus membuat perubahan terlihat.

---

# 16. Variable History

User dapat melihat:

```text
x

10
↓
20
↓
30
```

Feature ini berguna untuk memahami assignment dan mutation.

MVP dapat hanya menampilkan current state.

History dapat ditambahkan setelah event system stabil.

---

# 17. Type Display

Type harus ditampilkan.

Contoh:

```text
x
10
int
```

dan:

```text
name
"Diva"
str
```

Tujuannya membantu user menghubungkan:

```text
value
+
type
```

---

# 18. Call Stack

Contoh:

```text
CALL STACK

calculate()
line 5

main
line 10
```

Saat function return:

```text
calculate()
```

hilang dari stack.

Visualisasi ini penting untuk memahami function execution.

---

# 19. Output

Output panel:

```text
OUTPUT

Hello Diva
Age: 20
```

stdout dan stderr dibedakan.

Contoh:

```text
OUTPUT
Hello

ERROR OUTPUT
Traceback...
```

---

# 20. Error Display

Jika terjadi:

```python
x = 10
y = "5"

print(x + y)
```

UI:

```text
┌──────────────────────────────┐
│ ERROR                        │
│                              │
│ TypeError                    │
│                              │
│ Line 4                       │
│                              │
│ print(x + y)                 │
└──────────────────────────────┘
```

Jangan langsung menampilkan penjelasan panjang AI di error box.

Error box menunjukkan **fakta runtime**.

Penjelasan berada di AI section.

---

# 21. Error Line Highlight

Line error diberi indikator:

```text
1 │ x = 10
2 │ y = "5"
3 │
4 │ ✕ print(x + y)
```

Current/error line berasal dari execution event.

---

# 22. Section 4 — AI Explanation

AI panel merupakan tutor.

Contoh:

```text
AI TUTOR

Python berhenti di line 4.

x memiliki type int.
y memiliki type str.

Sebelum saya jelaskan lebih lanjut:

Menurutmu apa yang terjadi ketika
int + str dijalankan?

[Your answer...]
```

AI tidak langsung memberikan jawaban ketika prediction masih diperlukan.

---

# 23. Prediction Interaction

Flow:

```text
Execution
    ↓
Pause
    ↓
AI asks prediction
    ↓
User answers
    ↓
AI evaluates
    ↓
Hint / Explanation
```

Contoh:

```text
What will y contain after this line?

y = x + 5

Your prediction:
[____________]

[Check]
```

---

# 24. Explanation Modes

AI dapat memiliki beberapa mode:

```text
QUESTION
HINT
EXPLANATION
ERROR_EXPLANATION
SUMMARY
```

### QUESTION

Meminta learner memprediksi.

### HINT

Memberi petunjuk tanpa memberikan jawaban penuh.

### EXPLANATION

Menjelaskan konsep.

### ERROR_EXPLANATION

Menjelaskan penyebab exception.

### SUMMARY

Merangkum execution setelah program selesai.

---

# 25. AI Must Know Current State

AI context minimal:

```text
Source Code
Current Line
Current Event
Current State
Relevant Execution History
```

AI tidak boleh hanya menerima source code.

Contoh buruk:

```text
AI:
"Sepertinya x mungkin bernilai 10."
```

Jika runtime state sudah tersedia:

```text
x = 20
```

AI harus menggunakan fakta tersebut.

---

# 26. AI Loading State

Saat AI sedang menghasilkan response:

```text
AI is analyzing current execution...
```

Tetapi execution engine tidak boleh berhenti secara internal hanya karena AI sedang loading kecuali execution flow memang dirancang untuk menunggu pedagogical interaction.

---

# 27. Execution vs AI Synchronization

Dua mode dapat digunakan.

### Mode A — Execution First

```text
Execute
 ↓
Pause
 ↓
AI explanation
```

### Mode B — Prediction First

```text
AI question
 ↓
User prediction
 ↓
Execute
 ↓
Compare prediction
```

Learning Engine menentukan mode.

---

# 28. Beginner Mode

Untuk learner baru:

```text
Step
 ↓
Observe
 ↓
Question
 ↓
Explain
```

AI memberikan lebih banyak guidance.

---

# 29. Advanced Mode

Untuk learner lebih kuat:

```text
Prediction
 ↓
Step
 ↓
Compare
 ↓
Minimal explanation
```

AI tidak terlalu banyak menjelaskan.

---

# 30. Execution Speed

MVP tidak perlu real-time animation kompleks.

Gunakan discrete state transitions:

```text
Step 1
 ↓
Step 2
 ↓
Step 3
```

Future:

```text
slow
normal
fast
```

Animation hanya presentation.

Source of truth tetap execution events.

---

# 31. Execution Arrow

Arrow current line harus mengikuti:

```text
state.current_line
```

Bukan:

```text
frontend timer
```

Jangan membuat:

```text
line 1 → wait 1 second → line 2
```

karena execution Python tidak selalu membutuhkan waktu yang sama.

---

# 32. Loop Visualization

Contoh:

```python
for i in range(3):
    print(i)
```

UI:

```text
→ for i in range(3):

Iteration: 1
i = 0

Iteration: 2
i = 1

Iteration: 3
i = 2
```

Jika metadata iteration belum tersedia secara reliable, UI hanya menunjukkan execution events aktual.

---

# 33. Function Visualization

Contoh:

```text
main
 │
 ▼
calculate()
 │
 ├── a = 10
 ├── b = 20
 └── return 30
 │
 ▼
main
 │
 └── result = 30
```

Call stack menjadi sumber data utama.

---

# 34. Responsive Layout

Desktop-first untuk MVP.

Layout:

```text
2 × 2 grid
```

Tablet:

```text
Code
Execution

State
AI
```

Mobile:

```text
Code
↓
Execution
↓
State
↓
AI
```

---

# 35. Accessibility

Minimal:

- keyboard navigation;
- readable contrast;
- screen-reader-friendly labels;
- tidak hanya mengandalkan warna;
- error harus memiliki text label;
- current line memiliki indicator selain highlight.

Contoh:

```text
→ Line 4
```

lebih baik daripada hanya memberi warna background.

---

# 36. Loading / Network Errors

Jika AI gagal:

```text
AI Tutor unavailable.

Execution state is still preserved.
```

Execution tidak boleh dianggap gagal hanya karena AI API gagal.

Architecture:

```text
Execution
     │
     ├────→ Frontend
     │
     └────→ AI
```

Bukan:

```text
Execution
     ↓
AI
     ↓
Frontend
```

---

# 37. Offline Execution

Jika memungkinkan, execution state tetap dapat ditampilkan tanpa AI.

Minimal:

```text
Code
Execution
State
Output
```

AI merupakan enhancement terhadap execution experience, bukan dependency untuk menjalankan Python.

---

# 38. State Persistence

Jika user refresh atau reconnect:

execution session dapat direstore jika backend masih menyimpan session.

Frontend tidak boleh menjadi satu-satunya tempat penyimpanan execution state.

---

# 39. UI Data Flow

```text
Python Execution Engine
          │
          ▼
    Execution Event
          │
          ▼
       Backend
          │
      ┌───┴────┐
      ▼        ▼
   Frontend    AI
      │        │
      ▼        ▼
    Visual   Explanation
```

---

# 40. UI State Model

Frontend state minimal:

```text
code
session
executionStatus
currentLine
currentEvent
executionHistory
variables
callStack
stdout
stderr
error
aiMessage
aiMode
inputRequest
```

Frontend state harus berasal dari backend/event stream.

---

# 41. UI Must Not Infer Runtime

Frontend tidak boleh melakukan:

```text
if currentLine === 5:
    assume x changed
```

Frontend harus menerima:

```text
variable_updated
```

dari execution system.

Dengan demikian UI tidak mengandung business logic Python.

---

# 42. MVP Screen

MVP hanya membutuhkan satu primary screen:

```text
┌─────────────────────────────────────────────────────────┐
│ Python Execution Flow Tutor                             │
├────────────────────────┬────────────────────────────────┤
│ CODE                   │ EXECUTION                      │
│                        │                                │
│ 1 x = 10               │ Status: PAUSED                │
│ 2 y = x + 5            │ → Line 2                      │
│ 3 print(y)             │                                │
│                        │ [Run] [Step] [Continue] [Stop]│
├────────────────────────┼────────────────────────────────┤
│ STATE / RESULT         │ AI TUTOR                       │
│                        │                                │
│ Variables              │ Why is y equal to 15?          │
│ x = 10 int             │                                │
│ y = 15 int             │ Your prediction:              │
│                        │ [________________]             │
│ Output                 │                                │
│ 15                     │ [Submit]                       │
└────────────────────────┴────────────────────────────────┘
```

---

# 43. Visual Hierarchy

Prioritas visual:

```text
1. Current execution line
2. Current runtime state
3. User interaction
4. Execution history
5. AI explanation
6. Secondary metadata
```

Jangan membuat AI panel lebih dominan daripada execution state.

Produk ini mengajarkan execution flow, bukan sekadar chat dengan AI.

---

# 44. Definition of Done

UI MVP dianggap selesai apabila user dapat:

1. menulis Python;
2. menjalankan Python;
3. melihat current line;
4. melihat arrow bergerak mengikuti execution;
5. melakukan Step;
6. melakukan Continue;
7. memasukkan input;
8. melihat output;
9. melihat variable;
10. melihat type;
11. melihat call stack;
12. melihat error line;
13. melihat execution timeline;
14. menerima AI explanation;
15. menjawab prediction;
16. menjalankan program tanpa AI.

---

# 45. Fundamental UI Principle

```text
CODE
 ↓
EXECUTION
 ↓
STATE
 ↓
MEANING
```

Bukan:

```text
CODE
 ↓
CHATBOT
 ↓
ANSWER
```

UI harus membuat **execution terlihat terlebih dahulu**, baru AI memberikan interpretasi.
