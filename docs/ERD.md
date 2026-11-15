# Entity Relationship Diagram (ERD)
## Sistem Tanda Tangan Dokumen Threshold Pasca-Kuantum (ML-DSA FIPS 204)

Dokumen ini memodelkan skema basis data relasional untuk sistem pengelolaan alur kerja penandatanganan dokumen institusi berbasis ambang batas ($k$-dari-$n$) tahan kuantum.

---

### Diagram ERD (Mermaid)

```mermaid
erDiagram
    INSTITUTION ||--o{ SIGNING_GROUP : "memiliki"
    INSTITUTION ||--o{ USER : "menaungi"
    USER ||--o{ SIGNER_SHARE : "memegang"
    SIGNING_GROUP ||--o{ SIGNER_SHARE : "terdiri_atas"
    SIGNING_GROUP ||--o{ DOCUMENT : "menetapkan_kebijakan"
    
    DOCUMENT ||--one-to-many SIGNING_SESSION : "memulai"
    SIGNING_SESSION ||--o{ PARTIAL_SIGNATURE : "mengumpulkan"
    USER ||--o{ PARTIAL_SIGNATURE : "menghasilkan"
    SIGNING_SESSION ||--|| FINAL_SIGNATURE : "menghasilkan"
    DOCUMENT ||--o| FINAL_SIGNATURE : "disahkan_oleh"
    
    DOCUMENT ||--o{ AUDIT_LOG : "mencatat_riwayat"
    USER ||--o{ AUDIT_LOG : "melakukan_aksi"

    INSTITUTION {
        string institution_id PK "UUID"
        string name "Nama Institusi / Sekolah"
        string code "Kode Unik Institusi"
        string address "Alamat"
        datetime created_at "Waktu Registrasi"
    }

    USER {
        string user_id PK "UUID"
        string institution_id FK "Referensi Institusi"
        string nip_nik "Nomor Induk Pegawai"
        string full_name "Nama Lengkap"
        string email "Email Resmi"
        string role "Peran (kepsek, wakasek, tu, bendahara, komite)"
        string status "ACTIVE, INACTIVE, REVOKED"
        datetime created_at "Waktu Dibuat"
    }

    SIGNING_GROUP {
        string group_id PK "UUID"
        string institution_id FK "Referensi Institusi"
        string policy_name "Nama Kebijakan (misal: Pengesahan SK Rektor)"
        int threshold_k "Nilai Ambang Minimal (k)"
        int total_n "Jumlah Total Penanda Tangan (n)"
        string algorithm "ML-DSA-65 / Dilithium3"
        blob group_public_key "Kunci Publik Kolektif (bytes)"
        string status "ACTIVE, ARCHIVED"
        datetime created_at "Waktu Dibuat"
    }

    SIGNER_SHARE {
        string share_id PK "UUID"
        string group_id FK "Referensi Grup"
        string user_id FK "Referensi Pengguna"
        int share_index "Indeks Peserta (1..n)"
        blob public_key_share "Kunci Publik Parsial Penanda Tangan"
        string status "ACTIVE, REVOKED, EXPIRED"
        datetime assigned_at "Waktu Pembagian Share"
    }

    DOCUMENT {
        string doc_id PK "ID Dokumen / Nomor Surat (SK-123)"
        string institution_id FK "Referensi Institusi"
        string group_id FK "Referensi Kebijakan Grup"
        string title "Judul Dokumen"
        string doc_type "SURAT_KEPUTUSAN, IJAZAH, KONTRAK"
        blob file_sha3_256 "Hash Isi Dokumen (32 bytes)"
        string storage_path "Lokasi Berkas PDF / Asli"
        string status "DRAFT, PENDING_APPROVAL, SIGNED, REJECTED"
        datetime uploaded_at "Waktu Unggah"
    }

    SIGNING_SESSION {
        string session_id PK "UUID"
        string doc_id FK "Referensi Dokumen"
        blob bound_digest "Digest THRESHDOC-v0 (H(doc, id, k, signers))"
        string session_status "OPEN, COLLECTING, COMPLETED, EXPIRED, ABORTED"
        datetime started_at "Waktu Sesi Dimulai"
        datetime expires_at "Batas Waktu Persetujuan"
    }

    PARTIAL_SIGNATURE {
        string partial_id PK "UUID"
        string session_id FK "Referensi Sesi"
        string user_id FK "Referensi Penanda Tangan"
        blob partial_sig_bytes "Tanda Tangan Parsial ML-DSA / Ed25519"
        boolean is_valid "Hasil Validasi Koordinator"
        datetime signed_at "Waktu Penandatanganan"
    }

    FINAL_SIGNATURE {
        string sig_id PK "UUID"
        string session_id FK "Referensi Sesi"
        string doc_id FK "Referensi Dokumen"
        blob combined_sig_bytes "Tanda Tangan Final FIPS 204"
        string container_format "CMS_SIGNED_DATA, PAdES_ATTACHED, RAW"
        blob cms_der_package "Paket Kontainer ASN.1 DER"
        boolean is_verified "Status Verifikasi Akhir"
        datetime completed_at "Waktu Selesai Digabungkan"
    }

    AUDIT_LOG {
        string log_id PK "UUID"
        string doc_id FK "Referensi Dokumen (opsional)"
        string user_id FK "Aktor / Pengguna"
        string action "DOCUMENT_CREATED, PARTIAL_SIGNED, MERGED, TAMPER_ATTEMPT"
        string ip_address "Alamat IP"
        string user_agent "Informasi Perangkat"
        blob record_hash "Hash Integritas Log Rantai (Audit Trail)"
        datetime timestamp "Waktu Kejadian"
    }
```

---

### Penjelasan Entitas Kunci

1. **`INSTITUTION` & `USER`**: Memodelkan pihak sekolah/universitas dan pejabat berwenang (Kepala Sekolah, Wakil, Tata Usaha, Bendahara, Komite).
2. **`SIGNING_GROUP`**: Kebijakan kuorum $k$-dari-$n$. Menyimpan ambang batas $k$, jumlah penanda tangan $n$, dan algoritma dasar (`ML-DSA-65`).
3. **`SIGNER_SHARE`**: Mengaitkan pejabat penanda tangan dengan share kunci masing-masing. Kunci privat tidak pernah disimpan di database pusat, melainkan berada di modul aman masing-masing penanda tangan.
4. **`DOCUMENT` & `SIGNING_SESSION`**: Menjamin pengikatan dokumen melalui *domain separation* `THRESHDOC-v0` pada tingkat digest ($H(\text{dokumen}, \text{ID}, k, \text{daftar})$).
5. **`PARTIAL_SIGNATURE` & `FINAL_SIGNATURE`**: Menyimpan tanda tangan parsial yang dikumpulkan koordinator hingga mencapai kuorum $\ge k$, lalu digabungkan menjadi tanda tangan standar FIPS 204 yang kompatibel dengan verifier biasa.
6. **`AUDIT_LOG`**: Memenuhi kebutuhan non-fungsional tata kelola institusi (mencatat siapa menyetujui dokumen apa, kapan, dan dari perangkat mana, dilengkapi hashing berantai anti-manipulasi).

