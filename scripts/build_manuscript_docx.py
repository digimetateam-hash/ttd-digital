#!/usr/bin/env python3
"""
build_manuscript_docx.py
Converts docs/MANUSCRIPT_SLREV.md to a publication-ready Microsoft Word (.docx) document
styled for Sriwijaya Law Review (SLRev) in APA 7th edition.
Outputs:
1. /Users/jevin/Downloads/ttd forensic/MANUSCRIPT_SLREV_POST_QUANTUM_LEGAL_POLICY.docx
2. /Users/jevin/Downloads/ttd forensic/repo_ttd_digital/docs/MANUSCRIPT_SLREV.docx
"""

import os
import re
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    """Set inner padding for table cell (in twips, 1 pt = 20 twips)."""
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{m}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def set_cell_background(cell, hex_color):
    """Set background color of a table cell."""
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>')
    tcPr.append(shd)

def set_cell_borders(cell, top="CCCCCC", bottom="CCCCCC", left=None, right=None, sz="4"):
    """Set borders on cell."""
    tcPr = cell._tc.get_or_add_tcPr()
    tcBorders = OxmlElement('w:tcBorders')
    
    borders = {'top': top, 'bottom': bottom, 'left': left, 'right': right}
    for border_name, color in borders.items():
        if color:
            b_elem = OxmlElement(f'w:{border_name}')
            b_elem.set(qn('w:val'), 'single')
            b_elem.set(qn('w:sz'), sz)
            b_elem.set(qn('w:space'), '0')
            b_elem.set(qn('w:color'), color)
            tcBorders.append(b_elem)
        else:
            b_elem = OxmlElement(f'w:{border_name}')
            b_elem.set(qn('w:val'), 'none')
            tcBorders.append(b_elem)
    tcPr.append(tcBorders)

def add_styled_paragraph(doc, text="", style=None, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=0, space_after=6, line_spacing=1.5, bold=False, italic=False, font_size=12, font_color=RGBColor(30, 41, 59)):
    p = doc.add_paragraph(style=style)
    p.alignment = align
    p.paragraph_format.space_before = Pt(space_before)
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.line_spacing = line_spacing
    
    if text:
        add_formatted_runs(p, text, default_bold=bold, default_italic=italic, default_size=font_size, default_color=font_color)
    return p

def add_formatted_runs(paragraph, text, default_bold=False, default_italic=False, default_size=12, default_color=RGBColor(30, 41, 59), font_name="Times New Roman"):
    """Parse inline markdown formatting (**bold**, *italic*, `code`, math $...$) into Word runs."""
    # Split text while preserving markdown tokens
    tokens = re.split(r'(\*\*[^*]+\*\*|\*[^*]+\*|`[^`]+`|\$[^$]+\$)', text)
    for token in tokens:
        if not token:
            continue
        run = paragraph.add_run()
        run.font.name = font_name
        run.font.size = Pt(default_size)
        run.font.color.rgb = default_color
        run.bold = default_bold
        run.italic = default_italic
        
        if token.startswith('**') and token.endswith('**') and len(token) >= 4:
            run.text = token[2:-2]
            run.bold = True
        elif token.startswith('*') and token.endswith('*') and len(token) >= 2:
            run.text = token[1:-1]
            run.italic = True
        elif token.startswith('`') and token.endswith('`') and len(token) >= 2:
            run.text = token[1:-1]
            run.font.name = "Courier New"
            run.font.size = Pt(default_size - 1)
            run.font.color.rgb = RGBColor(15, 23, 42)
        elif token.startswith('$') and token.endswith('$') and len(token) >= 2:
            # Inline math
            math_text = token[1:-1].replace(r'\text', '').replace(r'\bigwedge', '⋀').replace(r'\neq', '≠').replace(r'\implies', '⟹').replace(r'\le', '≤').replace('{', '').replace('}', '')
            run.text = math_text
            run.italic = True
            run.font.name = "Cambria Math"
        else:
            run.text = token

def create_manuscript_docx(input_md_path, output_docx_paths):
    doc = docx.Document()
    
    # Configure A4 page layout with 1-inch margins
    sections = doc.sections
    for section in sections:
        section.page_width = Inches(8.27)   # A4 width
        section.page_height = Inches(11.69) # A4 height
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(1.0)
        
        # Configure Header & Footer
        header = section.header
        hp = header.paragraphs[0]
        hp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        hrun = hp.add_run("Sriwijaya Law Review (SLRev) — Pre-Print Research Monograph | Legal Policy")
        hrun.font.name = "Times New Roman"
        hrun.font.size = Pt(8.5)
        hrun.font.italic = True
        hrun.font.color.rgb = RGBColor(100, 116, 139)
        
        footer = section.footer
        fp = footer.paragraphs[0]
        fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
        frun = fp.add_run("Post-Quantum Cryptography & Electronic Signature Legislation in Indonesia — ")
        frun.font.name = "Times New Roman"
        frun.font.size = Pt(8.5)
        frun.font.color.rgb = RGBColor(100, 116, 139)
        
        # Add Page Number field xml in footer
        f_p = fp._p
        f_run = OxmlElement('w:r')
        f_rPr = OxmlElement('w:rPr')
        f_rFont = OxmlElement('w:rFonts')
        f_rFont.set(qn('w:ascii'), 'Times New Roman')
        f_rPr.append(f_rFont)
        f_fld = OxmlElement('w:fldSimple')
        f_fld.set(qn('w:instr'), 'PAGE')
        f_run.append(f_rPr)
        f_run.append(f_fld)
        f_p.append(f_run)

    with open(input_md_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    in_abstract = False
    in_table_eval = False
    table_rows = []
    in_mermaid = False
    mermaid_type = ""
    mermaid_lines = []
    in_references = False
    current_ref_category = ""

    idx = 0
    while idx < len(lines):
        line = lines[idx].rstrip('\n')
        stripped = line.strip()

        # Handle Title
        if stripped.startswith('# '):
            title_text = stripped[2:]
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_before = Pt(12)
            p.paragraph_format.space_after = Pt(14)
            p.paragraph_format.line_spacing = 1.2
            add_formatted_runs(p, title_text, default_bold=True, default_size=15, default_color=RGBColor(15, 23, 42))
            idx += 1
            continue

        # Handle Metadata Box (Authors, Target Journal, Category, Length, Style)
        if stripped.startswith('**Authors:**'):
            meta_box = doc.add_table(rows=1, cols=1)
            meta_box.alignment = WD_TABLE_ALIGNMENT.CENTER
            cell = meta_box.rows[0].cells[0]
            cell.width = Inches(6.27)
            set_cell_background(cell, "F8FAFC")
            set_cell_borders(cell, top="CBD5E1", bottom="CBD5E1", left="CBD5E1", right="CBD5E1", sz="6")
            set_cell_margins(cell, top=140, bottom=140, left=200, right=200)
            
            cp = cell.paragraphs[0]
            cp.alignment = WD_ALIGN_PARAGRAPH.CENTER
            cp.paragraph_format.space_after = Pt(3)
            cp.paragraph_format.line_spacing = 1.15
            add_formatted_runs(cp, stripped, default_size=10, default_color=RGBColor(30, 41, 59))
            
            # Read subsequent metadata lines
            while idx + 1 < len(lines) and (lines[idx+1].strip().startswith('**') or lines[idx+1].strip() == ''):
                idx += 1
                nxt = lines[idx].strip()
                if nxt.startswith('**'):
                    p2 = cell.add_paragraph()
                    p2.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    p2.paragraph_format.space_after = Pt(3)
                    p2.paragraph_format.line_spacing = 1.15
                    add_formatted_runs(p2, nxt, default_size=10, default_color=RGBColor(30, 41, 59))
            
            # Add small gap after metadata box
            gap = doc.add_paragraph()
            gap.paragraph_format.space_before = Pt(0)
            gap.paragraph_format.space_after = Pt(10)
            idx += 1
            continue

        # Handle Horizontal Rules
        if stripped in ('---', '***', '___'):
            idx += 1
            continue

        # Handle Heading 2 (e.g. ## 1. INTRODUCTION)
        if stripped.startswith('## '):
            h_text = stripped[3:].strip()
            if "REFERENCES" in h_text:
                in_references = True
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            p.paragraph_format.space_before = Pt(16)
            p.paragraph_format.space_after = Pt(6)
            p.paragraph_format.keep_with_next = True
            add_formatted_runs(p, h_text, default_bold=True, default_size=12.5, default_color=RGBColor(15, 23, 42))
            idx += 1
            continue

        # Handle Heading 3 (e.g. ### Abstract, ### 2.1 Research Approaches)
        if stripped.startswith('### '):
            h_text = stripped[4:].strip()
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            p.paragraph_format.space_before = Pt(12)
            p.paragraph_format.space_after = Pt(4)
            p.paragraph_format.keep_with_next = True
            
            if h_text.lower() == 'abstract':
                in_abstract = True
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                add_formatted_runs(p, "ABSTRACT", default_bold=True, default_size=11, default_color=RGBColor(15, 23, 42))
            elif in_references:
                add_formatted_runs(p, h_text, default_bold=True, default_italic=True, default_size=11, default_color=RGBColor(51, 65, 85))
            else:
                add_formatted_runs(p, h_text, default_bold=True, default_size=11.5, default_color=RGBColor(30, 41, 59))
            idx += 1
            continue

        # Handle Heading 4 (e.g. #### 3.3.1 The United States Paradigm)
        if stripped.startswith('#### '):
            h_text = stripped[5:].strip()
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            p.paragraph_format.space_before = Pt(10)
            p.paragraph_format.space_after = Pt(4)
            p.paragraph_format.keep_with_next = True
            add_formatted_runs(p, h_text, default_bold=True, default_italic=True, default_size=11, default_color=RGBColor(30, 41, 59))
            idx += 1
            continue

        # Handle Keywords
        if stripped.startswith('**Keywords:**'):
            in_abstract = False
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            p.paragraph_format.left_indent = Inches(0.4)
            p.paragraph_format.right_indent = Inches(0.4)
            p.paragraph_format.space_before = Pt(6)
            p.paragraph_format.space_after = Pt(14)
            p.paragraph_format.line_spacing = 1.15
            add_formatted_runs(p, stripped, default_size=10, default_color=RGBColor(51, 65, 85))
            idx += 1
            continue

        # Handle Display Math Equations ($$...$$)
        if stripped.startswith('$$') and stripped.endswith('$$') and len(stripped) >= 4:
            eq_text = stripped[2:-2].strip()
            # Clean LaTeX macros for clean rendering
            eq_clean = eq_text.replace(r'\text', '').replace(r'\bigwedge', '⋀').replace(r'\neq', '≠').replace(r'\implies', ' ⟹ ').replace(r'\mathcal{O}', 'O').replace(r'\left', '').replace(r'\right', '').replace(r'\exp', 'exp').replace(r'\sqrt', '√').replace(r'\,\|\,', ' || ').replace('{', '').replace('}', '')
            
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_before = Pt(8)
            p.paragraph_format.space_after = Pt(8)
            p.paragraph_format.line_spacing = 1.15
            
            run = p.add_run(eq_clean)
            run.font.name = "Cambria Math"
            run.font.size = Pt(11.5)
            run.italic = True
            run.font.color.rgb = RGBColor(15, 23, 42)
            idx += 1
            continue

        # Handle Mermaid Diagrams: Convert into structured visual diagram boxes in Word
        if stripped.startswith('```mermaid'):
            in_mermaid = True
            mermaid_lines = []
            idx += 1
            while idx < len(lines) and not lines[idx].strip().startswith('```'):
                mermaid_lines.append(lines[idx].rstrip('\n'))
                idx += 1
            idx += 1  # Skip closing ```
            
            # Render Diagram Box
            dia_table = doc.add_table(rows=1, cols=1)
            dia_table.alignment = WD_TABLE_ALIGNMENT.CENTER
            cell = dia_table.rows[0].cells[0]
            cell.width = Inches(6.27)
            set_cell_background(cell, "F1F5F9")
            set_cell_borders(cell, top="0284C7", bottom="0284C7", left="0284C7", right="0284C7", sz="8")
            set_cell_margins(cell, top=140, bottom=140, left=180, right=180)
            
            # Diagram title run
            dp0 = cell.paragraphs[0]
            dp0.alignment = WD_ALIGN_PARAGRAPH.LEFT
            dp0.paragraph_format.space_after = Pt(4)
            dtitle_run = dp0.add_run("DIAGRAM TEKNIS & ALIR YURIDIS (ARCHITECTURAL MODEL)")
            dtitle_run.bold = True
            dtitle_run.font.name = "Times New Roman"
            dtitle_run.font.size = Pt(9.5)
            dtitle_run.font.color.rgb = RGBColor(3, 105, 161)
            
            # Diagram content
            full_mermaid_text = "\n".join(mermaid_lines)
            
            # Format clean textual flowchart
            p_content = cell.add_paragraph()
            p_content.alignment = WD_ALIGN_PARAGRAPH.LEFT
            p_content.paragraph_format.line_spacing = 1.05
            p_content.paragraph_format.space_after = Pt(0)
            
            c_run = p_content.add_run(full_mermaid_text)
            c_run.font.name = "Courier New"
            c_run.font.size = Pt(8.5)
            c_run.font.color.rgb = RGBColor(15, 23, 42)
            
            # Spacing after diagram
            post_dia = doc.add_paragraph()
            post_dia.paragraph_format.space_before = Pt(2)
            post_dia.paragraph_format.space_after = Pt(8)
            continue

        # Handle Preformatted Table Evaluation Block
        if stripped.startswith('```') and idx + 1 < len(lines) and 'TABEL 1' in lines[idx+1]:
            in_table_eval = True
            table_lines = []
            idx += 1
            while idx < len(lines) and not lines[idx].strip().startswith('```'):
                table_lines.append(lines[idx].rstrip('\n'))
                idx += 1
            idx += 1 # skip closing ```
            
            # Build genuine Word Table from evaluation table data
            # Table data:
            # Col headers: No | Berkas Sampel Dokumen | Format | Ukuran (KB) | Parsing (ms) | Sign (ms) | Verify (ms) | Tamper Check | Hasil Pengesahan
            eval_data = [
                ["1", "SK Rektor Kurikulum 2026", "Word (.docx)", "37.00", "5.94", "0.42", "0.49", "Ditolak Mutlak (Pass)", "Sah (Valid)"],
                ["2", "RAB Anggaran Lab PQC", "Excel (.xlsx)", "6.63", "23.25", "0.26", "0.50", "Ditolak Mutlak (Pass)", "Sah (Valid)"],
                ["3", "BAST Pengadaan Server PQC", "Digital PDF", "3.08", "778.29*", "0.36", "0.52", "Ditolak Mutlak (Pass)", "Sah (Valid)"],
                ["4", "Surat Izin Operasional Scan", "Scanned PDF", "105.62", "526.95*", "0.42", "0.50", "Ditolak Mutlak (Pass)", "Sah (Valid)"],
                ["5", "Laporan Transaksi Keuangan", "CSV Tabel", "0.62", "6.12", "0.27", "0.49", "Ditolak Mutlak (Pass)", "Sah (Valid)"],
                ["6", "Surat Edaran Sosialisasi RTF", "Word RTF", "0.65", "0.24", "0.23", "0.47", "Ditolak Mutlak (Pass)", "Sah (Valid)"],
                ["7", "Sertifikat Kelulusan Fisik", "Citra PNG", "20.72", "241.26*", "0.38", "0.53", "Ditolak Mutlak (Pass)", "Sah (Valid)"]
            ]
            
            # Add Table Caption
            tp = doc.add_paragraph()
            tp.alignment = WD_ALIGN_PARAGRAPH.CENTER
            tp.paragraph_format.space_before = Pt(8)
            tp.paragraph_format.space_after = Pt(4)
            trun = tp.add_run("Tabel 1: Hasil Evaluasi Forensik Empiris Dataset Dokumen Resmi Multi-Format (NIST FIPS 204)")
            trun.bold = True
            trun.font.name = "Times New Roman"
            trun.font.size = Pt(10.5)
            trun.font.color.rgb = RGBColor(15, 23, 42)
            
            headers = ["No", "Berkas Sampel Dokumen", "Format", "Ukuran", "Parsing", "Sign", "Verify", "Tamper Check", "Pengesahan"]
            col_widths = [Inches(0.35), Inches(1.85), Inches(0.85), Inches(0.55), Inches(0.65), Inches(0.50), Inches(0.50), Inches(1.05), Inches(0.70)]
            
            tbl = doc.add_table(rows=len(eval_data) + 1, cols=9)
            tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
            
            # Header row
            hdr_cells = tbl.rows[0].cells
            for col_i, h_text in enumerate(headers):
                hdr_cells[col_i].width = col_widths[col_i]
                set_cell_background(hdr_cells[col_i], "1E293B")
                set_cell_margins(hdr_cells[col_i], top=100, bottom=100, left=60, right=60)
                set_cell_borders(hdr_cells[col_i], top="0F172A", bottom="0F172A", left="334155", right="334155")
                hp = hdr_cells[col_i].paragraphs[0]
                hp.alignment = WD_ALIGN_PARAGRAPH.CENTER
                hr = hp.add_run(h_text)
                hr.bold = True
                hr.font.name = "Times New Roman"
                hr.font.size = Pt(8.5)
                hr.font.color.rgb = RGBColor(255, 255, 255)
            
            # Data rows
            for row_i, row_vals in enumerate(eval_data):
                row_cells = tbl.rows[row_i + 1].cells
                bg_color = "FFFFFF" if row_i % 2 == 0 else "F8FAFC"
                for col_i, val in enumerate(row_vals):
                    row_cells[col_i].width = col_widths[col_i]
                    set_cell_background(row_cells[col_i], bg_color)
                    set_cell_margins(row_cells[col_i], top=80, bottom=80, left=60, right=60)
                    set_cell_borders(row_cells[col_i], top="E2E8F0", bottom="E2E8F0", left="E2E8F0", right="E2E8F0")
                    cp = row_cells[col_i].paragraphs[0]
                    cp.alignment = WD_ALIGN_PARAGRAPH.LEFT if col_i == 1 else WD_ALIGN_PARAGRAPH.CENTER
                    cr = cp.add_run(val)
                    cr.font.name = "Times New Roman"
                    cr.font.size = Pt(8.0)
                    if "Sah" in val or "Pass" in val:
                        cr.font.color.rgb = RGBColor(22, 101, 52)
                        cr.bold = True
                    else:
                        cr.font.color.rgb = RGBColor(30, 41, 59)
            
            # Table Note
            np = doc.add_paragraph()
            np.alignment = WD_ALIGN_PARAGRAPH.LEFT
            np.paragraph_format.space_before = Pt(3)
            np.paragraph_format.space_after = Pt(8)
            nrun = np.add_run("*Catatan: Durasi pemrosesan mencakup perenderan citra resolusi tinggi dan pengenalan karakter optis Tesseract OCR 5.5 multi-bahasa (ind+eng).")
            nrun.font.name = "Times New Roman"
            nrun.font.size = Pt(8.5)
            nrun.italic = True
            nrun.font.color.rgb = RGBColor(100, 116, 139)
            continue

        # Handle References entries (Lines starting with '* ')
        if in_references and stripped.startswith('* '):
            ref_entry = stripped[2:].strip()
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            p.paragraph_format.left_indent = Inches(0.5)
            p.paragraph_format.first_line_indent = Inches(-0.5)  # APA 7th Hanging Indent!
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(5)
            p.paragraph_format.line_spacing = 1.15
            add_formatted_runs(p, ref_entry, default_size=10.5, default_color=RGBColor(15, 23, 42))
            idx += 1
            continue

        # Handle Bulleted Lists (Non-reference)
        if stripped.startswith('* ') or stripped.startswith('- '):
            list_text = stripped[2:].strip()
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            p.paragraph_format.left_indent = Inches(0.35)
            p.paragraph_format.first_line_indent = Inches(-0.2)
            p.paragraph_format.space_before = Pt(1)
            p.paragraph_format.space_after = Pt(3)
            p.paragraph_format.line_spacing = 1.35
            
            bullet_run = p.add_run("•  ")
            bullet_run.font.name = "Times New Roman"
            bullet_run.font.size = Pt(11)
            bullet_run.bold = True
            add_formatted_runs(p, list_text, default_size=11.5, default_color=RGBColor(30, 41, 59))
            idx += 1
            continue

        # Handle Numbered Lists
        num_match = re.match(r'^(\d+)\.\s+(.*)', stripped)
        if num_match:
            num_str = num_match.group(1)
            item_text = num_match.group(2)
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            p.paragraph_format.left_indent = Inches(0.4)
            p.paragraph_format.first_line_indent = Inches(-0.25)
            p.paragraph_format.space_before = Pt(2)
            p.paragraph_format.space_after = Pt(4)
            p.paragraph_format.line_spacing = 1.35
            
            num_run = p.add_run(f"{num_str}. ")
            num_run.font.name = "Times New Roman"
            num_run.font.size = Pt(11.5)
            num_run.bold = True
            add_formatted_runs(p, item_text, default_size=11.5, default_color=RGBColor(30, 41, 59))
            idx += 1
            continue

        # Handle Abstract Body
        if in_abstract and stripped:
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            p.paragraph_format.left_indent = Inches(0.4)
            p.paragraph_format.right_indent = Inches(0.4)
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(6)
            p.paragraph_format.line_spacing = 1.15
            add_formatted_runs(p, stripped, default_italic=True, default_size=10, default_color=RGBColor(30, 41, 59))
            idx += 1
            continue

        # Handle Regular Paragraphs
        if stripped:
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(6)
            p.paragraph_format.line_spacing = 1.5
            p.paragraph_format.first_line_indent = Inches(0.35)
            add_formatted_runs(p, stripped, default_size=12, default_color=RGBColor(15, 23, 42))

        idx += 1

    # Save outputs to all target locations
    for out_path in output_docx_paths:
        os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
        doc.save(out_path)
        print(f"[SUCCESS] Saved Word manuscript to: {out_path}")

if __name__ == "__main__":
    src_md = "/Users/jevin/Downloads/ttd forensic/repo_ttd_digital/docs/MANUSCRIPT_SLREV.md"
    targets = [
        "/Users/jevin/Downloads/ttd forensic/MANUSCRIPT_SLREV_POST_QUANTUM_LEGAL_POLICY.docx",
        "/Users/jevin/Downloads/ttd forensic/repo_ttd_digital/docs/MANUSCRIPT_SLREV.docx"
    ]
    create_manuscript_docx(src_md, targets)
