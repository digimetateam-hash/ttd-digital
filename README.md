<p align="center">
  <img src="assets/logo-3d.png" alt="TTD-Digital 3D Post-Quantum Threshold Signing Logo" width="200" style="max-width: 200px; border-radius: 16px; box-shadow: 0 8px 24px rgba(0, 0, 0, 0.35);" />
</p>

<h1 align="center">Threshold Post-Quantum Document Signing (ML-DSA / FIPS 204)</h1>

<p align="center">
  <em>Sistem Tanda Tangan Dokumen (TTD) Resmi Institusi Berbasis Ambang Batas (k-dari-n) Tahan Komputasi Kuantum</em>
</p>

<p align="center">
  <a href="https://github.com/digimetateam-hash/ttd-digital"><img src="https://img.shields.io/badge/Standard-NIST%20FIPS%20204%20(ML--DSA--65)-0284c7?style=for-the-badge&logo=shield" alt="FIPS 204"></a>
  <a href="https://github.com/digimetateam-hash/ttd-digital"><img src="https://img.shields.io/badge/Quorum-k--dari--n%20Threshold-0d9488?style=for-the-badge" alt="Threshold Quorum"></a>
  <a href="https://github.com/digimetateam-hash/ttd-digital"><img src="https://img.shields.io/badge/UI%20Design-Material%20Design%203-1a56db?style=for-the-badge" alt="Material Design 3"></a>
  <a href="https://github.com/digimetateam-hash/ttd-digital"><img src="https://img.shields.io/badge/Test%20Suite-15%2F15%20Passed%20(100%25)-10b981?style=for-the-badge" alt="Tests Passed"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-Apache%202.0-blue.svg?style=for-the-badge" alt="Apache 2.0 License"></a>
  <a href="https://github.com/digimetateam-hash/ttd-digital"><img src="https://img.shields.io/badge/Cloud-Streamlit%20Ready-ff4b4b?style=for-the-badge&logo=streamlit" alt="Streamlit Cloud"></a>
</p>

---

> **Judul Riset:** *Threshold Post-Quantum Document Signing for Institutional Workflows: Design, Integration, and Empirical Evaluation*  
> **Algoritma Dasar:** ML-DSA (FIPS 204 / Dilithium) dengan fallback Ed25519.

Aplikasi web interaktif berbasis **Streamlit** untuk mendemonstrasikan, menguji, dan mengevaluasi penandatanganan dokumen resmi secara kolektif dengan skema threshold ($k$-dari-$n$) tahan komputasi kuantum.

---

## 🎯 Target Pengguna & Penerima Manfaat (Untuk Siapa?)

Proyek ini dirancang secara khusus untuk 4 kelompok pemangku kepentingan utama:

1. **🏫 Institusi Pendidikan (Sekolah, Madrasah, Universitas, & Yayasan):**
   * **Pengguna:** Kepala Sekolah, Wakil Kepala Sekolah, Kepala Tata Usaha, Bendahara, dan Komite Sekolah.
   * **Manfaat:** Mencegah otorisasi sepihak atau pemalsuan dokumen penting (Surat Keputusan Kelulusan, Ijazah Digital, RAPBS/RAB, dan Laporan Pertanggungjawaban Dana BOS). Dokumen hanya sah bila disetujui kuorum bersama.
2. **🏛️ Instansi Pemerintah & Sektor Publik (Birokrasi / SPBE):**
   * **Pengguna:** Pejabat Pembuat Komitmen (PPK), Kuasa Pengguna Anggaran (KPA), Tim Pengadaan Barang/Jasa (LPSE), dan Inspektorat Daerah.
   * **Manfaat:** Menghilangkan *Single Point of Failure* (titik kegagalan tunggal) pada penandatanganan kontrak proyek negara bernilai miliaran rupiah dan Berita Acara Serah Terima (BAST).
3. **💼 Korporasi, Perbankan, & Lembaga Hukum (Enterprise & Fintech):**
   * **Pengguna:** Dewan Direksi (*Board of Directors*), Dewan Komisaris, Tim *Treasury*, dan Notaris.
   * **Manfaat:** Pengesahan Perjanjian Kerjasama (PKS) dan otorisasi pencairan dana multi-pihak (*multi-party wire approval*) yang tahan dari ancaman pemecahan kunci di masa depan.
4. **🔬 Peneliti, Akademisi, & Mahasiswa Pascasarjana (Riset & Publikasi):**
   * **Pengguna:** Peneliti bidang Keamanan Siber, Kriptografi Terapan, dan Informatika Forensik.
   * **Manfaat:** Menyediakan artefak ilmiah lengkap yang dapat direplikasi (*reproducible research*), menjawab 4 Pertanyaan Riset (RQ1–RQ4), dilengkapi dataset benchmark 30 repetisi (Median & IQR), serta suite uji model ancaman otomatis.

---

## ⚠️ 5 Isu Kritis & Masalah Nyata yang Diselesaikan

| No | Isu Kritis (Problem Statement) | Penjelasan Masalah Nyata di Lapangan | Solusi Kriptografis Proyek Ini |
|:---:|:---|:---|:---|
| **1** | **Ancaman Komputer Kuantum (*Harvest Now, Decrypt Later*)** | Dokumen resmi (Ijazah, SK, Sertifikat) harus sah puluhan tahun. Kriptografi saat ini (RSA / ECDSA) dapat dipecahkan oleh komputer kuantum di masa depan menggunakan Algoritma Shor. | Migrasi ke standar pasca-kuantum resmi **NIST FIPS 204 (ML-DSA-65)** berbasis kisi (*lattice-based cryptography*). |
| **2** | **Titik Kegagalan Tunggal & Otorisasi Sepihak (*Key Compromise*)** | Pada sistem biasa, satu orang memegang kunci privat utuh. Jika token USB/laptop pejabat dicuri atau disalahgunakan, dokumen palsu dapat disahkan sendirian. | Menerapkan **Threshold Cryptography ($k$-dari-$n$)** tanpa *key escrow*. Kunci dipecah menjadi share lokal independen; tidak ada 1 pihak pun yang memegang kunci utuh. |
| **3** | **Pembengkakan Ukuran Berkas Multi-Pihak (*Multisig Size Bloat / RQ1*)** | Jika tanda tangan multi-pihak dikumpulkan berderet (*multisig biasa*), ukuran file membengkak secara linear $O(k)$ (>16.5 KB untuk 5 penanda tangan), membebani jaringan sekolah/kantor. | Skema **Threshold sejati** memadatkan kuorum menjadi **satu tanda tangan tunggal berukuran konstan $O(1) = 3.309\text{ Bytes}$** (hemat ukuran hingga 80%). |
| **4** | **Pemalsuan Alur & Replay Attack (*Serangan Pemutaran Ulang / RQ3*)** | Tanda tangan sah dari surat edaran biasa rawan diputar ulang (*replay*) penyerang ke dokumen anggaran (RAB), atau daftar nama pejabat diganti pihak lain. | Lapisan pengikat **`THRESHDOC-v0`** (SHA3-256) mengikat mutlak: isi biner berkas (Word/Excel/PDF), nomor ID surat, ambang $k$, dan identitas seluruh penanda tangan. |
| **5** | **Ketiadaan Dukungan Asli PDF/PAdES Terhadap OID Baru (*Interoperabilitas / RQ2*)** | Pembaca PDF umum (Adobe Acrobat, PDF.js, pyHanko) belum mengenali OID resmi ML-DSA FIPS 204 secara native, sehingga menandai dokumen sebagai *unrecognized format*. | Memetakan temuan negatif tersebut secara jujur dan merumuskan solusi **Hybrid Co-Signature** (kontainer ASN.1 CMS RFC 5652 dengan tanda tangan visual ganda). |

---

## Fitur Utama

1. **📁 Dukungan Lengkap Multi-Format Dokumen & Mesin OCR Forensik:**
   - 📝 **Semua Varian Dokumen Word:** `.docx`, `.doc` (Legacy Word 97-2003 OLE2), `.docm`, `.dotx`, `.dotm`, `.rtf` (Rich Text), dan `.odt` (OpenDocument Text).
   - 📊 **Semua Varian Dokumen Excel / Tabel:** `.xlsx`, `.xls` (Legacy Excel 97-2003 BIFF8), `.xlsm`, `.xltx`, `.xltm`, `.csv`, `.tsv`, dan `.ods` (OpenDocument Spreadsheet).
   - 📑 **Semua Varian PDF & Deteksi Hasil Scan:** Dokumen PDF berbasis teks digital, PDF terenkripsi/berproteksi, dan PDF berbasis citra grafis (*scanned*).
   - 🖼️ **Citra Dokumen Pindai (Scan & Foto):** `.png`, `.jpg`, `.jpeg`, `.tiff`, `.bmp`, `.webp`.
   - 🔍 **Mesin Ekstraksi Tesseract OCR Terintegrasi:** Dilengkapi deteksi otomatis PDF hasil scan dan sakelar paksa OCR (*deep OCR analysis*) dengan dukungan multi-bahasa Indonesia & Inggris (`ind+eng`).
2. **✍️ Alur Penandatanganan Kolektif ($k$-dari-$n$):**
   - Mendukung penandatanganan bersama tanpa satu pihak pun memegang kunci utuh.
   - Pengikatan kriptografis (*domain-separated digest* `THRESHDOC-v0`) yang mengikat biner dokumen (Word/Excel/PDF), ID unik dokumen, nilai ambang $k$, dan identitas seluruh penanda tangan.
3. **🛡️ Uji Negatif & Verifikasi Model Ancaman (RQ3):**
   - Uji otomatis penolakan manipulasi isi dokumen (*tampering* 1 huruf/angka di Word/Excel membatalkan tanda tangan).
   - Penolakan kuorum di bawah ambang ($< k$).
   - Pencegahan pemutaran ulang tanda tangan (*replay attack*) ke dokumen/ID lain.
   - Pencegahan penggantian daftar penanda tangan (*policy substitution*).
4. **📊 Evaluasi & Benchmark Kinerja Empiris (RQ1 & RQ4):**
   - Pengukuran latensi penandatanganan dan verifikasi (median & IQR).
   - Analisis perbandingan ukuran tanda tangan antara *Multisig Baseline* ($O(k)$) dan *True Threshold ML-DSA* ($O(1)$).
   - Ekspor laporan benchmark dan jejak audit langsung ke format **Excel (`.xlsx`)**.
5. **📦 Evaluasi Kontainer CMS & Kompatibilitas Dokumen (RQ2):**
   - Pemeriksaan kontainer ASN.1 CMS `SignedData` dengan OID `ML-DSA-65` (`2.16.840.1.101.3.4.3.18`).
   - Analisis kesiapan format PDF/PAdES dan pendekatan *hybrid co-signature*.
6. **🤖 Asisten AI Anti-Halusinasi (Strict Grounding):**
   - Didukung Groq Cloud LPU (`temperature: 0.0`) untuk audit faktual naskah SK Word, pendeteksian anomali sel Excel, dan Q&A berbasis kutipan langsung (*verbatim citation*).
7. **🎖️ Penerbitan Otomatis Sertifikat Pengesahan PDF (Certificate of Authenticity):**
   - Jika dan hanya jika verifikasi kuorum berstatus **SAH (Valid)**, sistem secara otomatis menerbitkan **Sertifikat Pengesahan Dokumen Digital (.pdf)** resmi yang memuat nomor UUID sertifikat, stempel waktu, bukti hash SHA3-256, kuorum pejabat, dan jaminan FIPS 204. Jika kuorum gagal atau dokumen diubah, sertifikat **dilarang terbit**.

---

## Daftar Istilah & Singkatan (Glossary)

Untuk memudahkan pemahaman para peneliti, penguji, dan pengembang, berikut adalah daftar istilah dan singkatan yang digunakan dalam repositori ini:

| Istilah / Singkatan | Kepanjangan / Nama Resmi | Penjelasan Singkat dalam Sistem Ini |
|:---|:---|:---|
| **TTD** | **Tanda Tangan Dokumen** / Digital | Proses pengesahan berkas resmi institusi secara elektronik oleh para pejabat berwenang. |
| **PQ / PQC** | **Post-Quantum Cryptography** | Kriptografi pasca-kuantum yang dirancang tahan terhadap serangan komputer kuantum (algoritma Shor). |
| **ML-DSA (FIPS 204)**| **Module-Lattice-Based Digital Signature Algorithm** | Standar resmi tanda tangan digital pasca-kuantum NIST (sebelumnya dikenal sebagai *CRYSTALS-Dilithium*). |
| **$k$-dari-$n$** | **Threshold Quorum ($k$-of-$n$)** | Skema pembagian otorisasi: dokumen baru sah bila minimal $k$ pihak berwenang dari total $n$ pihak menyetujui. |
| **RQ1 – RQ4** | **Research Questions 1 s.d. 4** | Empat pertanyaan riset empiris yang dijawab tuntas melalui eksperimen benchmark dan uji model ancaman. |
| **CMS** | **Cryptographic Message Syntax** (RFC 5652) | Format kontainer standar ASN.1 (`pkcs7-signedData`) untuk membungkus data bertanda tangan dan sertifikat. |
| **PAdES** | **PDF Advanced Electronic Signatures** | Profil standar tanda tangan dokumen PDF yang diakui secara legal di tingkat internasional (ETSI EN 319 142). |
| **SK, RAB, RAPBS** | **Surat Keputusan, Rencana Anggaran Biaya, RAPB Sekolah** | Jenis dokumen resmi institusi sekolah/pemerintah yang didukung penuh (Word `.docx` dan Excel `.xlsx`). |
| **Non-Escrow** | **No Trusted Third-Party Key Custody** | Prinsip keamanan di mana kunci privat utuh **tidak pernah** dibuat atau disimpan di server mana pun. |

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
├── assets/
│   ├── logo-3d.png                # Visual Render 3D Hero Banner Landing Page
│   └── logo-3d.svg                # Vektor 3D Isometric Logo (Lattice & Shield)
├── docs/
│   ├── ERD.md                     # Entity Relationship Diagram & Relasi Data
│   ├── SCHEMA.md                  # Spesifikasi Skema Database, DDL SQL & Batasan Kripto
│   ├── RULES.md                   # Aturan Bisnis, Kriptografi & Tata Kelola Forensik
│   ├── DESIGN_MATERIAL3.md        # Panduan Desain Material Design 3 (M3) & UI/UX
│   ├── QUALITY_ASSESSMENT.md      # Laporan Evaluasi Kualitas Perangkat Lunak & RQ Matrix
│   └── EVALUATION_REPORT.md       # Laporan Hasil Uji Evaluasi Empiris Lengkap (30 Runs)
├── samples/                       # Dataset Uji Coba Multi-Format & Citra OCR Siap Pakai
│   ├── 01_SK_Rektor_Kurikulum_PQC_2026.docx
│   ├── 02_RAB_Anggaran_BOS_Lab_PQC.xlsx
│   ├── 03_BAST_Pengadaan_Server_PQC.pdf
│   ├── 04_Surat_Izin_Operasional_Scan.pdf
│   ├── 05_Laporan_Keuangan_Pengadaan.csv
│   ├── 06_Surat_Edaran_Sosialisasi_Legacy.rtf
│   ├── 07_Ijazah_Sertifikat_Fisik_Scan.png
│   └── README.md                  # Katalog & Panduan Lengkap Dataset Sampel
├── scripts/
│   ├── evaluate_empirical.py      # Skrip Eksekusi Benchmark & Simulasi Jaringan RQ1-RQ4
│   └── generate_sample_dataset.py # Skrip Pembangkit Berkas Sampel Uji Coba Multi-Format
├── reports/
│   ├── benchmark_rq1_30runs.csv   # Data mentah benchmark 30 runs per konfigurasi
│   └── simulation_rq4_network.csv # Data mentah simulasi jaringan & signer offline
├── tests/
│   ├── test_threshold_docsign.py  # Suite Uji Otomatis & Uji Negatif Model Ancaman (RQ3)
│   └── test_doc_analyzer.py       # Suite Uji Multi-Format Word, Excel, PDF & Mesin OCR
├── pytest.ini                     # Konfigurasi pengujian pytest
├── app.py                         # Aplikasi utama dashboard Streamlit
├── doc_analyzer.py                # Mesin analisis forensik berkas multi-format & Tesseract OCR
├── cert_generator.py              # Generator Sertifikat Keaslian Dokumen Resmi (PDF)
├── ai_auditor.py                  # Auditor Integritas Kripto AI (Groq LLM)
├── threshold_docsign.py           # Modul logika kriptografi & baseline evaluasi
├── PRD_Threshold-PQ-Signature.md  # Dokumen spesifikasi kebutuhan riset & referensi
├── requirements.txt               # Daftar pustaka Python untuk Streamlit Cloud
├── packages.txt                   # Paket sistem OS Debian untuk Streamlit Cloud (Tesseract OCR)
├── LICENSE                        # Lisensi Open Source (Apache License 2.0)
├── .gitignore
└── README.md                      # Dokumentasi proyek
```

---

## 📄 Lisensi (License)

Proyek ini didistribusikan di bawah lisensi terbuka **[Apache License 2.0](LICENSE)**.

### Mengapa Apache License 2.0?
1. **Perlindungan Hak Paten (*Patent Grant*):** Memberikan perlindungan eksplisit terhadap klaim atau tuntutan paten terkait implementasi algoritma lattice-based cryptography dan skema threshold post-quantum.
2. **Komersial & Institusional:** Memungkinkan adopsi bebas oleh instansi pemerintah, institusi pendidikan, dan korporasi perbankan tanpa biaya lisensi (*royalty-free*).
3. **Penelitian & Replikasi Terbuka:** Menjamin kode dan artefak eksperimen dapat direplikasi, dimodifikasi, dan diaudit secara independen oleh komunitas kriptografi dan keamanan siber global.

*Copyright (c) 2026 DigiMeta Team & TTD-Digital Contributors.*

