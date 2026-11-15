# 📁 Dataset Sampel Uji Coba Dokumen Resmi (Preset Dataset)

Direktori ini memuat **7 berkas sampel dokumen uji coba realistis** yang dirancang khusus untuk menguji seluruh fungsionalitas sistem tanda tangan dokumen pasca-kuantum (*ML-DSA / FIPS 204*), pengesahan ambang batas (*threshold $k$-dari-$n$*), mesin analisis forensik, dan mesin ekstraksi **Tesseract OCR**.

---

## 📋 Katalog Berkas Sampel Uji Coba

| No | Nama Berkas | Format | Skenario Penggunaan Nyata | Target Pengujian Sistem |
|:---:|:---|:---:|:---|:---|
| **01** | `01_SK_Rektor_Kurikulum_PQC_2026.docx` | **Microsoft Word (`.docx`)** | Surat Keputusan Rektor tentang Penetapan Kurikulum Kriptografi Pasca-Kuantum & Keamanan Siber. | Parsing naskah dinas, hierarki paragraf, tabel distribusi SKS mata kuliah, dan pembacaan core metadata (*Author*, Tanggal Dibuat). |
| **02** | `02_RAB_Anggaran_BOS_Lab_PQC.xlsx` | **Microsoft Excel (`.xlsx`)** | Rencana Anggaran Biaya (RAB) Multi-Sheet Pengadaan Hardware Server HSM & Laboratorium Kuantum. | Multi-sheet navigation (`RAB_Pengadaan_PQC` & `Kuorum_Verifikator`), formula hitung anggaran, kalkulasi total Rp 245.000.000. |
| **03** | `03_BAST_Pengadaan_Server_PQC.pdf` | **Digital Native PDF (`.pdf`)** | Berita Acara Serah Terima (BAST) Pekerjaan antara Pejabat Pembuat Komitmen (PPK) & Rekanan Penyedia. | Ekstraksi teks digital native PDF, pemeriksaan enkripsi, tabel status uji kripto, kesiapan kontainer CMS ASN.1. |
| **04** | `04_Surat_Izin_Operasional_Scan.pdf` | **Scanned PDF (`.pdf`)** | Dokumen Surat Izin Operasional Lembaga Negara Berbasis Citra Pindai Kertas (Non-searchable). | **Uji Otomatis Mesin OCR**: Merender halaman gambar dan mengekstraksi teks naskah izin serta stempel cap basah LLDIKTI. |
| **05** | `05_Laporan_Keuangan_Pengadaan.csv` | **Tabular Data (`.csv`)** | Rekam Jejak Transaksi Rekening Koran & Realisasi Kas Keuangan Pengadaan Teknologi Kuantum. | Parsing delimitasi CSV, deteksi encoding, tabel data transaksi keuangan (*debit*, *kredit*, *saldo*). |
| **06** | `06_Surat_Edaran_Sosialisasi_Legacy.rtf` | **Word RTF (`.rtf`)** | Surat Edaran Resmi Kementerian Pendidikan Tinggi format Rich Text kompatibel Word versi lama. | Ekstraksi format Word berbasis RTF, pembersihan kode kontrol, pengikatan digest biner `THRESHDOC-v0`. |
| **07** | `07_Ijazah_Sertifikat_Fisik_Scan.png` | **Citra Pindai Dokumen (`.png`)** | Foto / Scan Sertifikat Kelulusan Uji Forensik beresolusi tinggi dengan stempel cap fisik. | **Uji Langsung Citra OCR**: Ekstraksi teks dari citra foto murni menggunakan mesin Tesseract OCR 5.5 multi-bahasa. |

---

## 🚀 Cara Menggunakan di Dashboard Streamlit

1. Jalankan aplikasi web: `streamlit run app.py` (atau akses tautan Streamlit Cloud Anda).
2. Pada mode masukan dokumen, pilih **"Unggah Berkas"**.
3. Di dropdown **"⚡ Muat Cepat Contoh Dokumen Uji Coba (Preset Dataset)"**, pilih salah satu berkas di atas.
4. Sistem akan otomatis memuat biner dokumen, menampilkan pratinjau analisis forensik, menjalankan kalkulasi hash **SHA3-256**, dan mengaktifkan mesin **Tesseract OCR** (untuk dokumen scan).
5. Anda dapat langsung menguji pengesahan kuorum $k$-dari-$n$, menjalankan **AI Auditor (Groq LPU)**, serta mengunduh **Sertifikat Pengesahan PDF Resmi**.

