"""cert_generator.py - Modul Pembuat Sertifikat Pengesahan Dokumen Kolektif (Certificate of Authenticity).
Menerbitkan Sertifikat PDF Resmi jika dan hanya jika tanda tangan threshold ML-DSA FIPS 204 berstatus VALID.
"""
from __future__ import annotations
import io
import time
import uuid
from datetime import datetime

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER, TA_LEFT
except ImportError:
    pass

def generate_signing_certificate_pdf(
    doc_id: str,
    doc_title: str,
    file_sha3: str,
    bound_digest: str,
    k_threshold: int,
    total_n: int,
    signers: list[str],
    algorithm: str = "ML-DSA-65 (NIST FIPS 204)",
    is_valid: bool = True
) -> bytes | None:
    """Menghasilkan berkas PDF Sertifikat Pengesahan jika dokumen terbukti valid."""
    if not is_valid:
        return None
        
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )
    
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CertTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#0F2F6B')
    )
    
    subtitle_style = ParagraphStyle(
        'CertSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=11,
        leading=14,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#0D9488')
    )
    
    section_style = ParagraphStyle(
        'SectionHead',
        parent=styles['Heading3'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor('#1E3A8A'),
        spaceAfter=6
    )
    
    body_style = ParagraphStyle(
        'CertBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=13,
        textColor=colors.HexColor('#1E293B')
    )
    
    code_style = ParagraphStyle(
        'CertCode',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=8,
        leading=10,
        textColor=colors.HexColor('#0F172A')
    )
    
    elements = []
    
    # 1. Header & Logo Title
    elements.append(Paragraph("SERTIFIKAT PENGESAHAN DOKUMEN DIGITAL", title_style))
    elements.append(Paragraph("CERTIFICATE OF THRESHOLD POST-QUANTUM SIGNING (NIST FIPS 204)", subtitle_style))
    elements.append(Spacer(1, 15))
    elements.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#1A56DB'), spaceAfter=15))
    
    # 2. Metadata Sertifikat
    cert_id = str(uuid.uuid4()).upper()
    issue_date = datetime.now().strftime("%d %B %Y, %H:%M:%S WIB")
    
    meta_table_data = [
        [Paragraph("<b>Nomor Sertifikat (UUID):</b>", body_style), Paragraph(cert_id, code_style)],
        [Paragraph("<b>Waktu Penerbitan:</b>", body_style), Paragraph(issue_date, body_style)],
        [Paragraph("<b>Status Verifikasi:</b>", body_style), Paragraph("<b>SAH & TERVERIFIKASI PENUH (FIPS 204 VALID)</b>", ParagraphStyle('Valid', parent=body_style, textColor=colors.HexColor('#059669')))]
    ]
    t_meta = Table(meta_table_data, colWidths=[160, 350])
    t_meta.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8FAFC')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#CBD5E1')),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))
    elements.append(t_meta)
    elements.append(Spacer(1, 15))
    
    # 3. Rincian Dokumen Resmi
    elements.append(Paragraph("1. IDENTITAS DOKUMEN RESMI", section_style))
    doc_table_data = [
        [Paragraph("<b>ID / Nomor Dokumen:</b>", body_style), Paragraph(doc_id, body_style)],
        [Paragraph("<b>Judul / Nama Berkas:</b>", body_style), Paragraph(doc_title, body_style)],
        [Paragraph("<b>Hash Biner SHA3-256:</b>", body_style), Paragraph(file_sha3, code_style)],
        [Paragraph("<b>Digest Pengikat THRESHDOC-v0:</b>", body_style), Paragraph(bound_digest, code_style)]
    ]
    t_doc = Table(doc_table_data, colWidths=[160, 350])
    t_doc.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#E2E8F0')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#F1F5F9')),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
    ]))
    elements.append(t_doc)
    elements.append(Spacer(1, 15))
    
    # 4. Pembuktian Kuorum & Kriptografi
    elements.append(Paragraph("2. PEMBUKTIAN KUORUM & KRIPTOGRAFI PASCA-KUANTUM", section_style))
    crypto_table_data = [
        [Paragraph("<b>Algoritma Standar:</b>", body_style), Paragraph(algorithm, body_style)],
        [Paragraph("<b>Aturan Kuorum:</b>", body_style), Paragraph(f"Minimal {k_threshold} dari total {total_n} penanda tangan berwenang", body_style)],
        [Paragraph("<b>Daftar Pejabat Penyetuju:</b>", body_style), Paragraph(", ".join(signers), body_style)],
        [Paragraph("<b>Prinsip Kunci (Non-Escrow):</b>", body_style), Paragraph("Kunci privat tidak pernah disatukan; tanda tangan digabung dari share independen.", body_style)]
    ]
    t_crypto = Table(crypto_table_data, colWidths=[160, 350])
    t_crypto.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#E2E8F0')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#F1F5F9')),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
    ]))
    elements.append(t_crypto)
    elements.append(Spacer(1, 20))
    
    # 5. Klausul Pernyataan Hukum & Segel
    footer_text = (
        "Sertifikat ini diterbitkan secara otomatis oleh sistem TTD-Digital berdasarkan pembuktian matematis skema "
        "ambang batas k-dari-n FIPS 204. Dokumen asli terikat permanen pada digest di atas dan kebal terhadap pemalsuan "
        "oleh komputer kuantum. Setiap modifikasi satu bit pada berkas asli membatalkan keabsahan sertifikat ini."
    )
    elements.append(Paragraph(footer_text, ParagraphStyle('Footer', parent=body_style, fontSize=8, leading=11, textColor=colors.HexColor('#64748B'))))
    
    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()

