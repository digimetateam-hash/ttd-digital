"""test_threshold_docsign.py - Suite Uji Kualitas & Verifikasi Model Ancaman (RQ3).
Mencakup pengujian unit fungsional, batas ambang kuorum, dan seluruh uji negatif kriptografi.
"""
import pytest
import os
import sys

# Tambahkan direktori root repo ke sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import threshold_docsign as tds


@pytest.fixture
def default_policy():
    return tds.Policy(3, ("kepsek", "wakasek", "tu", "bendahara", "komite"))


@pytest.fixture
def backend():
    return tds.MultiSigBackend()


@pytest.fixture
def group(backend, default_policy):
    return backend.setup(default_policy)


class TestPolicyValidation:
    def test_valid_policy(self):
        p = tds.Policy(2, ("p1", "p2", "p3"))
        assert p.k == 2
        assert len(p.signers) == 3

    def test_invalid_k_zero(self):
        with pytest.raises(ValueError, match="syarat: 1 <= k <= n"):
            tds.Policy(0, ("p1", "p2"))

    def test_invalid_k_greater_than_n(self):
        with pytest.raises(ValueError, match="syarat: 1 <= k <= n"):
            tds.Policy(4, ("p1", "p2", "p3"))

    def test_duplicate_signers_rejected(self):
        with pytest.raises(ValueError, match="daftar penanda tangan harus unik"):
            tds.Policy(2, ("p1", "p1", "p2"))


class TestDocumentBinding:
    def test_digest_deterministic(self, default_policy):
        doc = b"Surat Keputusan Resmi 2026"
        d1 = tds.document_digest(doc, "SK-001", default_policy)
        d2 = tds.document_digest(doc, "SK-001", default_policy)
        assert d1 == d2
        assert len(d1) == 32  # SHA3-256 output

    def test_digest_content_sensitive(self, default_policy):
        d1 = tds.document_digest(b"Dokumen Asli", "SK-001", default_policy)
        d2 = tds.document_digest(b"Dokumen Palsu", "SK-001", default_policy)
        assert d1 != d2

    def test_digest_id_sensitive(self, default_policy):
        doc = b"Dokumen Sama"
        d1 = tds.document_digest(doc, "SK-001", default_policy)
        d2 = tds.document_digest(doc, "SK-002", default_policy)
        assert d1 != d2

    def test_digest_policy_sensitive(self):
        doc = b"Dokumen Sama"
        p1 = tds.Policy(2, ("p1", "p2", "p3"))
        p2 = tds.Policy(3, ("p1", "p2", "p3"))
        d1 = tds.document_digest(doc, "SK-001", p1)
        d2 = tds.document_digest(doc, "SK-001", p2)
        assert d1 != d2


class TestRQ3ThreatModelNegativeTests:
    def test_normal_signing_and_verification_pass(self, backend, default_policy, group):
        doc = b"Surat Keputusan 123"
        msg, sig = tds.sign_document(doc, "SK-123", default_policy, backend, group, ["kepsek", "wakasek", "tu"])
        assert backend.verify(group, msg, sig) is True

    def test_quorum_shortfall_rejected(self, backend, default_policy, group):
        """Negatif: Penanda tangan kurang dari k (2 dari 5 ketika k=3)."""
        doc = b"Surat Keputusan 123"
        msg, sig = tds.sign_document(doc, "SK-123", default_policy, backend, group, ["kepsek", "wakasek"])
        assert backend.verify(group, msg, sig) is False

    def test_duplicate_signer_reuse_rejected(self, backend, default_policy, group):
        """Negatif: Penanda tangan tunggal menduplikasi tanda tangan untuk memalsukan kuorum."""
        doc = b"Surat Keputusan 123"
        msg, sig = tds.sign_document(doc, "SK-123", default_policy, backend, group, ["kepsek", "wakasek", "tu"])
        dup_sig = {"kepsek": sig["kepsek"]}
        assert backend.verify(group, msg, dup_sig) is False

    def test_content_tampering_rejected(self, backend, default_policy, group):
        """Negatif: Isi dokumen diubah setelah penandatanganan."""
        doc = b"Surat Keputusan 123"
        msg, sig = tds.sign_document(doc, "SK-123", default_policy, backend, group, ["kepsek", "wakasek", "tu"])
        tampered_msg = tds.document_digest(b"Surat Keputusan PALSU 999", "SK-123", default_policy)
        assert backend.verify(group, tampered_msg, sig) is False

    def test_replay_attack_rejected(self, backend, default_policy, group):
        """Negatif: Tanda tangan diputar ulang ke nomor/ID dokumen berbeda."""
        doc = b"Surat Keputusan 123"
        msg, sig = tds.sign_document(doc, "SK-123", default_policy, backend, group, ["kepsek", "wakasek", "tu"])
        replay_msg = tds.document_digest(doc, "SK-LAIN-999", default_policy)
        assert backend.verify(group, replay_msg, sig) is False

    def test_signer_substitution_rejected(self, backend, default_policy, group):
        """Negatif: Daftar anggota penanda tangan dalam kebijakan diganti pihak asing."""
        doc = b"Surat Keputusan 123"
        msg, sig = tds.sign_document(doc, "SK-123", default_policy, backend, group, ["kepsek", "wakasek", "tu"])
        swapped_policy = tds.Policy(3, ("kepsek", "wakasek", "tu", "bendahara", "penyusup"))
        swapped_msg = tds.document_digest(doc, "SK-123", swapped_policy)
        assert backend.verify(group, swapped_msg, sig) is False

    def test_unregistered_signer_aborts(self, backend, default_policy, group):
        """Negatif: Pihak yang tidak terdaftar mencoba ikut menandatangani."""
        doc = b"Surat Keputusan 123"
        with pytest.raises(ValueError, match="bukan penanda tangan yang terdaftar"):
            tds.sign_document(doc, "SK-123", default_policy, backend, group, ["kepsek", "wakasek", "orang_asing"])

