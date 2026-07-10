# 🧠 Document Copilot: Pelajaran Arsitektur & Implementasi (Fase 1)

Dokumen ini merangkum konsep-konsep kritikal dan keputusan arsitektur yang dipelajari selama proses *setup* awal aplikasi **Document Copilot**. Rangkuman ini disusun secara berurutan sesuai alur penyelesaian masalah (*workflow*) yang kita jalani.

---

## 1. Arsitektur Makro (High-Level Architecture)
Aplikasi Document Copilot adalah aplikasi RAG (*Retrieval-Augmented Generation*) kelas *enterprise* yang berfokus pada akurasi dan sitasi. Arsitekturnya secara ketat membagi peran:
- **Frontend (Thin Client):** Dibangun dengan Vite + React SPA. Tugasnya murni hanya untuk merender UI, mengatur sesi login pengguna via Supabase Auth, dan menangani state *streaming* dari *chat* (menggunakan Vercel AI SDK).
- **Backend (Authoritative Server):** Dibangun menggunakan Python + FastAPI. Semua eksekusi cerdas dan otoritatif (pencarian dokumen, perangkaian *prompt*, eksekusi LLM via PydanticAI, validasi sitasi, dan manipulasi *database*) berpusat di sini.
- **Database & Identity:** Menggunakan Supabase (PostgreSQL). Tidak hanya untuk data relasional, tetapi juga mengeksploitasi `pgvector` untuk pencarian makna (semantik) dan *Postgres Full-Text Search* untuk pencarian kata kunci leksikal.

---

## 2. Manajemen Dependensi (Ekosistem `uv`)
Alih-alih menggunakan `pip`, `poetry`, atau `virtualenv` konvensional, proyek ini diarsiteki dengan **`uv`** (berbasis Rust).
- **Konsep Penting:** `uv` menyatukan *dependency resolution* dan manajemen *virtual environment* (`.venv`) menjadi satu langkah ultra-cepat.
- **Editable Package (`pyproject.toml`):** Untuk menghindari *error* fatal klasik seperti `ModuleNotFoundError` saat mengeksekusi skrip dari berbagai sub-folder (seperti folder `tests/`), kita mempraktekkan *editable install* (`uv pip install -e .`) dengan bantuan *build system* `hatchling`. Hal ini mengikat folder `app/` ke sistem sedemikian rupa sehingga `from app...` akan selalu berhasil tanpa memandang letak eksekusi (Current Working Directory).

---

## 3. Filosofi Environment Variables (Runtime vs Shell)
- **Konsep Penting:** Proyek modern memusatkan seluruh konfigurasi di sebuah modul statis. Di proyek ini, `AGENTS.md` melarang keras penggunaan `load_dotenv` maupun `os.getenv()`.
- **Pydantic Settings:** Sebagai gantinya, `pydantic-settings` diinstruksikan untuk mem-parsing file `.env` secara mandiri dari *disk* saat *runtime*.
- **Pelajaran Praktis:** Berkat arsitektur ini, aplikasi kita menjadi imun terhadap inkonsistensi *shell/terminal*. Peringatan dari IDE (seperti VS Code yang gagal meng-*inject* env ke terminal) dapat diabaikan 100% dengan aman, karena aplikasi Python kita tidak mengambil variabel dari terminal.

---

## 4. Manajemen Migrasi Database (Alembic & SQLAlchemy)
Ini adalah area di mana kebanyakan perancang sistem jatuh. Eksekusi ini mengajarkan perbedaan krusial antara abstraksi ORM dan realita *database engine*.

- **Transaction Pooler vs Direct/Session Connection:** 
  - *Transaction pooler* (seperti PgBouncer di Supabase) dirancang untuk memutus/menyambung sesi antar klien secara agresif demi efisiensi skala.
  - Namun, operasi DDL (*Data Definition Language*) yang berat—seperti `CREATE EXTENSION` atau memodifikasi tabel menggunakan Alembic—membutuhkan status kunci (*lock state*) dan sesi persisten yang utuh. 
  - **Aturan Emas:** Skrip migrasi harus selalu dieksekusi melalui **Direct/Session Connection URL** (Port 5432) dan dilarang dilewatkan melalui URL *transaction pooler*.

- **Kelemahan Autogenerate Alembic:**
  - Alembic (`--autogenerate`) sangat pintar dalam mendeteksi tabel biasa.
  - Namun, Alembic itu *database-agnostic* dan "buta" terhadap ekstensi tingkat lanjut yang spesifik eksklusif milik PostgreSQL (seperti `pgvector`, dan indeks HNSW).
  - **Pelajaran Praktis:** Kita tidak bisa hanya menekan tombol *autogenerate*. Kita harus memecah migrasi. Pengaktifan ekstensi tingkat server (`op.execute("CREATE EXTENSION IF NOT EXISTS vector")`) harus diinjeksikan secara **manual** pada iterasi migrasi ke-0 sebelum tabel-tabel produk yang bergantung padanya di-generate.

---

## 5. Metodologi Pendekatan Masalah
Mengandalkan metode **Socratic Troubleshooting**, alih-alih langsung memecahkan *error* (seperti *command not found* pada `uv` atau *missing dialect* pada SQLAlchemy). Kita diajarkan untuk:
1. Melakukan **RCA (Root Cause Analysis)**.
2. Memahami perilaku sistem operasi, mekanisme koneksi *database*, dan *compiler* sebelum mengetikkan sebaris kode apa pun. 
3. Menyelesaikan masalah di tingkat konsep (arsitektural), lalu mengeksekusinya ke dalam sintaks.
