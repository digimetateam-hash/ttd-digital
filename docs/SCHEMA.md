# Database Schema Specification (SCHEMA.md)
## Sistem Tanda Tangan Dokumen Threshold Pasca-Kuantum (ML-DSA FIPS 204)

Dokumen ini mendefinisikan spesifikasi skema basis data relasional (DDL SQL, kamus data, integritas relasi, dan batasan kriptografi) untuk alur kerja tanda tangan dokumen resmi institusi berbasis ambang batas ($k$-dari-$n$).

---

## 1. DDL SQL (PostgreSQL / SQLite Compatible)

```sql
-- ============================================================
-- 1. INSTITUTIONS
-- ============================================================
CREATE TABLE institutions (
    institution_id      VARCHAR(36) PRIMARY KEY,       -- UUID v4
    name                VARCHAR(255) NOT NULL,          -- Nama Sekolah / Universitas / Lembaga
    code                VARCHAR(50) NOT NULL UNIQUE,    -- Kode institusi (misal: SMAN1-JKT, ITB)
    address             TEXT,
    created_at          TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at          TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- 2. USERS (Pejabat & Penanda Tangan)
-- ============================================================
CREATE TABLE users (
    user_id             VARCHAR(36) PRIMARY KEY,       -- UUID v4
    institution_id      VARCHAR(36) NOT NULL,
    nip_nik             VARCHAR(50) NOT NULL,           -- Nomor Induk Pegawai / NIK
    full_name           VARCHAR(255) NOT NULL,
    email               VARCHAR(150) NOT NULL UNIQUE,
    role                VARCHAR(50) NOT NULL,           -- kepsek, wakasek, tu, bendahara, komite
    status              VARCHAR(20) DEFAULT 'ACTIVE'    -- ACTIVE, INACTIVE, REVOKED
        CHECK (status IN ('ACTIVE', 'INACTIVE', 'REVOKED')),
    created_at          TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_users_institution FOREIGN KEY (institution_id)
        REFERENCES institutions(institution_id) ON DELETE CASCADE
);

CREATE INDEX idx_users_institution ON users(institution_id);
CREATE INDEX idx_users_role ON users(role);

-- ============================================================
-- 3. SIGNING_GROUPS (Kebijakan Ambang / Policy)
-- ============================================================
CREATE TABLE signing_groups (
    group_id            VARCHAR(36) PRIMARY KEY,       -- UUID v4
    institution_id      VARCHAR(36) NOT NULL,
    policy_name         VARCHAR(150) NOT NULL,          -- misal: "Kebijakan SK Kelulusan 3-dari-5"
    threshold_k         INT NOT NULL CHECK (threshold_k >= 1),
    total_n             INT NOT NULL CHECK (total_n >= threshold_k),
    algorithm           VARCHAR(50) DEFAULT 'ML-DSA-65' -- ML-DSA-65, Dilithium3, Ed25519-FALLBACK
        CHECK (algorithm IN ('ML-DSA-44', 'ML-DSA-65', 'ML-DSA-87', 'Dilithium3', 'Ed25519-FALLBACK')),
    group_public_key    BYTEA NOT NULL,                 -- Kunci publik kolektif grup
    status              VARCHAR(20) DEFAULT 'ACTIVE'    -- ACTIVE, ARCHIVED
        CHECK (status IN ('ACTIVE', 'ARCHIVED')),
    created_at          TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_groups_institution FOREIGN KEY (institution_id)
        REFERENCES institutions(institution_id) ON DELETE CASCADE
);

CREATE INDEX idx_signing_groups_inst ON signing_groups(institution_id);

-- ============================================================
-- 4. SIGNER_SHARES (Pemetaan Kunci Parsial ke Penanda Tangan)
-- ============================================================
CREATE TABLE signer_shares (
    share_id            VARCHAR(36) PRIMARY KEY,       -- UUID v4
    group_id            VARCHAR(36) NOT NULL,
    user_id             VARCHAR(36) NOT NULL,
    share_index         INT NOT NULL,                   -- Indeks koordinat share (1..n)
    public_key_share    BYTEA NOT NULL,                 -- Kunci publik share penanda tangan
    status              VARCHAR(20) DEFAULT 'ACTIVE'    -- ACTIVE, REVOKED, EXPIRED
        CHECK (status IN ('ACTIVE', 'REVOKED', 'EXPIRED')),
    assigned_at         TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_shares_group FOREIGN KEY (group_id)
        REFERENCES signing_groups(group_id) ON DELETE CASCADE,
    CONSTRAINT fk_shares_user FOREIGN KEY (user_id)
        REFERENCES users(user_id) ON DELETE CASCADE,
    CONSTRAINT uq_group_share_user UNIQUE (group_id, user_id),
    CONSTRAINT uq_group_share_index UNIQUE (group_id, share_index)
);

CREATE INDEX idx_signer_shares_user ON signer_shares(user_id);

-- ============================================================
-- 5. DOCUMENTS (Dokumen Resmi Institusi)
-- ============================================================
CREATE TABLE documents (
    doc_id              VARCHAR(50) PRIMARY KEY,        -- Nomor Surat / Kode Dokumen (misal: SK-123/2026)
    institution_id      VARCHAR(36) NOT NULL,
    group_id            VARCHAR(36) NOT NULL,
    title               VARCHAR(255) NOT NULL,
    doc_type            VARCHAR(50) NOT NULL            -- SURAT_KEPUTUSAN, IJAZAH, KONTRAK, SURAT_TUGAS
        CHECK (doc_type IN ('SURAT_KEPUTUSAN', 'IJAZAH', 'KONTRAK', 'SURAT_TUGAS', 'OTHER')),
    file_sha3_256       BYTEA NOT NULL,                 -- SHA3-256 dari konten biner dokumen (32 bytes)
    storage_path        VARCHAR(500),                   -- Path berkas dokumen di storage aman
    status              VARCHAR(30) DEFAULT 'DRAFT'     -- DRAFT, PENDING_APPROVAL, SIGNED, REJECTED
        CHECK (status IN ('DRAFT', 'PENDING_APPROVAL', 'SIGNED', 'REJECTED')),
    uploaded_at         TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_documents_inst FOREIGN KEY (institution_id)
        REFERENCES institutions(institution_id) ON DELETE CASCADE,
    CONSTRAINT fk_documents_group FOREIGN KEY (group_id)
        REFERENCES signing_groups(group_id)
);

CREATE INDEX idx_documents_status ON documents(status);

-- ============================================================
-- 6. SIGNING_SESSIONS (Sesi Penandatanganan Kolektif)
-- ============================================================
CREATE TABLE signing_sessions (
    session_id          VARCHAR(36) PRIMARY KEY,       -- UUID v4
    doc_id              VARCHAR(50) NOT NULL,
    bound_digest        BYTEA NOT NULL,                 -- Digest pengikat THRESHDOC-v0 (32 bytes)
    session_status      VARCHAR(25) DEFAULT 'OPEN'      -- OPEN, COLLECTING, COMPLETED, EXPIRED, ABORTED
        CHECK (session_status IN ('OPEN', 'COLLECTING', 'COMPLETED', 'EXPIRED', 'ABORTED')),
    started_at          TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    expires_at          TIMESTAMP WITH TIME ZONE NOT NULL,
    CONSTRAINT fk_sessions_document FOREIGN KEY (doc_id)
        REFERENCES documents(doc_id) ON DELETE CASCADE
);

CREATE INDEX idx_sessions_doc ON signing_sessions(doc_id);

-- ============================================================
-- 7. PARTIAL_SIGNATURES (Tanda Tangan Parsial Tiap Penanda Tangan)
-- ============================================================
CREATE TABLE partial_signatures (
    partial_id          VARCHAR(36) PRIMARY KEY,       -- UUID v4
    session_id          VARCHAR(36) NOT NULL,
    user_id             VARCHAR(36) NOT NULL,
    partial_sig_bytes   BYTEA NOT NULL,                 -- Tanda tangan parsial penanda tangan
    is_valid            BOOLEAN DEFAULT TRUE,           -- Hasil verifikasi koordinator terhadap share
    signed_at           TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_partials_session FOREIGN KEY (session_id)
        REFERENCES signing_sessions(session_id) ON DELETE CASCADE,
    CONSTRAINT fk_partials_user FOREIGN KEY (user_id)
        REFERENCES users(user_id) ON DELETE CASCADE,
    CONSTRAINT uq_session_user_sig UNIQUE (session_id, user_id)
);

CREATE INDEX idx_partials_session ON partial_signatures(session_id);

-- ============================================================
-- 8. FINAL_SIGNATURES (Tanda Tangan Gabungan / Standar FIPS 204)
-- ============================================================
CREATE TABLE final_signatures (
    sig_id              VARCHAR(36) PRIMARY KEY,       -- UUID v4
    session_id          VARCHAR(36) NOT NULL UNIQUE,
    doc_id              VARCHAR(50) NOT NULL UNIQUE,
    combined_sig_bytes  BYTEA NOT NULL,                 -- Tanda tangan gabungan (3309 B untuk ML-DSA-65)
    container_format    VARCHAR(30) DEFAULT 'CMS_SIGNED_DATA'
        CHECK (container_format IN ('CMS_SIGNED_DATA', 'PADES_EMBEDDED', 'RAW_JSON')),
    cms_der_package     BYTEA,                          -- Kontainer ASN.1 CMS SignedData biner
    is_verified         BOOLEAN NOT NULL DEFAULT TRUE,  -- Hasil verifikasi verifier standar
    completed_at        TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_finals_session FOREIGN KEY (session_id)
        REFERENCES signing_sessions(session_id) ON DELETE CASCADE,
    CONSTRAINT fk_finals_document FOREIGN KEY (doc_id)
        REFERENCES documents(doc_id) ON DELETE CASCADE
);

-- ============================================================
-- 9. AUDIT_LOGS (Log Jejak Audit & Ketahanan Forensik)
-- ============================================================
CREATE TABLE audit_logs (
    log_id              VARCHAR(36) PRIMARY KEY,       -- UUID v4
    doc_id              VARCHAR(50),                    -- Opsional, referensi dokumen
    user_id             VARCHAR(36),                    -- Aktor yang melakukan aksi
    action              VARCHAR(50) NOT NULL,           -- DOC_CREATED, PARTIAL_SIGNED, COMBINED, TAMPER_ATTEMPT, REPLAY_BLOCKED
    ip_address          VARCHAR(45),                    -- IPv4 / IPv6
    user_agent          TEXT,
    record_hash         BYTEA NOT NULL,                 -- Hash SHA3-256 berantai (tamper-evident log)
    timestamp           TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_audit_doc ON audit_logs(doc_id);
CREATE INDEX idx_audit_action ON audit_logs(action);
CREATE INDEX idx_audit_timestamp ON audit_logs(timestamp);
```

---

## 2. Kamus Data & Batasan Kriptografi

| Entitas / Kolom | Tipe Data | Ukuran / Format | Penjelasan Kriptografis |
|:---|:---|:---|:---|
| `documents.file_sha3_256` | `BYTEA` | 32 Bytes | Digest SHA3-256 dari konten biner dokumen mentah. |
| `signing_sessions.bound_digest` | `BYTEA` | 32 Bytes | Digest dengan pemisahan domain: `SHA3-256("THRESHDOC-v0" || len || metadata || doc_hash)`. |
| `signing_groups.group_public_key` | `BYTEA` | 1952 Bytes (ML-DSA-65) | Kunci publik agregat untuk verifikasi verifier FIPS 204. |
| `signer_shares.public_key_share` | `BYTEA` | 1952 Bytes (ML-DSA-65) | Kunci publik verifikasi share individu penanda tangan. |
| `partial_signatures.partial_sig_bytes` | `BYTEA` | 3309 Bytes (ML-DSA-65) | Tanda tangan parsial yang dihasilkan masing-masing penanda tangan. |
| `final_signatures.combined_sig_bytes` | `BYTEA` | 3309 Bytes (ML-DSA-65) | Tanda tangan threshold gabungan berukuran konstan $O(1)$. |
| `final_signatures.cms_der_package` | `BYTEA` | ~9.2 KB | Kontainer ASN.1 CMS `pkcs7-signedData` (OID `2.16.840.1.101.3.4.3.18`). |
| `audit_logs.record_hash` | `BYTEA` | 32 Bytes | Hash berantai: `SHA3-256(prev_hash || log_id || action || timestamp)`. |

> **Prinsip Keamanan Tanpa Escrow:**  
> Kunci privat parsial (`secret_key_share`) **TIDAK PERNAH DISIMPAN** dalam basis data server. Kunci privat disimpan secara eksklusif pada secure storage perangkat lokal masing-masing penanda tangan.

---

## 3. Data Awal Percontohan (Seed Data Institusi: Ambang 3-dari-5)

```sql
-- 1. Institusi
INSERT INTO institutions (institution_id, name, code, address)
VALUES ('inst-001', 'SMAN 1 Teladan Digital', 'SMAN1-TD', 'Jl. Merdeka No. 45, Jakarta');

-- 2. Lima Penanda Tangan
INSERT INTO users (user_id, institution_id, nip_nik, full_name, email, role) VALUES
('usr-001', 'inst-001', '197501012000031001', 'Dr. H. Ahmad Fauzi, M.Pd.', 'kepsek@sman1td.sch.id', 'kepsek'),
('usr-002', 'inst-001', '198002022005011002', 'Dra. Siti Rahmawati, M.Si.', 'wakasek@sman1td.sch.id', 'wakasek'),
('usr-003', 'inst-001', '198503032010012003', 'Budi Santoso, S.Kom.', 'tu@sman1td.sch.id', 'tu'),
('usr-004', 'inst-001', '198804042012012004', 'Sri Wahyuni, S.E.', 'bendahara@sman1td.sch.id', 'bendahara'),
('usr-005', 'inst-001', '3171012345670005', 'Ir. Hendro Wijaya', 'komite@sman1td.sch.id', 'komite');

-- 3. Kebijakan Tanda Tangan (Ambang 3 dari 5)
INSERT INTO signing_groups (group_id, institution_id, policy_name, threshold_k, total_n, algorithm, group_public_key)
VALUES ('grp-001', 'inst-001', 'Kebijakan Pengesahan Ijazah & SK Kelulusan (3 dari 5)', 3, 5, 'ML-DSA-65', '\x00');
```
