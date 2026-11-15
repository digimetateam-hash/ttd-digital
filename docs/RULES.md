# System Rules & Cryptographic Governance (RULES.md)
## Sistem Tanda Tangan Dokumen Threshold Pasca-Kuantum (ML-DSA FIPS 204)

Dokumen ini menetapkan aturan bisnis, kebijakan kriptografi, batasan integritas alur kerja, dan tata kelola sistem untuk pengesahan dokumen resmi institusi berbasis ambang batas ($k$-dari-$n$).

---

## 1. Aturan Bisnis & Kebijakan Kuorum (Business Rules - BR)

* **BR-01 (Syarat Kuorum $k$-dari-$n$):**
  * Nilai ambang minimal $k$ harus memenuhi $1 \le k \le n$.
  * Dokumen dinyatakan **SAH** jika dan hanya jika terdapat minimal $k$ tanda tangan parsial yang valid dari daftar $n$ penanda tangan yang sah.
  * Jika jumlah penanda tangan yang menyetujui $< k$, sistem **WAJIB MENOLAK** pengesahan dan dokumen berstatus `PENDING_APPROVAL` atau `REJECTED`.
* **BR-02 (Keunikan Penanda Tangan / Anti-Duplikasi):**
  * Setiap penanda tangan hanya berhak memberikan 1 (satu) tanda tangan parsial per sesi penandatanganan dokumen.
  * Tanda tangan ganda dari penanda tangan yang sama **TIDAK BOLEH** dihitung sebagai penambah kuorum.
* **BR-03 (Pemisahan Peran & Otoritas):**
  * Peran penanda tangan (Kepala Sekolah, Wakil Kepala Sekolah, Tata Usaha, Bendahara, Komite) memiliki bobot suara setara dalam kuorum kriptografis, namun koordinator hanya berhak memicu penggabungan tanda tangan jika kuorum terpenuhi.
  * Penanda tangan di luar daftar kebijakan grup yang bersangkutan **DITOLAK SECARA OTOMATIS**.
* **BR-04 (Batas Waktu Sesi / Session Timeout):**
  * Sesi penandatanganan memiliki masa aktif (`expires_at`), default 7 hari kalender.
  * Sesi yang melewati batas waktu tanpa mencapai kuorum dinyatakan `EXPIRED`.
* **BR-05 (Imutabilitas Dokumen yang Telah Sah):**
  * Dokumen dengan status `SIGNED` bersifat *read-only* permanen. Modifikasi apa pun setelah pengesahan membatalkan tanda tangan.

---

## 2. Aturan Kriptografi & Keamanan Pasca-Kuantum (Cryptographic Rules - CR)

* **CR-01 (Algoritma Standar FIPS 204):**
  * Algoritma utama wajib menggunakan **ML-DSA-65** (keamanan setara Kategori 3 NIST / AES-192 / SHA3-384).
  * Varian fallback klasik (misal: Ed25519) hanya diizinkan untuk lingkungan uji/komparasi benchmark dan wajib diberi label eksplisit `NON-PQ-FALLBACK`.
* **CR-02 (Prinsip Non-Escrow & Zeroization):**
  * **Kunci privat utuh TIDAK PERNAH direkonstruksi atau disimpan di server.**
  * Masing-masing penanda tangan memegang share kunci privat lokal (`secret_key_share`).
  * Koordinator hanya mengumpulkan tanda tangan parsial (`partial_signatures`) untuk menghasilkan 1 (satu) tanda tangan standar FIPS 204.
* **CR-03 (Pemisahan Domain & Pengikatan Dokumen - Domain Separation):**
  * Setiap digest dokumen wajib dihitung menggunakan SHA3-256 dengan prefix domain `THRESHDOC-v0`:
    $$\text{Digest} = \text{SHA3-256}\Big(\text{"THRESHDOC-v0"} \parallel \text{len}(\text{meta}) \parallel \text{meta} \parallel \text{SHA3-256}(\text{dokumen})\Big)$$
  * Di mana $\text{meta}$ adalah serialisasi JSON kanonikal dari `{"doc_id": ID, "k": k, "signers": [p1, ..., pn]}`.
* **CR-04 (Pencegahan Pemutaran Ulang - Anti-Replay):**
  * Tanda tangan yang sah untuk suatu dokumen dengan `doc_id = A` tidak dapat dipindahkan atau dinyatakan sah untuk dokumen lain dengan `doc_id = B`.
* **CR-05 (Pencegahan Rejection Sampling Abort Loop):**
  * Pada protokol threshold terdistribusi berbasis kisi (lattice MPC), batas maksimum percobaan ulang (*retry limit*) akibat penolakan sampling adalah 10 kali putaran. Jika melebihi batas, sesi dihentikan (*abort*) untuk mencegah kebocoran informasi side-channel.

---

## 3. Aturan Kontainer Dokumen & Verifikasi PDF (Format Rules - FR)

* **FR-01 (Format Kontainer Standar CMS):**
  * Paket tanda tangan final dikemas dalam kontainer ASN.1 CMS `SignedData` (RFC 5652) dengan OID:
    * `2.16.840.1.101.3.4.3.18` (`id-ml-dsa-65`)
    * Digest OID: `shake256` atau `sha3-256`
* **FR-02 (Strategi Kompatibilitas Pembaca PDF / Hybrid Co-Signature):**
  * Mengingat verifier PDF lama (seperti Adobe Acrobat Reader) belum mengenali OID ML-DSA secara native:
    * Sistem menerapkan pendekatan **Hybrid Co-Signature**: kontainer dokumen memuat tanda tangan visual Ed25519/ECDSA untuk verifikasi aplikasi legacy, serta atribut ekstensi pasca-kuantum ML-DSA FIPS 204 untuk validasi jangka panjang (*long-term archival validation*).

---

## 4. Aturan Audit Forensik & Jejak Integritas (Audit Rules - AR)

* **AR-01 (Pencatatan Rantai Log Tak Dapat Dimanipulasi):**
  * Setiap aksi penting (`DOC_CREATED`, `PARTIAL_SIGNED`, `COMBINED`, `TAMPER_ATTEMPT`, `REPLAY_BLOCKED`) dicatat dalam tabel `audit_logs`.
  * Setiap entri log memiliki hash integritas berantai:
    $$\text{record\_hash}_i = \text{SHA3-256}(\text{record\_hash}_{i-1} \parallel \text{log\_id} \parallel \text{action} \parallel \text{timestamp})$$
* **AR-02 (Pencatatan Kegagalan Kuorum & Serangan):**
  * Upaya verifikasi yang gagal karena ketidaksesuaian digest atau modifikasi dokumen wajib dicatat sebagai insiden `TAMPER_ATTEMPT` beserta alamat IP dan identitas perangkat.

---

## 5. Aturan Evaluasi Empiris & Pengujian (Research Rules - RR)

* **RR-01 (Validasi Pengujian Negatif RQ3):**
  * Seluruh rangkaian uji negatif (isi dokumen diubah, ambang kurang dari $k$, duplikasi signer, replay ID lain, penggantian signer) wajib mencapai **tingkat kelulusan 100% (semua manipulasi harus tertolak)** sebelum sistem dinyatakan layak pakai.
* **RR-02 (Metrik Benchmark RQ1 & RQ4):**
  * Pengukuran latensi penandatanganan dan verifikasi wajib diulang minimal 30 kali iterasi, dengan pelaporan statistik berbasis **Median** dan **Interquartile Range (IQR)** untuk menghindari bias outlier latensi jaringan.

