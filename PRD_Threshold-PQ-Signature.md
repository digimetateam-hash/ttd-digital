# PRD + Kode Referensi: Tanda Tangan Threshold Pasca-Kuantum untuk Dokumen Resmi

**Judul kerja:** *Threshold Post-Quantum Document Signing for Institutional Workflows: Design, Integration, and Empirical Evaluation*

Tanggal: 15 November 2026 · Status: draf awal · Penulis: Indri

---

## 1. Ringkasan dan hasil cek novelty

**Gagasan:** beberapa pihak (misalnya kepala sekolah, wakil, dan tata usaha) menandatangani dokumen resmi bersama, sehingga tanda tangan baru sah bila minimal *k* dari *n* pihak setuju dan tidak ada satu pun yang memegang kunci utuh. Algoritma dasarnya ML-DSA (FIPS 204).

**Hasil cek literatur (pencarian web, 15 November 2026; verifikasi ulang di Scopus/ePrint sebelum menulis): area ini sangat padat.** Merancang protokol threshold ML-DSA baru bukan target realistis untuk satu peneliti dalam 8-10 minggu.

| Karya | Isi singkat | Dampak |
| --- | --- | --- |
| [Mithril (Celi dkk., USENIX Security 2026)](https://www.usenix.org/system/files/conference/usenixsecurity26/sec26_prepub_celi.pdf) | Klaim skema threshold pertama yang praktis dan kompatibel penuh dengan ML-DSA; berbasis berbagi rahasia dengan share pendek | Protokol inti sudah ada |
| [Quorus (Bienstock dkk., ePrint 2025/1163)](https://eprint.iacr.org/2025/1163) | Threshold ML-DSA dari MPC, skala hingga puluhan penanda tangan, verifikasi FIPS 204 standar | Pendekatan MPC sudah ada |
| [THED (ePrint 2026/638)](https://eprint.iacr.org/2026/638) | Threshold Dilithium dari FHE, dua ronde | Pendekatan FHE sudah ada |
| [Pebble (Silence Laboratories, 2026)](https://silencelaboratories.com/papers/pebble-normal-threshold-ml-dsa.pdf) | Threshold ML-DSA dengan nonce Gaussian diskret | Variasi desain sudah ada |
| [Masked Threshold ML-DSA (Kao, arXiv 2601.20917)](https://arxiv.org/abs/2601.20917) | Threshold sembarang dengan tanda tangan berukuran standar | Ambang besar sudah ada |
| [TALUS (arXiv 2603.22109)](https://arxiv.org/pdf/2603.22109) | Threshold ML-DSA yang tepat sesuai FIPS 204 | Area terus bergerak |
| [Quorus preview di NIST](https://csrc.nist.gov/csrc/media/Projects/threshold-cryptography/documents/TCall-1/Quorus-PW01.pdf) dan [Mithril preview di NIST](https://csrc.nist.gov/csrc/media/Projects/threshold-cryptography/documents/TCall-1/Mithril-PW01.pdf) | Pengajuan ke NIST Threshold Call | Standardisasi masih berjalan; skema bisa berubah |

**Posisi naskah yang diusulkan (realistis dan jujur):** bukan protokol baru, melainkan **studi terapan dan evaluasi empiris** untuk alur dokumen institusi. Celah yang saya lihat (belum saya temukan dikerjakan; periksa ulang):

1. **Integrasi ke alur dokumen resmi** (PDF, kontainer tanda tangan) dengan verifikasi memakai verifier ML-DSA standar tanpa modifikasi.
2. **Evaluasi pada beban kerja institusi:** ambang kecil (2 dari 3, 3 dari 5, 5 dari 9), jaringan sekolah/kantor, penanda tangan yang offline, dan biaya percobaan ulang akibat rejection sampling.
3. **Lapisan pengikatan dokumen dan kebijakan:** analisis keamanan bahwa tanda tangan tidak bisa dipakai ulang lintas dokumen atau dengan himpunan penanda tangan lain. Ini bagian "dalam" yang masih terjangkau.
4. **Tata kelola kunci:** penggantian anggota (resharing), pencabutan, dan jejak audit.

Konsekuensinya, naskah ini lebih tepat untuk jurnal terapan/sistem atau keamanan terapan daripada jurnal kriptografi teori. Bila tujuanmu kedalaman teori, minta saya mengecek arah lain (misalnya side-channel ML-KEM/ML-DSA di perangkat murah).

## 2. Pertanyaan riset

- **RQ1:** Berapa overhead (ukuran tanda tangan, latensi, komunikasi, jumlah percobaan ulang) skema threshold ML-DSA dibanding baseline multisig (k tanda tangan independen) untuk konfigurasi (2,3), (3,5), (5,9)?
- **RQ2:** Apakah tanda tangan keluaran threshold diterima verifier ML-DSA standar di dalam alur dokumen (PDF/CMS) tanpa perubahan di sisi verifier?
- **RQ3:** Apakah lapisan pengikatan dokumen-kebijakan-penanda tangan mencegah replay lintas dokumen dan penggantian himpunan penanda tangan?
- **RQ4:** Bagaimana kinerja saat sebagian penanda tangan offline atau lambat?

## 3. Model ancaman

- **Pihak:** *Penanda tangan* (n orang/perangkat), *Koordinator* (menyusun dokumen dan menggabungkan hasil), *Verifier* (pihak penerima dokumen), *Adversary*.
- **Adversary yang ditangani:** koalisi hingga k-1 penanda tangan yang berkolusi atau kuncinya dicuri; koordinator yang berniat jahat (tidak boleh bisa memalsukan tanda tangan atas dokumen lain); penyerang yang memutar ulang tanda tangan pada dokumen atau kebijakan lain.
- **Di luar cakupan:** kompromi k atau lebih penanda tangan; kompromi perangkat tingkat kernel; keabsahan hukum (lihat risiko).

**Properti:** unforgeability di bawah ambang, *document binding* (tanda tangan terikat pada isi dokumen, ID, k, dan daftar penanda tangan), kompatibilitas verifier FIPS 204, ketahanan pasca-kuantum.

## 4. Arsitektur

```
 Penanda tangan p1..pn          Koordinator                       Verifier
 (kunci/share terpisah)   ┌───────────────────────┐
        │  setuju(k dari n) │ 1. digest = H(dokumen, id, k, daftar)
        ├──partial_sign────►│ 2. kumpulkan >= k partial
        │                   │ 3. combine -> tanda tangan           ┌──────────────┐
        │                   └──────────┬────────────┘             │ verify(pk,   │
        │                              └── dokumen + tanda tangan ►│ digest, sig) │
        │                                                          └──────────────┘
```

Backend bisa ditukar: **baseline multisig** (ada di kode) dan **skema threshold sungguhan** (Mithril/Quorus/Pebble, lewat antarmuka).

## 5. Kebutuhan fungsional (MVP)

1. **Pengikat dokumen:** digest yang mencakup isi dokumen, ID, ambang k, dan daftar penanda tangan, dengan pemisahan domain.
2. **Abstraksi backend** (`setup`, `partial_sign`, `combine`, `verify`).
3. **Backend baseline multisig** untuk pembanding.
4. **Adaptor ke implementasi threshold ML-DSA** referensi (subprocess/FFI).
5. **Alur persetujuan** k dari n, dengan penolakan penanda tangan di luar daftar.
6. **Skrip benchmark** (ukuran, waktu, retry) dan **uji keamanan alur** (replay, substitusi).
7. **Pembungkus format dokumen** (PDF/CMS) setelah dukungan ML-DSA di pustaka target dipastikan.

## 6. Kebutuhan non-fungsional

- Jangan menulis protokol threshold sendiri tanpa tinjauan kriptografer; pakai implementasi referensi yang dipublikasikan.
- Seluruh kode, parameter, dan skrip benchmark dirilis terbuka.
- Kunci tidak pernah disimpan atau dikirim dalam bentuk utuh; log audit mencatat siapa menyetujui apa dan kapan.

## 7. Metodologi evaluasi

- **RQ1:** untuk tiap (k,n) dan tiap backend, minimal 30 kali pengulangan; laporkan median dan IQR untuk ukuran tanda tangan, waktu penandatanganan, waktu verifikasi, jumlah ronde, komunikasi per pihak, dan jumlah percobaan ulang.
- **RQ2:** uji verifikasi dengan minimal dua pustaka ML-DSA independen; dokumentasikan format kontainer yang berhasil dan yang tidak.
- **RQ3:** serangkaian uji negatif otomatis (dokumen diubah, k diubah, daftar penanda tangan diganti, tanda tangan dipindah ke dokumen lain) plus argumen keamanan tertulis atas pengikatan digest.
- **RQ4:** simulasi penanda tangan yang offline atau lambat (latensi tambahan, drop pesan).

## 8. Metrik keberhasilan

- Semua uji negatif RQ3 ditolak verifier.
- Tabel perbandingan lengkap untuk minimal 3 konfigurasi (k,n) dan 2 backend.
- Artefak dapat direplikasi dari repositori.

## 9. Risiko

| Risiko | Mitigasi |
| --- | --- |
| Skema dan API implementasi referensi berubah (NIST Threshold Call masih berjalan) | Kunci versi dan commit; jelaskan batasan di naskah |
| Implementasi referensi adalah prototipe riset, belum untuk produksi | Jangan mengklaim siap produksi; jelaskan status keamanannya |
| Klaim novelty ditantang | Posisikan sebagai studi terapan dan evaluasi, bukan protokol baru |
| Dukungan ML-DSA di PDF/CMS belum merata | Verifikasi dulu per pustaka; laporkan hasil negatif |
| Keabsahan hukum tanda tangan elektronik di Indonesia | Belum saya verifikasi; kaji aturan tanda tangan elektronik tersertifikasi dan penyelenggara sertifikasi sebelum mengklaim apa pun soal keabsahan |

## 10. Kode referensi (Python)

Simpan sebagai `threshold_docsign.py` lalu jalankan `python threshold_docsign.py`. Ini **kerangka riset dan baseline**, bukan skema threshold sejati: `MultiSigBackend` mengumpulkan k tanda tangan independen, sehingga ukuran dan waktu verifikasinya tumbuh sebanding k. Skema threshold sungguhan menghasilkan **satu** tanda tangan ML-DSA berukuran standar; itu yang dibandingkan di RQ1 lewat `ExternalThresholdBackend`. Tanda tangan memakai ML-DSA bila `liboqs-python` (`oqs`) terpasang, kalau tidak jatuh ke Ed25519 yang **bukan** pasca-kuantum.

```python
"""threshold_docsign.py - kerangka riset tanda tangan dokumen k-dari-n (v0). Python >= 3.9."""
from __future__ import annotations
import hashlib
import json
import statistics
import time
from dataclasses import dataclass

_PQ_NAMES = ("ML-DSA-65", "Dilithium3")


# ---------- Kunci tanda tangan (ML-DSA bila tersedia) ----------
class SigKey:
    def __init__(self):
        self.alg = None
        try:
            import oqs
            enabled = oqs.get_enabled_sig_mechanisms()
            for name in _PQ_NAMES:
                if name in enabled:
                    self._oqs = oqs.Signature(name)
                    self.pk = self._oqs.generate_keypair()
                    self.alg = name
                    break
        except Exception:
            pass
        if self.alg is None:
            from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
            from cryptography.hazmat.primitives import serialization as ser
            self._ed = Ed25519PrivateKey.generate()
            self.pk = self._ed.public_key().public_bytes(ser.Encoding.Raw, ser.PublicFormat.Raw)
            self.alg = "Ed25519-FALLBACK(bukan-PQ)"

    def sign(self, msg: bytes) -> bytes:
        return self._oqs.sign(msg) if self.alg in _PQ_NAMES else self._ed.sign(msg)


def verify_sig(alg: str, pk: bytes, msg: bytes, sig: bytes) -> bool:
    if alg in _PQ_NAMES:
        import oqs
        with oqs.Signature(alg) as v:
            return bool(v.verify(msg, sig, pk))
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
    from cryptography.exceptions import InvalidSignature
    try:
        Ed25519PublicKey.from_public_bytes(pk).verify(sig, msg)
        return True
    except InvalidSignature:
        return False


# ---------- Kebijakan dan pengikatan dokumen ----------
@dataclass(frozen=True)
class Policy:
    k: int
    signers: tuple  # identitas/peran penanda tangan; panjang = n

    def __post_init__(self):
        if not (1 <= self.k <= len(self.signers)):
            raise ValueError("syarat: 1 <= k <= n")
        if len(set(self.signers)) != len(self.signers):
            raise ValueError("daftar penanda tangan harus unik")


def document_digest(doc: bytes, doc_id: str, policy: Policy) -> bytes:
    """Mengikat isi dokumen, ID, k, dan daftar penanda tangan (pemisahan domain)."""
    meta = json.dumps({"doc_id": doc_id, "k": policy.k, "signers": list(policy.signers)},
                      sort_keys=True).encode()
    return hashlib.sha3_256(
        b"THRESHDOC-v0" + len(meta).to_bytes(4, "big") + meta + hashlib.sha3_256(doc).digest()
    ).digest()


# ---------- Backend ----------
class MultiSigBackend:
    """Baseline: tiap penanda tangan punya kunci sendiri; k tanda tangan independen dikumpulkan.
    Ukuran tanda tangan dan waktu verifikasi tumbuh linear terhadap k."""
    name = "multisig-baseline"

    def setup(self, policy: Policy) -> dict:
        self._keys = {s: SigKey() for s in policy.signers}
        return {"k": policy.k,
                "pks": {s: (key.alg, key.pk.hex()) for s, key in self._keys.items()}}

    def partial_sign(self, signer_id: str, msg: bytes) -> bytes:
        return self._keys[signer_id].sign(msg)

    def combine(self, partials: dict, msg: bytes, group: dict) -> dict:
        return {sid: sig.hex() for sid, sig in partials.items()}

    def verify(self, group: dict, msg: bytes, signature: dict) -> bool:
        good = 0
        for sid, sig_hex in signature.items():  # kunci dict unik: duplikat dihitung sekali
            if sid not in group["pks"]:
                continue
            alg, pk_hex = group["pks"][sid]
            try:
                if verify_sig(alg, bytes.fromhex(pk_hex), msg, bytes.fromhex(sig_hex)):
                    good += 1
            except Exception:
                continue
        return good >= group["k"]

    def sig_bytes(self, signature: dict) -> int:
        return sum(len(h) // 2 for h in signature.values())


class ExternalThresholdBackend:
    """Antarmuka untuk skema threshold ML-DSA sungguhan (implementasi referensi Mithril, Quorus,
    Pebble, dst. dalam Go/Rust/C), dipanggil lewat subprocess atau FFI. Kontrak: combine() menghasilkan
    SATU tanda tangan FIPS 204 standar, dan verify() memakai verifier ML-DSA biasa."""
    name = "external-threshold"

    def __init__(self, *args, **kwargs):
        raise NotImplementedError(
            "Hubungkan ke implementasi referensi yang dipublikasikan. Jangan menulis protokol "
            "threshold sendiri tanpa tinjauan kriptografer.")


# ---------- Alur persetujuan ----------
def sign_document(doc: bytes, doc_id: str, policy: Policy, backend, group: dict, approvers):
    msg = document_digest(doc, doc_id, policy)
    partials = {}
    for s in approvers:
        if s not in policy.signers:
            raise ValueError(f"{s!r} bukan penanda tangan yang terdaftar")
        partials[s] = backend.partial_sign(s, msg)
    return msg, backend.combine(partials, msg, group)


# ---------- Benchmark (RQ1, baseline) ----------
def bench(configs=((2, 3), (3, 5), (5, 9)), runs=5):
    rows = []
    for k, n in configs:
        policy = Policy(k, tuple(f"p{i}" for i in range(n)))
        be = MultiSigBackend()
        group = be.setup(policy)
        t_sign, t_ver, size = [], [], 0
        for r in range(runs):
            doc = f"dokumen {r}".encode()
            t0 = time.perf_counter()
            msg, sig = sign_document(doc, f"doc-{r}", policy, be, group, policy.signers[:k])
            t1 = time.perf_counter()
            ok = be.verify(group, msg, sig)
            t2 = time.perf_counter()
            assert ok
            t_sign.append((t1 - t0) * 1000)
            t_ver.append((t2 - t1) * 1000)
            size = be.sig_bytes(sig)
        rows.append((be.name, k, n, size, statistics.median(t_sign), statistics.median(t_ver)))
    return rows


if __name__ == "__main__":
    policy = Policy(3, ("kepsek", "wakasek", "tu", "bendahara", "komite"))
    be = MultiSigBackend()
    group = be.setup(policy)
    doc = b"Surat Keputusan No. 123"
    print("algoritma:", group["pks"]["kepsek"][0])

    msg, sig = sign_document(doc, "SK-123", policy, be, group, ["kepsek", "wakasek", "tu"])
    print("3 dari 5 menyetujui            ->", be.verify(group, msg, sig))

    msg2, sig2 = sign_document(doc, "SK-123", policy, be, group, ["kepsek", "wakasek"])
    print("hanya 2 dari 5                 ->", be.verify(group, msg2, sig2))

    dup = dict(sig)
    dup2 = {"kepsek": sig["kepsek"]}
    print("satu penanda tangan diulang    ->", be.verify(group, msg, dup2))

    tampered = document_digest(b"Surat Keputusan No. 999", "SK-123", policy)
    print("dokumen diubah                 ->", be.verify(group, tampered, dup))

    other = Policy(3, ("kepsek", "wakasek", "tu", "bendahara", "pihak-lain"))
    swapped = document_digest(doc, "SK-123", other)
    print("daftar penanda tangan diganti  ->", be.verify(group, swapped, dup))

    replay = document_digest(doc, "SK-124", policy)
    print("replay ke ID dokumen lain      ->", be.verify(group, replay, dup))

    print("\nBenchmark baseline (median, ms):")
    print(f"{'backend':20s} {'k':>2s} {'n':>2s} {'ukuran(B)':>10s} {'sign':>8s} {'verify':>8s}")
    for name, k, n, size, ts, tv in bench():
        print(f"{name:20s} {k:>2d} {n:>2d} {size:>10d} {ts:>8.2f} {tv:>8.2f}")
```

### Cara pakai dan integrasi skema threshold sejati

```bash
pip install cryptography           # fallback Ed25519
pip install liboqs-python          # opsional, untuk ML-DSA (butuh liboqs)
python threshold_docsign.py
```

Langkah pengembangan berikutnya (belum diuji di draf ini; periksa dokumentasi tiap proyek):

1. Pilih 2-3 implementasi referensi yang tersedia publik dari makalah di bagian 1, kunci versi dan commit-nya.
2. Bungkus tiap implementasi sebagai kelas dengan metode `setup`, `partial_sign`, `combine`, `verify` yang sama seperti `MultiSigBackend`. Ganti `ExternalThresholdBackend` dengan adaptor nyata.
3. Pastikan `combine()` mengeluarkan satu tanda tangan ML-DSA standar, lalu verifikasi dengan pustaka ML-DSA independen (RQ2).
4. Jalankan `bench()` untuk semua backend dengan kondisi jaringan yang disimulasikan (RQ1, RQ4).

## 11. Linimasa (10 minggu)

1. **Minggu 1-2:** verifikasi novelty, pilih implementasi referensi, finalisasi model ancaman.
2. **Minggu 3-4:** lapisan pengikatan dokumen, uji negatif RQ3, baseline multisig.
3. **Minggu 5-6:** adaptor ke 2-3 implementasi threshold dan verifikasi silang (RQ2).
4. **Minggu 7-8:** benchmark RQ1 dan simulasi RQ4.
5. **Minggu 9-10:** pembungkus format dokumen, penulisan naskah, perapian artefak replikasi.

## 12. Referensi awal

- NIST. *FIPS 204: Module-Lattice-Based Digital Signature Standard (ML-DSA).* 2024.
- Celi dkk. *Mithril: threshold ML-DSA.* USENIX Security 2026.
- Bienstock, de Castro, Escudero, Polychroniadou. *Quorus: Efficient, Scalable Threshold ML-DSA Signatures from MPC.* ePrint 2025/1163.
- Park, Passelègue, Stehlé. *THED: Threshold Dilithium from FHE.* ePrint 2026/638.
- Kondi dkk. *Pebble: Normal Threshold ML-DSA.* Silence Laboratories, 2026.
- Kao, L. *FIPS 204-Compatible Threshold ML-DSA via Shamir Nonce DKG.* arXiv:2601.20917.
- *TALUS: FIPS-204-Exact Threshold ML-DSA via Boundary Clearance.* arXiv:2603.22109.
