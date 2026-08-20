# Python Execution Flow Tutor

Aplikasi pembelajaran Python yang memvisualisasikan proses eksekusi program secara step-by-step.

> Repo ini saya buat **full menggunakan AI (Claude)** sebagai bagian dari proses belajar Python saya.  
> Saya tidak copy-paste tutorial — saya belajar dengan membangun sesuatu yang nyata, sambil memahami setiap keputusan teknis yang dibuat.

---

## Kenapa proyek ini ada?

Belajar Python itu mudah sampai di titik tertentu. Tapi begitu program mulai kompleks — ada `if/else`, loop, function, scope — banyak pemula (termasuk saya) bingung: **"Python lagi ngapain sekarang?"**

Proyek ini menjawab pertanyaan itu secara visual.

---

## Apa yang dilakukan aplikasi ini?

Kamu tulis kode Python, tekan Run, lalu aplikasi menunjukkan:

- **Baris mana yang sedang dieksekusi** (arrow bergerak mengikuti eksekusi nyata)
- **Perubahan variabel** (nilai dan tipe data, setiap kali berubah)
- **Call stack** (saat function dipanggil dan return)
- **Output dan error** (stdout / stderr)
- **AI Tutor** yang bertanya *sebelum* menjelaskan — bukan langsung kasih jawaban

Prinsip belajarnya:

```
TULIS KODE
    ↓
PREDIKSI apa yang akan terjadi
    ↓
JALANKAN
    ↓
AMATI eksekusi
    ↓
AI BERTANYA untuk memastikan kamu paham
    ↓
JELASKAN dengan kata-katamu sendiri
```

---

## Tech Stack

| Layer | Teknologi |
|---|---|
| Frontend | Next.js 15 + TypeScript + Tailwind CSS |
| Backend | Python + FastAPI + WebSocket |
| Execution Engine | Python `sys.settrace` (real tracing, bukan simulasi) |
| AI Tutor | LLM API (OpenAI / Anthropic) |

---

## Status Pengembangan

Proyek ini dibangun secara inkremental mengikuti 30-task roadmap.

| Task | Deskripsi | Status |
|---|---|---|
| 01 | Repository Audit | ✅ |
| 02 | Project Skeleton | ✅ |
| 03 | Domain Types | ✅ |
| 04 | Event Schema | ✅ |
| 05 | Execution Prototype | ✅ |
| 06-30 | Session, Tracing, UI, AI, dst. | 🔄 In Progress |

---

## Catatan

Seluruh kode, arsitektur, dan keputusan teknis dalam repo ini dihasilkan bersama AI.  
Saya memahami setiap bagian yang dibuat — bukan sekadar menjalankan perintah.

Tujuan akhirnya bukan hanya aplikasi yang jalan, tapi **pemahaman yang nyata tentang bagaimana Python bekerja**.
