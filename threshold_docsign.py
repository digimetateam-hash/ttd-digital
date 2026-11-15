"""threshold_docsign.py - Modul Inti Tanda Tangan Dokumen Threshold Pasca-Kuantum k-dari-n.
Mendukung ML-DSA-65 (FIPS 204) bila liboqs tersedia, dengan fallback aman ke Ed25519.
"""
from __future__ import annotations
import hashlib
import json
import os
import statistics
import sys
import time
from dataclasses import dataclass

# Path fallback untuk macOS Homebrew liboqs & Linux standard paths
for p in ("/opt/homebrew", "/usr/local", "/usr"):
    if os.path.exists(os.path.join(p, "lib", "liboqs.dylib")) or os.path.exists(os.path.join(p, "lib", "liboqs.so")):
        os.environ.setdefault("OQS_DIR", p)
        cur_dyld = os.environ.get("DYLD_LIBRARY_PATH", "")
        if f"{p}/lib" not in cur_dyld:
            os.environ["DYLD_LIBRARY_PATH"] = f"{p}/lib:{cur_dyld}" if cur_dyld else f"{p}/lib"
        break

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

