"""
Skrip Pembangkit Dataset Uji Coba Resmi Multi-Format
Menghasilkan berkas sampel realistis untuk pengujian sistem TTD Digital Post-Quantum:
1. Word (.docx): Surat Keputusan Rektor
2. Excel (.xlsx): Rencana Anggaran Biaya (RAB) Multi-Sheet
3. PDF Digital (.pdf): Berita Acara Serah Terima (BAST)
4. PDF Scan (.pdf): Dokumen Citra Hasil Pindai (Memicu OCR Tesseract)
5. CSV (.csv): Laporan Realisasi Keuangan Transaksi
6. RTF (.rtf): Surat Edaran Resmi Format Word Legacy
7. Citra Scan (.png): Sertifikat Fisik Hasil Foto/Scan untuk Uji OCR
"""

import io
import os
import csv
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
import pymupdf as fitz
from PIL import Image, ImageDraw, ImageFont


def create_sample_docx(filepath: str):
    """Membuat sampel dokumen Word (.docx) resmi."""
    doc = docx.Document()
    
    # Metadata
    doc.core_properties.title = "Surat Keputusan Rektor tentang Kurikulum Pasca-Kuantum 2026"
    doc.core_properties.author = "Prof. Dr. Ir. H. Bambang Sudarsono, M.Kom."
    doc.core_properties.category = "Surat Keputusan Resmi"
    doc.core_properties.comments = "Dokumen resmi untuk pengesahan kolektif k-dari-n threshold ML-DSA FIPS 204"

    # Header Judul
    p_kop = doc.add_paragraph()
    p_kop.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_kop = p_kop.add_run("KEMENTERIAN PENDIDIKAN TINGGI, SAINS, DAN TEKNOLOGI\nUNIVERSITAS NUSANTARA TEKNOLOGI DIGITAL\n")
    r_kop.bold = True
    r_kop.font.size = Pt(13)
    r_sub = p_kop.add_run("Gedung Rektorat Sayap Timur Lt. 4, Kawasan Riset Kuantum Indonesia\nLaman: https://digimeta.ac.id | Pos-el: rektorat@digimeta.ac.id\n")
    r_sub.font.size = Pt(9)
    r_sub.font.italic = True

    p_hr = doc.add_paragraph()
    p_hr.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_hr.add_run("=" * 65).bold = True

    # Nomor SK
    p_sk = doc.add_paragraph()
    p_sk.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_sk = p_sk.add_run("SURAT KEPUTUSAN REKTOR\nNOMOR: SK-REKTOR-2026/089\n\nTENTANG\nPENETAPAN KURIKULUM NASIONAL KRIPTOGRAFI PASCA-KUANTUM (ML-DSA / FIPS 204)\nTAHUN AKADEMIK 2026/2027\n")
    r_sk.bold = True
    r_sk.font.size = Pt(11)

    # Menimbang & Mengingat
    doc.add_heading("MENIMBANG:", level=2)
    doc.add_paragraph(
        "a. Bahwa perkembangan komputer kuantum berpotensi meretas sistem enkripsi dan tanda tangan RSA/ECC konvensional;\n"
        "b. Bahwa standar NIST FIPS 204 (ML-DSA) telah resmi diundangkan sebagai standar global tanda tangan pasca-kuantum;\n"
        "c. Bahwa institusi perlu menetapkan kurikulum adaptif dan pengesahan kolektif berbasis ambang k-dari-n."
    )

    doc.add_heading("MEMUTUSKAN:", level=2)
    doc.add_paragraph(
        "KESATU: Mengesahkan Mata Kuliah Wajib Kriptografi Pasca-Kuantum bagi seluruh program studi informatika dan sistem informasi;\n"
        "KEDUA: Menetapkan rincian distribusi beban mata kuliah dan alokasi laboratorium sebagaimana tertera dalam tabel berikut:"
    )

    # Tabel Rincian
    table = doc.add_table(rows=1, cols=4)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    hdr_cells = table.rows[0].cells
    headers = ["Kode MK", "Nama Mata Kuliah", "SKS", "Status"]
    for i, h in enumerate(headers):
        hdr_cells[i].text = h
        hdr_cells[i].paragraphs[0].runs[0].bold = True

    data_rows = [
        ["CS-411", "Kriptografi Kisi & Lattice Cryptography", "3 SKS", "Wajib"],
        ["CS-412", "Standar FIPS 204 ML-DSA & Implementasi", "3 SKS", "Wajib"],
        ["CS-413", "Protokol Threshold & Multi-Party Computation", "3 SKS", "Wajib Lab"],
        ["CS-414", "Audit Forensik Tanda Tangan Digital PQC", "2 SKS", "Pilihan"],
    ]
    for row in data_rows:
        row_cells = table.add_row().cells
        for i, val in enumerate(row):
            row_cells[i].text = val

    p_penutup = doc.add_paragraph("\nDitetapkan di Jakarta pada tanggal 15 November 2026.\nDokumen ini sah jika telah ditandatangani minimal 3 dari 5 anggota dewan senat rektorat.")
    p_penutup.paragraph_format.space_before = Pt(12)

    doc.save(filepath)
    print(f"[OK] Word DOCX dibuat: {filepath}")


def create_sample_xlsx(filepath: str):
    """Membuat sampel dokumen Excel (.xlsx) multi-sheet resmi."""
    wb = openpyxl.Workbook()
    
    # Sheet 1: RAB Pengadaan
    ws1 = wb.active
    ws1.title = "RAB_Pengadaan_PQC"
    
    # Header format
    header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
    header_fill = PatternFill(start_color="1F497D", end_color="1F497D", fill_type="solid")
    center_align = Alignment(horizontal="center", vertical="center")
    border_thin = Border(
        left=Side(style='thin', color='D9D9D9'),
        right=Side(style='thin', color='D9D9D9'),
        top=Side(style='thin', color='D9D9D9'),
        bottom=Side(style='thin', color='D9D9D9')
    )

    ws1.merge_cells("A1:G1")
    ws1["A1"] = "RENCANA ANGGARAN BIAYA (RAB) LABORATORIUM KOMPUTASI PASCA-KUANTUM"
    ws1["A1"].font = Font(name="Calibri", size=14, bold=True, color="1F497D")
    ws1["A1"].alignment = center_align

    ws1.merge_cells("A2:G2")
    ws1["A2"] = "Tahun Anggaran: 2026/2027 | ID Proyek: RAB-PQC-LAB-2026-X1"
    ws1["A2"].font = Font(name="Calibri", size=10, italic=True)
    ws1["A2"].alignment = center_align

    headers = ["No", "Kode Akun", "Komponen Pengadaan", "Spesifikasi Teknis", "Volume", "Harga Satuan (Rp)", "Total Biaya (Rp)"]
    for col_idx, h in enumerate(headers, 1):
        cell = ws1.cell(row=4, column=col_idx, value=h)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = center_align

    items = [
        (1, "5.3.2.1", "Server Rak Serverless HSM PQC", "Dual Xeon 64-core, ML-DSA acceleration hardware", 2, 75000000),
        (2, "5.3.2.2", "Kunci Keamanan Fisik FIDO-PQC", "Token FIPS 140-3 Level 3 Hybrid Dilithium", 15, 2500000),
        (3, "5.3.2.3", "Lisensi Simulator Komputasi Kuantum", "SDK Emulasi QPU 64-qubit untuk pengujian Shor", 1, 35000000),
        (4, "5.3.2.4", "Perangkat Workstation Forensik", "Apple Silicon M4 Max 128GB Unified Memory", 2, 60000000),
        (5, "5.3.2.5", "Jasa Audit Independen Kriptografi", "Sertifikasi BSSN & Pengujian Ambang Batas", 1, 45000000),
    ]

    start_row = 5
    for idx, (no, kode, nama, spek, vol, harga) in enumerate(items, start_row):
        ws1.cell(row=idx, column=1, value=no).alignment = center_align
        ws1.cell(row=idx, column=2, value=kode).alignment = center_align
        ws1.cell(row=idx, column=3, value=nama)
        ws1.cell(row=idx, column=4, value=spek)
        ws1.cell(row=idx, column=5, value=vol).alignment = center_align
        ws1.cell(row=idx, column=6, value=harga).number_format = '#,##0'
        total_cell = ws1.cell(row=idx, column=7, value=f"=E{idx}*F{idx}")
        total_cell.number_format = '#,##0'
        total_cell.font = Font(bold=True)

    end_row = start_row + len(items)
    ws1.merge_cells(f"A{end_row}:F{end_row}")
    total_label = ws1.cell(row=end_row, column=1, value="TOTAL ANGGARAN YANG DISETUJUI (Rp)")
    total_label.font = Font(bold=True, size=11)
    total_label.alignment = Alignment(horizontal="right")
    grand_total = ws1.cell(row=end_row, column=7, value=f"=SUM(G5:G{end_row-1})")
    grand_total.font = Font(bold=True, size=11, color="1F497D")
    grand_total.number_format = '#,##0'

    # Auto-fit columns
    for col in ws1.columns:
        max_len = max(len(str(cell.value or '')) for cell in col)
        col_letter = openpyxl.utils.get_column_letter(col[0].column)
        ws1.column_dimensions[col_letter].width = max(max_len + 3, 12)

    # Sheet 2: Daftar Verifikator Kuorum
    ws2 = wb.create_sheet(title="Kuorum_Verifikator")
    ws2.append(["ID Role", "Nama Pejabat", "Jabatan Resmi", "Ambang Syarat", "Status Rekomendasi"])
    for cell in ws2[1]:
        cell.font = header_font
        cell.fill = header_fill
    verifikators = [
        ("kepsek", "Dr. H. Mulyadi, M.Pd.", "Kepala Sekolah / Rektor", "Wajib Hadir", "Disetujui"),
        ("wakasek", "Ir. Ratna Dewi, M.T.", "Wakil Kepala Sarpras", "Kuorum Minimal", "Disetujui"),
        ("tu", "Ahmad Fauzi, S.E.", "Kepala Tata Usaha", "Kuorum Minimal", "Disetujui"),
        ("bendahara", "Siti Nurhaliza, S.Ak.", "Bendahara Pengeluaran", "Wajib Hadir", "Disetujui"),
        ("komite", "H. Hendra Kusuma, S.H.", "Ketua Komite Lembaga", "Kuorum Minimal", "Disetujui"),
    ]
    for row in verifikators:
        ws2.append(list(row))

    wb.save(filepath)
    print(f"[OK] Excel XLSX dibuat: {filepath}")


def create_sample_digital_pdf(filepath: str):
    """Membuat sampel dokumen PDF digital resmi (BAST)."""
    doc = SimpleDocTemplate(filepath, pagesize=A4, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=16,
        alignment=1,
        textColor=colors.HexColor('#0f172a')
    )
    
    body_style = ParagraphStyle(
        'DocBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=14,
        textColor=colors.HexColor('#1e293b')
    )

    bold_body = ParagraphStyle(
        'BoldBody',
        parent=body_style,
        fontName='Helvetica-Bold'
    )

    elements = []
    elements.append(Paragraph("<b>BERITA ACARA SERAH TERIMA PEKERJAAN (BAST)</b>", title_style))
    elements.append(Paragraph("NOMOR: BAST-PQC-2026/044 | TANGGAL: 15 NOVEMBER 2026", ParagraphStyle('Sub', parent=title_style, fontSize=10, textColor=colors.HexColor('#475569'))))
    elements.append(Spacer(1, 12))
    elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#0f172a'), spaceAfter=15))

    p1 = (
        "Pada hari ini, <b>Jumat tanggal Lima Belas bulan November tahun Dua Ribu Dua Puluh Enam</b>, bertempat di Kantor PPK SPBE "
        "Layanan Pos-Kuantum, kami yang bertanda tangan di bawah ini:<br/><br/>"
        "<b>1. PEJABAT PEMBUAT KOMITMEN (PPK):</b> Dr. Ir. H. Bambang Sudarsono, M.Kom., bertindak atas nama Satuan Kerja Kementerian;<br/>"
        "<b>2. PENYEDIA BARANG/JASA:</b> PT DigiMeta Solusi Kuantum, diwakili oleh Direktur Utama Ir. H. Hendra Kusuma, S.H.<br/><br/>"
        "Menyatakan bahwa Penyedia telah menyelesaikan dan menyerahkan 100% pekerjaan <b>Pengadaan dan Konfigurasi Modul Keamanan Data FIPS 204 (ML-DSA-65)</b> "
        "dengan spesifikasi dan pengujian ambang batas kuorum k=3 dari n=5 yang telah diverifikasi tanpa cacat."
    )
    elements.append(Paragraph(p1, body_style))
    elements.append(Spacer(1, 14))

    # Tabel Rincian BAST
    table_data = [
        [Paragraph("<b>No</b>", bold_body), Paragraph("<b>Uraian Barang / Layanan</b>", bold_body), Paragraph("<b>Volume</b>", bold_body), Paragraph("<b>Status Uji Kripto</b>", bold_body)],
        [Paragraph("1", body_style), Paragraph("Hardware Security Module ML-DSA-65", body_style), Paragraph("2 Unit", body_style), Paragraph("Lolos Verifikasi 100%", body_style)],
        [Paragraph("2", body_style), Paragraph("Kompilasi Kontainer CMS ASN.1 RFC 5652", body_style), Paragraph("1 Paket", body_style), Paragraph("OID Sesuai NIST FIPS 204", body_style)],
        [Paragraph("3", body_style), Paragraph("Pengujian Model Ancaman RQ3 (Tampering & Replay)", body_style), Paragraph("15 Skenario", body_style), Paragraph("Semua Serangan Ditolak", body_style)],
    ]
    t = Table(table_data, colWidths=[30, 260, 80, 140])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f1f5f9')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(t)
    elements.append(Spacer(1, 20))

    elements.append(Paragraph(
        "Demikian Berita Acara Serah Terima ini dibuat dalam rangkap sah untuk dipergunakan sebagaimana mestinya dan "
        "dinyatakan berkekuatan hukum penuh setelah disahkan dengan Tanda Tangan Threshold Pasca-Kuantum.",
        body_style
    ))

    doc.build(elements)
    print(f"[OK] Digital PDF dibuat: {filepath}")


def create_sample_scanned_pdf(filepath: str):
    """
    Membuat sampel PDF hasil scan murni (Citra / Raster).
    Teks dicetak menjadi gambar tanpa stream teks digital, sehingga membuktikan
    kemampuan Tesseract OCR dalam mengekstraksi isi dokumen.
    """
    # 1. Buat citra beresolusi tinggi menyerupai kertas fisik dipindai (A4 @ 150 DPI = 1240 x 1754)
    width, height = 1240, 1754
    img = Image.new("RGB", (width, height), color=(253, 252, 248)) # Kertas putih gading
    draw = ImageDraw.Draw(img)

    # Garis tepi / margin
    draw.rectangle([60, 60, width - 60, height - 60], outline=(220, 220, 220), width=2)

    # Teks Kop Surat
    draw.text((width // 2 - 320, 120), "LEMBAGA LAYANAN PENDIDIKAN TINGGI (LLDIKTI)", fill=(20, 30, 50))
    draw.text((width // 2 - 280, 160), "SURAT IZIN OPERASIONAL SISTEM DIGITAL PQC", fill=(10, 20, 40))
    draw.text((width // 2 - 220, 200), "NOMOR: 442/LLDIKTI-PQC/IZIN/2026", fill=(60, 70, 90))
    draw.line([(100, 240), (width - 100, 240)], fill=(40, 50, 70), width=3)

    # Isi Surat Hasil Pindai
    isi_lines = [
        "DIBERIKAN KEPADA:",
        "Nama Lembaga  : UNIVERSITAS NUSANTARA TEKNOLOGI DIGITAL",
        "Alamat Kampus : Jl. Kuantum Riset No. 10, Jakarta Pusat",
        "Bidang Usaha  : Penyelenggara Tanda Tangan Elektronik Threshold Post-Quantum",
        "",
        "MENYATAKAN BAHWA:",
        "Berdasarkan hasil uji kelaikan forensik kriptografi modul ML-DSA (NIST FIPS 204),",
        "sistem telah memenuhi standar keamanan negara terhadap ancaman komputasi kuantum.",
        "Sistem diizinkan beroperasi penuh untuk pengesahan SK, Ijazah, dan Transaksi Keuangan.",
        "",
        "Ketentuan Khusus:",
        "1. Penandatanganan wajib menggunakan skema k-dari-n dengan kuorum minimal 3 pihak;",
        "2. Setiap manipulasi berkas biner akan otomatis membatalkan seluruh tanda tangan;",
        "3. Masa berlaku sertifikat operasional: 5 (lima) tahun terhitung sejak tanggal penetapan.",
        "",
        "Ditetapkan di Jakarta, 15 November 2026",
        "Direktur Jenderal Keamanan Sistem Informasi Digital Nasional",
    ]

    y_cur = 300
    for line in isi_lines:
        if line.startswith("DIBERIKAN") or line.startswith("MENYATAKAN") or line.startswith("Ketentuan"):
            draw.text((120, y_cur), line, fill=(10, 20, 50))
        else:
            draw.text((140, y_cur), line, fill=(30, 40, 50))
        y_cur += 45

    # Buat Stempel Merah Cap Basah Simulasi
    stamp_x, stamp_y = width - 420, height - 420
    draw.ellipse([stamp_x, stamp_y, stamp_x + 240, stamp_y + 240], outline=(180, 30, 30), width=5)
    draw.ellipse([stamp_x + 12, stamp_y + 12, stamp_x + 228, stamp_y + 228], outline=(180, 30, 30), width=2)
    draw.text((stamp_x + 40, stamp_y + 80), "* LLDIKTI WILAYAH *", fill=(180, 30, 30))
    draw.text((stamp_x + 45, stamp_y + 120), "TERVERIFIKASI SAH", fill=(180, 30, 30))
    draw.text((stamp_x + 65, stamp_y + 160), "TAHUN 2026", fill=(180, 30, 30))

    # Tanda Tangan Simulasi (garis kurva)
    draw.line([(stamp_x - 120, stamp_y + 140), (stamp_x - 40, stamp_y + 110), (stamp_x - 20, stamp_y + 160), (stamp_x + 30, stamp_y + 120)], fill=(20, 30, 100), width=4)

    # 2. Simpan gambar ke PDF menggunakan PyMuPDF sebagai citra penuh (image-only PDF)
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='JPEG', quality=85)
    img_byte_arr.seek(0)

    pdf_doc = fitz.open()
    rect = fitz.Rect(0, 0, 595, 842) # A4 points
    pdf_page = pdf_doc.new_page(width=595, height=842)
    pdf_page.insert_image(rect, stream=img_byte_arr.getvalue())
    pdf_doc.save(filepath)
    pdf_doc.close()
    print(f"[OK] Scanned PDF (Citra Murni OCR) dibuat: {filepath}")


def create_sample_csv(filepath: str):
    """Membuat sampel data transaksi keuangan CSV (.csv)."""
    rows = [
        ["No_Transaksi", "Tanggal", "Kode_Akun", "Keterangan_Transaksi", "Penerima_Manfaat", "Debit_Rp", "Kredit_Rp", "Saldo_Rp"],
        ["TRX-2026-001", "2026-11-01", "5.1.01", "Pencairan Tahap I Dana BOS Afirmasi", "Bendahara Sekolah", 150000000, 0, 150000000],
        ["TRX-2026-002", "2026-11-04", "5.2.03", "Pembelian 2 Unit Server Modul ML-DSA", "PT DigiMeta Solusi", 0, 75000000, 75000000],
        ["TRX-2026-003", "2026-11-08", "5.2.04", "Pengadaan Token Kunci Fisik FIDO", "PT Cyber Kuantum", 0, 25000000, 50000000],
        ["TRX-2026-004", "2026-11-12", "5.3.01", "Honorarium Tim Verifikator Kuorum", "Panitia Khusus", 0, 15000000, 35000000],
        ["TRX-2026-005", "2026-11-15", "5.3.02", "Audit Sertifikasi Standar NIST FIPS 204", "Balai Sertifikasi Siber", 0, 20000000, 15000000],
    ]
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(rows)
    print(f"[OK] CSV Laporan Keuangan dibuat: {filepath}")


def create_sample_rtf(filepath: str):
    """Membuat naskah dinas Word RTF (.rtf)."""
    rtf_content = (
        r"{\rtf1\ansi\deff0"
        r"{\fonttbl{\f0\fswiss\fcharset0 Arial;}{\f1\froman\fcharset0 Times New Roman;}}"
        r"\viewkind4\uc1\pard\qc\f0\fs24\b SURAT EDARAN MENTERI PENDIDIKAN TINGGI\b0\par"
        r"Nomor: 12/SE/KEMENDIKTI/2026\par\par"
        r"\b TENTANG MIGRASI TANDA TANGAN DOKUMEN INSTITUSI MENUJU POST-QUANTUM ML-DSA\b0\par\par"
        r"\pard\ql\fs20 "
        r"Sehubungan dengan diterbitkannya standar resmi NIST FIPS 204 (ML-DSA), seluruh rektor, dekan, kepala sekolah, "
        r"dan pengelola anggaran pendidikan diwajibkan menerapkan skema tanda tangan ambang batas (k-dari-n) untuk menjamin "
        r"kedaulatan data dan mencegah pemalsuan dokumen resmi di era komputer kuantum.\par\par"
        r"Ditetapkan di Jakarta, 15 November 2026.\par"
        r"}"
    )
    with open(filepath, "w", encoding="ascii") as f:
        f.write(rtf_content)
    print(f"[OK] RTF Surat Edaran dibuat: {filepath}")


def create_sample_image_scan(filepath: str):
    """Membuat citra pindai fisik (.png) untuk uji OCR langsung."""
    width, height = 1000, 700
    img = Image.new("RGB", (width, height), color=(250, 250, 245))
    draw = ImageDraw.Draw(img)

    # Frame sertifikat
    draw.rectangle([30, 30, width - 30, height - 30], outline=(30, 60, 120), width=4)
    draw.rectangle([40, 40, width - 40, height - 40], outline=(190, 160, 80), width=2)

    draw.text((width // 2 - 200, 80), "SERTIFIKAT KELULUSAN UJI FORENSIK PQC", fill=(20, 40, 80))
    draw.text((width // 2 - 150, 120), "Nomor Registrasi: CERT-PQC-9921-2026", fill=(70, 80, 90))
    draw.line([(100, 160), (width - 100, 160)], fill=(190, 160, 80), width=2)

    draw.text((100, 220), "Diberikan Kepada : TIM SATUAN TUGAS PENGAWASAN DIGITAL", fill=(30, 30, 30))
    draw.text((100, 260), "Predikat         : LULUS DENGAN PUJIAN (VERIFIED 100%)", fill=(10, 120, 40))
    draw.text((100, 300), "Keahlian         : Pengesahan Dokumen Ambang Batas k-dari-n FIPS 204", fill=(30, 30, 30))
    draw.text((100, 340), "Metode Uji       : 15 Pengujian Model Ancaman & Audit Integritas AI", fill=(30, 30, 30))

    # Cap stempel bulat hijau
    cx, cy = width - 250, height - 200
    draw.ellipse([cx, cy, cx + 160, cy + 160], outline=(20, 140, 60), width=4)
    draw.text((cx + 25, cy + 50), "BADAN SERTIFIKASI", fill=(20, 140, 60))
    draw.text((cx + 35, cy + 80), "PQC INDONESIA", fill=(20, 140, 60))

    img.save(filepath, format="PNG")
    print(f"[OK] Citra Pindai Sertifikat PNG dibuat: {filepath}")


def generate_all_samples(samples_dir: str):
    """Menghasilkan seluruh paket dataset uji coba."""
    os.makedirs(samples_dir, exist_ok=True)
    
    create_sample_docx(os.path.join(samples_dir, "01_SK_Rektor_Kurikulum_PQC_2026.docx"))
    create_sample_xlsx(os.path.join(samples_dir, "02_RAB_Anggaran_BOS_Lab_PQC.xlsx"))
    create_sample_digital_pdf(os.path.join(samples_dir, "03_BAST_Pengadaan_Server_PQC.pdf"))
    create_sample_scanned_pdf(os.path.join(samples_dir, "04_Surat_Izin_Operasional_Scan.pdf"))
    create_sample_csv(os.path.join(samples_dir, "05_Laporan_Keuangan_Pengadaan.csv"))
    create_sample_rtf(os.path.join(samples_dir, "06_Surat_Edaran_Sosialisasi_Legacy.rtf"))
    create_sample_image_scan(os.path.join(samples_dir, "07_Ijazah_Sertifikat_Fisik_Scan.png"))

    print("\nSeluruh dataset sampel uji coba telah sukses dihasilkan di direktori:", samples_dir)


if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    target_dir = os.path.join(base_dir, "samples")
    generate_all_samples(target_dir)
