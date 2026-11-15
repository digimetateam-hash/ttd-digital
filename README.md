# Threshold Post-Quantum Document Signing (ML-DSA / FIPS 204)

> **Judul Riset:** *Threshold Post-Quantum Document Signing for Institutional Workflows: Design, Integration, and Empirical Evaluation*  
> **Algoritma Dasar:** ML-DSA (FIPS 204 / Dilithium) dengan fallback Ed25519.

Aplikasi web interaktif berbasis **Streamlit** untuk mendemonstrasikan, menguji, dan mengevaluasi penandatanganan dokumen resmi secara kolektif dengan skema threshold ($k$-dari-$n$) tahan komputasi kuantum.

---

## Fitur Utama

1. **✍️ Alur Penandatanganan Kolektif ($k$-dari-$n$):**
   - Mendukung penandatanganan bersama tanpa satu pihak pun memegang kunci utuh.
   - Pengikatan kriptografis (*domain-separated digest* `THRESHDOC-v0`) yang mengikat konten dokumen, ID unik dokumen, nilai ambang $k$, dan identitas seluruh penanda tangan.
2. **🛡️ Uji Negatif & Verifikasi Model Ancaman (RQ3):**
   - Uji otomatis penolakan manipulasi isi dokumen (*tampering*).
   - Penolakan kuorum di bawah ambang ($< k$).
   - Pencegahan pemutaran ulang tanda tangan (*replay attack*) ke dokumen/ID lain.
   - Pencegahan penggantian daftar penanda tangan (*policy substitution*).
3. **📊 Evaluasi & Benchmark Kinerja Empiris (RQ1 & RQ4):**
   - Pengukuran latensi penandatanganan dan verifikasi (median & IQR).
   - Analisis perbandingan ukuran tanda tangan antara *Multisig Baseline* ($O(k)$) dan *True Threshold ML-DSA* ($O(1)$).
4. **📦 Evaluasi Kontainer CMS & Kompatibilitas Dokumen (RQ2):**
   - Pemeriksaan kontainer ASN.1 CMS `SignedData` dengan OID `ML-DSA-65` (`2.16.840.1.101.3.4.3.18`).
   - Analisis kesiapan format PDF/PAdES dan pendekatan *hybrid co-signature*.

---

## Cara Menjalankan Secara Lokal

```bash
# 1. Clone repositori
git clone https://github.com/digimetateam-hash/ttd-digital.git
cd ttd-digital

# 2. Buat virtual environment & aktifkan
python3 -m venv .venv
source .venv/bin/activate

# 3. Pasang dependensi
pip install -r requirements.txt

# (Opsional) Untuk mengaktifkan algoritma pasca-kuantum ML-DSA FIPS 204:
# macOS: brew install liboqs && pip install liboqs-python
# Linux: pasang liboqs & pip install liboqs-python

# 4. Jalankan aplikasi Streamlit
streamlit run app.py
```

---

## Deploy ke Streamlit Cloud

1. Buka [share.streamlit.io](https://share.streamlit.io/).
2. Hubungkan akun GitHub Anda.
3. Pilih repositori: `digimetateam-hash/ttd-digital`.
4. Pilih cabang: `main`.
5. Tentukan Main file path: `app.py`.
6. Klik **Deploy**!

---

## Struktur Berkas

```
├── docs/
│   ├── ERD.md                     # Entity Relationship Diagram & Relasi Data
│   ├── SCHEMA.md                  # Spesifikasi Skema Database, DDL SQL & Batasan Kripto
│   └── RULES.md                   # Aturan Bisnis, Kriptografi & Tata Kelola Forensik
├── app.py                         # Aplikasi utama dashboard Streamlit
├── threshold_docsign.py           # Modul logika kriptografi & baseline evaluasi
├── PRD_Threshold-PQ-Signature.md  # Dokumen spesifikasi kebutuhan riset & referensi
├── requirements.txt               # Daftar pustaka Python untuk Streamlit Cloud
├── .gitignore
└── README.md                      # Dokumentasi proyek
```
