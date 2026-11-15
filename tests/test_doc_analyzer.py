"""
Unit test suite untuk modul doc_analyzer.py
Menguji parsing multi-format: Word (.docx, .doc, .rtf), Excel (.xlsx, .csv, .xls), PDF, dan OCR.
"""

import io
import pytest
import docx
import openpyxl
import pymupdf as fitz
from doc_analyzer import (
    analyze_document_unified,
    run_tesseract_ocr,
    get_tesseract_binary_path,
    ALL_SUPPORTED_EXTENSIONS
)


def test_supported_extensions_list():
    assert "docx" in ALL_SUPPORTED_EXTENSIONS
    assert "doc" in ALL_SUPPORTED_EXTENSIONS
    assert "xlsx" in ALL_SUPPORTED_EXTENSIONS
    assert "xls" in ALL_SUPPORTED_EXTENSIONS
    assert "csv" in ALL_SUPPORTED_EXTENSIONS
    assert "pdf" in ALL_SUPPORTED_EXTENSIONS
    assert "png" in ALL_SUPPORTED_EXTENSIONS


def test_parse_docx():
    doc = docx.Document()
    doc.add_heading("SURAT KEPUTUSAN PENGADAAN 2026", level=1)
    doc.add_paragraph("Menimbang bahwa teknologi post-quantum diperlukan.")
    doc.core_properties.author = "Pejabat Pembuat Komitmen"
    doc.core_properties.title = "SK Pengadaan FIPS 204"

    buf = io.BytesIO()
    doc.save(buf)
    file_bytes = buf.getvalue()

    result = analyze_document_unified(file_bytes, "sk_pengadaan.docx")
    assert result.doc_type == "Word"
    assert result.extension == "docx"
    assert "SURAT KEPUTUSAN PENGADAAN" in result.extracted_text
    assert result.author == "Pejabat Pembuat Komitmen"
    assert len(result.sha3_256) == 64


def test_parse_excel_xlsx():
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Anggaran"
    ws.append(["Komponen", "Biaya", "Status"])
    ws.append(["Server Post-Quantum", 150000000, "Disetujui"])
    ws.append(["Audit Kripto", 45000000, "Pending"])

    buf = io.BytesIO()
    wb.save(buf)
    file_bytes = buf.getvalue()

    result = analyze_document_unified(file_bytes, "rab_sekolah.xlsx")
    assert result.doc_type == "Excel"
    assert "Anggaran" in result.excel_sheets
    assert "Server Post-Quantum" in result.extracted_text
    assert len(result.sha3_256) == 64


def test_parse_csv():
    csv_content = "ID,Nama,Jabatan,Gaji\n1,Ahmad,Kepsek,12000000\n2,Budi,Bendahara,8000000\n"
    file_bytes = csv_content.encode("utf-8")

    result = analyze_document_unified(file_bytes, "pegawai.csv")
    assert result.doc_type == "Excel"
    assert result.extension == "csv"
    assert "Ahmad" in result.extracted_text
    assert "Data" in result.excel_sheets
    assert len(result.excel_sheets["Data"]) == 2


def test_parse_pdf_and_ocr():
    # Buat PDF digital dengan teks
    doc = fitz.open()
    page = doc.new_page(width=500, height=250)
    page.insert_text((50, 100), "DOKUMEN RESMI TTD POST-QUANTUM", fontsize=16)
    pdf_bytes = doc.tobytes()
    doc.close()

    result = analyze_document_unified(pdf_bytes, "dokumen_resmi.pdf")
    assert result.doc_type == "PDF"
    assert "DOKUMEN RESMI TTD POST-QUANTUM" in result.extracted_text
    assert result.page_count == 1
    assert result.is_scanned_pdf is False


def test_tesseract_ocr_execution():
    tess_path = get_tesseract_binary_path()
    if not tess_path:
        pytest.skip("Tesseract tidak terpasang di sistem.")

    # Buat citra sintesis teks
    doc = fitz.open()
    page = doc.new_page(width=400, height=120)
    page.insert_text((30, 60), "VERIFIKASI OCR BERHASIL 100%", fontsize=14)
    pix = page.get_pixmap(dpi=150)
    png_bytes = pix.tobytes("png")
    doc.close()

    text, err = run_tesseract_ocr(png_bytes, lang="ind+eng")
    assert err is None
    assert "VERIFIKASI OCR BERHASIL" in text



def test_all_samples_dataset():
    """Menguji parsing dan integritas seluruh 7 berkas dataset sampel."""
    import os
    samples_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "samples")
    assert os.path.exists(samples_dir), "Folder samples harus ada"
    
    expected_files = [
        "01_SK_Rektor_Kurikulum_PQC_2026.docx",
        "02_RAB_Anggaran_BOS_Lab_PQC.xlsx",
        "03_BAST_Pengadaan_Server_PQC.pdf",
        "04_Surat_Izin_Operasional_Scan.pdf",
        "05_Laporan_Keuangan_Pengadaan.csv",
        "06_Surat_Edaran_Sosialisasi_Legacy.rtf",
        "07_Ijazah_Sertifikat_Fisik_Scan.png"
    ]
    for fn in expected_files:
        fp = os.path.join(samples_dir, fn)
        assert os.path.exists(fp), f"Berkas sampel {fn} tidak ditemukan"
        with open(fp, "rb") as f:
            data = f.read()
        res = analyze_document_unified(data, fn, run_ocr_forced=True)
        assert res.doc_type in ["Word", "Excel", "PDF", "Image"]
        assert len(res.extracted_text) > 0, f"Ekstraksi teks kosong pada {fn}"
