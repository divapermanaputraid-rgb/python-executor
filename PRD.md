# Product Requirements Document (PRD)

## Python Execution Flow Tutor

### 1. Product Overview

**Python Execution Flow Tutor** adalah aplikasi pembelajaran Python yang memvisualisasikan proses eksekusi program secara step-by-step.

Fokus utama aplikasi bukan menghasilkan kode atau memberikan jawaban langsung, tetapi membuat pengguna **melihat dan memahami bagaimana Python mengeksekusi kode**.

Prinsip pembelajaran:

> **Predict → Execute → Observe → Explain → Recall**

Pengguna menulis kode sendiri, menjalankannya, memberikan input ketika program meminta input, kemudian melihat execution flow secara visual.

---

# 2. Problem

Pemula sering memahami Python sebagai:

```text
tulis kode → jalankan → keluar hasil
```

Padahal proses sebenarnya melibatkan:

- statement execution
- variable creation
- assignment
- expression evaluation
- branching
- loop iteration
- function call
- return
- scope
- call stack
- exception
- perubahan state

Masalahnya, proses tersebut tidak terlihat secara langsung.

Akibatnya pengguna dapat mengetahui **apa output program**, tetapi tidak memahami **mengapa output tersebut muncul**.

---

# 3. Product Goal

Aplikasi harus membuat pengguna mampu menjawab:

> "Python sedang melakukan apa sekarang?"

dan:

> "Kenapa Python berpindah ke baris tersebut?"

setelah melihat execution flow sebuah program.

### Success Criteria

Setelah menggunakan aplikasi, pengguna diharapkan mampu:

1. mengikuti eksekusi baris demi baris;
2. memahami perubahan variable;
3. memahami alur `if/else`;
4. memahami iterasi `for` dan `while`;
5. memahami function call dan `return`;
6. memahami basic scope dan call stack;
7. menemukan lokasi terjadinya error;
8. menjelaskan penyebab error sebelum melihat solusi.

---

# 4. Target User

### Primary User

Pemula Python yang sudah mengetahui basic syntax tetapi belum memiliki mental model execution flow.

Contoh:

- mengetahui `if`;
- mengetahui `for`;
- mengetahui function;
- bisa membuat program sederhana;
- tetapi masih bingung ketika program semakin kompleks.

### Non-Goal

Aplikasi bukan:

- AI code generator;
- autocomplete IDE;
- competitive programming platform;
- full replacement untuk VS Code/PyCharm;
- automatic homework solver.

---

# 5. Core UX

UI utama terdiri dari **4 section**.

```text
┌─────────────────────────────┬─────────────────────────────┐
│                             │                             │
│  1. CODE                    │  2. EXECUTION              │
│                             │                             │
│  Python source code         │  → current line             │
│                             │    highlighted              │
│                             │                             │
├─────────────────────────────┼─────────────────────────────┤
│                             │                             │
│  3. RESULT / STATE          │  4. EXPLANATION             │
│                             │                             │
│  Output                     │  AI explanation              │
│  Variables                  │  Prediction questions       │
│  Types                      │  Error explanation           │
│  Call Stack                 │                             │
│  Exceptions                 │                             │
└─────────────────────────────┴─────────────────────────────┘
```

---

# 6. Section 1 — CODE

Pengguna menulis kode Python.

Contoh:

```python
name = input("Nama: ")
age = int(input("Umur: "))

if age >= 18:
    status = "adult"
else:
    status = "minor"

print(status)
```

Features:

- syntax highlighting;
- line numbers;
- Run;
- Pause;
- Continue;
- Step;
- Reset;
- editable source code.

### Important

Aplikasi tidak boleh langsung memberikan penjelasan ketika kode ditulis.

Pengguna harus terlebih dahulu menjalankan program.

---

# 7. Section 2 — EXECUTION

Ini merupakan **core feature** aplikasi.

Current execution line diberikan indikator visual:

```text
 1  name = input("Nama: ")
 2  age = int(input("Umur: "))

→3  if age >= 18:

 4      status = "adult"
 5  else:
 6      status = "minor"

 7  print(status)
```

Indikator harus berpindah mengikuti execution state Python.

### Execution States

Minimal:

```text
RUNNING
WAITING_FOR_INPUT
PAUSED
COMPLETED
ERROR
```

### Controls

```text
▶ Run
⏸ Pause
→ Step
▶ Continue
↻ Reset
```

### Input

Jika program melakukan:

```python
name = input("Nama: ")
```

execution harus berhenti pada input.

UI menampilkan:

```text
Program meminta input:

Nama: [____________]

                 [Submit]
```

Program baru melanjutkan setelah pengguna memberikan input.

---

# 8. Section 3 — RESULT / STATE

Section ini tidak hanya menampilkan output.

Aplikasi harus menampilkan keadaan program saat execution berlangsung.

### Output

```text
OUTPUT

Nama: Diva
Umur: 22
adult
```

### Variables

```text
VARIABLES

name
value: "Diva"
type: str

age
value: 22
type: int

status
value: "adult"
type: str
```

### State Changes

Jika sebelumnya:

```text
status = undefined
```

kemudian:

```python
status = "adult"
```

UI menunjukkan:

```text
status

undefined
   ↓
"adult"
```

Tujuannya agar pengguna melihat **state transition**, bukan hanya state akhir.

---

# 9. Section 4 — AI EXPLANATION

AI bertugas sebagai tutor execution, bukan code generator.

AI menerima execution context seperti:

```text
Source code
Current line
Previous line
Variables
Variable types
Call stack
Input
Output
Exception
Execution history
User answers
```

Kemudian menghasilkan penjelasan berdasarkan state tersebut.

---

# 10. Prediction-First System

AI tidak boleh selalu langsung memberikan jawaban.

Contoh:

```python
x = "10"
y = int(x)
```

Ketika execution mencapai:

```python
→ y = int(x)
```

AI bertanya:

> `x` saat ini bernilai `"10"` dan bertipe `str`.
>
> Menurutmu setelah baris ini dijalankan, `y` akan bertipe apa?

User menjawab.

Baru execution dilanjutkan.

### Rules

Jika user benar:

```text
Correct.

Let's execute the line.
```

Jika salah:

AI memberikan hint.

Jika user masih salah:

AI memberikan penjelasan lebih konkret.

Tujuannya:

```text
Prediction
    ↓
Attempt
    ↓
Execution
    ↓
Feedback
    ↓
Explanation
```

---

# 11. Error Visualization

Ketika terjadi error:

```python
x = 10
y = "5"

print(x + y)
```

Execution berhenti:

```text
 1  x = 10
 2  y = "5"

→3  print(x + y)
       ^^^^^
```

State:

```text
x = 10       int
y = "5"      str
```

AI tidak langsung memberikan solusi.

Pertanyaan:

> Python berhenti pada operasi `x + y`.
>
> Perhatikan tipe `x` dan `y`.
>
> Menurutmu apa yang menyebabkan error?

Setelah pengguna mencoba menjawab, AI menjelaskan.

---

# 12. Function Visualization

Ketika function dipanggil:

```python
def add(a, b):
    result = a + b
    return result

x = add(10, 20)
```

UI menampilkan call stack:

```text
CALL STACK

┌────────────────────┐
│ add()              │
│ a = 10             │
│ b = 20             │
│ result = 30        │
├────────────────────┤
│ global scope       │
│ x = undefined      │
└────────────────────┘
```

Current line:

```text
→ result = a + b
```

Ketika `return`:

```text
add()
   │
   │ return 30
   ▼
global scope

x = 30
```

Ini digunakan untuk membangun pemahaman tentang:

- function call;
- parameters;
- local variables;
- return;
- scope;
- call stack.

---

# 13. Loop Visualization

Untuk:

```python
for i in range(3):
    print(i)
```

aplikasi harus menunjukkan iteration state:

```text
ITERATION 1

i = 0

→ print(i)
```

kemudian:

```text
ITERATION 2

i = 1

→ print(i)
```

kemudian:

```text
ITERATION 3

i = 2

→ print(i)
```

AI dapat bertanya sebelum iteration berikutnya:

> `range(3)` sudah menghasilkan `0` dan `1`.
>
> Menurutmu nilai `i` berikutnya apa?

---

# 14. Execution History

Aplikasi menyimpan timeline:

```text
01  x = 10
02  y = 20
03  calculate(x, y)
04  enter calculate()
05  result = x + y
06  return result
07  print(result)
```

User dapat melihat kembali execution sebelumnya.

Tujuan:

**spaced recall dan debugging retrospektif.**

---

# 15. AI Context Architecture

AI tidak menjalankan Python secara langsung.

Architecture:

```text
                    ┌──────────────┐
                    │ Python Code  │
                    └──────┬───────┘
                           ↓
                    ┌──────────────┐
                    │ Python       │
                    │ Execution    │
                    │ Engine       │
                    └──────┬───────┘
                           ↓
                  Execution State
                           ↓
              ┌────────────┴────────────┐
              ↓                         ↓
       Visualization               AI Tutor
              ↓                         ↓
       User observes              User predicts
              └────────────┬────────────┘
                           ↓
                       Continue
```

AI mendapatkan **structured execution state**, bukan hanya source code.

---

# 16. MVP Scope

Jangan langsung membuat seluruh Python debugger.

### MVP Phase 1

Support:

- variable assignment;
- `print`;
- `input`;
- arithmetic;
- `if`;
- `else`;
- basic comparison;
- basic exceptions.

UI:

- Code;
- Execution;
- Result/State;
- Explanation.

Controls:

- Run;
- Step;
- Continue;
- Reset.

---

# 17. MVP Phase 2

Tambahkan:

- `for`;
- `while`;
- function;
- parameters;
- return;
- local/global scope;
- call stack.

---

# 18. MVP Phase 3

Tambahkan:

- error diagnosis;
- execution timeline;
- AI prediction;
- adaptive questioning;
- learning history;
- weak-topic detection.

---

# 19. Security Requirement

Kode pengguna harus dijalankan dalam **sandbox**.

Jangan menjalankan arbitrary Python langsung pada host/server utama.

Minimal:

```text
User Code
   ↓
Sandbox
   ↓
Restricted Python Runtime
   ↓
Execution Trace
   ↓
Application
```

Batasi:

- filesystem access;
- network access;
- subprocess;
- resource usage;
- execution time;
- memory.

---

# 20. Technical Direction

Untuk prototype awal:

### Backend

Python execution engine dapat menggunakan mekanisme debugging/tracing Python seperti:

- `sys.settrace`;
- debugger hooks;
- AST analysis bila diperlukan.

Execution engine menghasilkan event terstruktur:

```json
{
  "event": "line",
  "line": 5,
  "variables": {
    "x": {
      "value": 10,
      "type": "int"
    }
  },
  "call_stack": ["main"]
}
```

Event tersebut kemudian dikirim ke frontend.

Frontend tidak perlu memahami bagaimana Python bekerja secara internal. Frontend hanya memvisualisasikan execution state.

---

# 21. Example Complete Flow

User memasukkan:

```python
x = int(input("Number: "))

if x > 10:
    print("Large")
else:
    print("Small")
```

Execution:

```text
→ x = int(input(...))
```

Program meminta:

```text
Number: [ 15 ]
```

State:

```text
x = 15
type = int
```

Next:

```text
→ if x > 10:
```

AI:

> `x` bernilai `15`.
>
> Prediksi: branch mana yang akan dijalankan?

User:

```text
if / true branch
```

Execution:

```text
→ print("Large")
```

Output:

```text
Large
```

AI:

> Kondisi menghasilkan `True`, sehingga Python masuk ke blok `if` dan tidak menjalankan blok `else`.

Program selesai.

---

# 22. Core Learning Loop

Seluruh produk harus mengikuti pola:

```text
WRITE
  ↓
RUN
  ↓
INPUT
  ↓
OBSERVE
  ↓
PREDICT
  ↓
EXECUTE
  ↓
COMPARE
  ↓
EXPLAIN
  ↓
RECALL
```

Bukan:

```text
WRITE
  ↓
RUN
  ↓
AI GIVES ANSWER
```

Perbedaan ini merupakan inti produk.

---

# 23. Definition of Done — MVP

MVP dianggap berhasil apabila pengguna dapat menjalankan:

```python
name = input()
age = int(input())

if age >= 18:
    print("Adult")
else:
    print("Minor")
```

dan aplikasi mampu:

- menunjukkan current execution line;
- berhenti pada `input()`;
- menerima input pengguna;
- memperbarui variable state;
- menunjukkan tipe data;
- memvisualisasikan branch `if/else`;
- menunjukkan output;
- mendeteksi error sederhana;
- menunjukkan lokasi error;
- memberikan prediction question;
- menjelaskan execution berdasarkan state aktual.

**Prioritas pertama bukan AI. Prioritas pertama adalah membuat execution engine yang benar.**

Kalau execution engine salah, AI hanya akan memberikan penjelasan yang terlihat pintar tetapi berdasarkan state yang salah.
