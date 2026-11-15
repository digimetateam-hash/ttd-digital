# Material Design 3 (M3) System Specification (DESIGN_MATERIAL3.md)
## Dashboard Tanda Tangan Dokumen Threshold Pasca-Kuantum (ML-DSA FIPS 204)

Dokumen ini mendefinisikan panduan antarmuka pengguna (UI) dan pengalaman pengguna (UX) berbasis **Google Material Design 3 (Material You)** untuk dashboard pengesahan dokumen institusi pasca-kuantum.

---

## 1. Fondasi Desain & Token Warna (M3 Color Tokens)

Sistem warna menggunakan palet tonal dinamis M3 yang mencerminkan otoritas institusional, transparansi tata kelola, dan keamanan kriptografis tingkat tinggi.

### 1.1 Palet Warna Utama (Light & Dark Theme)

| Token M3 | Nilai Hex (Light) | Nilai Hex (Dark) | Peran UI / Semantik |
|:---|:---|:---|:---|
| **`primary`** | `#1A56DB` (Quantum Blue) | `#93C5FD` (Light Blue) | Elemen aksi utama, tombol penandatanganan kolektif, tab aktif. |
| **`on-primary`** | `#FFFFFF` | `#0F2F6B` | Teks dan ikon di atas warna primer. |
| **`primary-container`** | `#E1E8F8` | `#1E3A8A` | Kartu status digest aktif, header sesi aktif. |
| **`on-primary-container`** | `#0C2556` | `#DBEAFE` | Teks di atas primary container. |
| **`secondary`** | `#0D9488` (PQC Teal) | `#5EEAD4` (Mint Teal) | Indikator keamanan kuantum, status validasi verifier. |
| **`secondary-container`** | `#CCFBF1` | `#115E59` | Badge penanda tangan berwenang yang menyetujui. |
| **`tertiary`** | `#D97706` (Institutional Gold)| `#FCD34D` (Warm Gold) | Indikator peringatan kuorum, mode fallback klasik. |
| **`error`** | `#DC2626` (Crimson) | `#F87171` (Light Red) | Tanda tangan ditolak, manipulasi dokumen terdeteksi. |
| **`error-container`** | `#FEE2E2` | `#7F1D1D` | Banner peringatan percobaan tampering (RQ3). |
| **`surface`** | `#F8FAFC` (Slate 50) | `#0F172A` (Slate 900) | Latar belakang halaman aplikasi. |
| **`surface-container`** | `#FFFFFF` (White) | `#1E293B` (Slate 800) | Kontainer kartu penanda tangan, tabel benchmark. |
| **`outline`** | `#CBD5E1` (Slate 300) | `#475569` (Slate 600) | Garis batas kartu dokumen, border input form. |

---

## 2. Sistem Tipografi (M3 Typography Scale)

Tipografi menggunakan kombinasi **Plus Jakarta Sans** / **Inter** untuk teks antarmuka dan **Fira Code** / **JetBrains Mono** untuk hash kriptografis dan digest heksadesimal.

```
Display Large    - 57sp / Line Height 64sp (Header Judul Riset Utama)
Headline Medium  - 28sp / Line Height 36sp (Judul Tab & Bagian Utama)
Title Medium     - 16sp / Line Height 24sp (Judul Kartu Dokumen & Penanda Tangan)
Body Large       - 16sp / Line Height 24sp (Isi Naskah Dokumen & Keterangan)
Body Small       - 12sp / Line Height 16sp (Keterangan Metadata & Timestamp)
Label Large      - 14sp / Line Height 20sp (Label Tombol Aksi & Badge Status)
Code / Mono      - 13sp / Line Height 18sp (Digest SHA3-256, Hash & Signature Bytes)
```

---

## 3. Sistem Elevasi & Bentuk Sudut (M3 Elevation & Shapes)

Sesuai standar Material 3, sistem tidak lagi mengandalkan bayangan tajam (*drop shadows*), melainkan **elevasi tonal** (*surface tint*) dengan variasi sudut lengkung (*corner radius*):

* **Surface Tonal Elevation:**
  * **Level 0 (Flat):** Latar belakang halaman aplikasi (`surface`).
  * **Level 1 (Card Default):** Kartu dokumen dan kebijakan ambang batas (`surface-container-low` + `outline` 1px).
  * **Level 2 (Active/Hover):** Kartu penanda tangan saat dipilih atau sedang memproses tanda tangan.
  * **Level 3 (Modal/Dialog):** Dialog rincian ASN.1 CMS dan notifikasi hasil uji negatif.
* **Shape Scale (Border Radius):**
  * **Full Rounded (`999px`):** Chip status penanda tangan, badge FIPS 204, dan tombol pill.
  * **Large (`16px`):** Kartu utama dokumen, panel pengikatan digest, dan grafik benchmark.
  * **Medium (`12px`):** Kotak input teks dokumen, kolom nomor surat, dan kontainer metrik.
  * **Small (`8px`):** Tombol aksi sekunder, kotak kode digest heksadesimal.

---

## 4. Pola Komponen Khusus Dashboard (Component Specs)

### 4.1 Kartu Penanda Tangan (Signer Adaptive Card)
* **Status Belum Menyetujui:**
  * Background: `surface-container` (Netral).
  * Border: 1px `outline`.
  * Ikon: Avatar inisial peran (`KS`, `WK`, `TU`, `BD`, `KM`).
* **Status Telah Menyetujui (Checked):**
  * Background: `secondary-container` (Teal lembut).
  * Border: 2px `secondary`.
  * Badge: Checkmark hijau dengan timestamp tanda tangan parsial.

### 4.2 Banner Status Pengesahan (Verdict Banner)
* **Dokumen Sah ($\ge k$):**
  * Kontainer M3 `Success` dengan ikon perisai pasca-kuantum 🛡️.
  * Headline: *"DOKUMEN SAH (FIPS 204 VALID)"*.
  * Body: Menampilkan jumlah kuorum (misal: "3 dari 5 pihak menyetujui") dan ukuran tanda tangan konstan ($O(1)$ = 3309 Bytes).
* **Dokumen Ditolak ($< k$ atau Tampered):**
  * Kontainer M3 `Error` dengan ikon silang peringatan ⚠️.
  * Headline: *"DOKUMEN DITOLAK (INVALID)"*.
  * Body: Rincian pelanggaran aturan (kuorum kurang, konten diubah, atau replay ID).

### 4.3 Visualisasi Metrik & Benchmark (M3 Metric Tile)
* Setiap metrik (Ukuran Bytes, Waktu Sign, Waktu Verify) ditampilkan dalam kontainer lengkung 12px dengan label kontras tinggi dan nilai numerik menonjol (Headline Small).

---

## 5. Konfigurasi Streamlit Theme (`.streamlit/config.toml`)

Untuk menerapkan token Material 3 secara otomatis pada runtime Streamlit Cloud:

```toml
[theme]
primaryColor = "#1A56DB"
backgroundColor = "#F8FAFC"
secondaryBackgroundColor = "#EDF2F7"
textColor = "#0F172A"
font = "sans serif"
```

---

## 6. Prinsip Aksesibilitas (WCAG 2.1 AA)

1. **Rasio Kontras Warna:** Semua teks pada tombol dan kartu memiliki rasio kontras minimal $4.5:1$ terhadap warna latar.
2. **Indikator Non-Warna:** Status sah/ditolak tidak hanya bergantung pada warna hijau/merah, tetapi wajib disertai ikon tegas (✅ / ❌) dan teks deskriptif eksplisit.
3. **Responsivitas:** Tata letak kolom multi-penanda tangan adaptif: 5 kolom pada layar desktop/tablet, dan beralih otomatis ke *single-column card list* pada layar ponsel pintar.
