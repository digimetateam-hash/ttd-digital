"""
Modul Analisis Dokumen Multi-Format & Mesin OCR Forensik
Mendukung:
- Semua varian Word: .docx, .doc (legacy 97-2003 OLE2), .docm, .dotx, .dotm, .rtf, .odt
- Semua varian Excel: .xlsx, .xls (legacy BIFF8), .xlsm, .xltx, .xltm, .csv, .tsv, .ods
- Semua varian PDF: Digital/Searchable, Scanned (Citra Hasil Pindai), Hybrid, Terenkripsi/Metadata
- Citra Dokumen Pindai Mandiri: .png, .jpg, .jpeg, .tiff, .bmp, .webp via Tesseract OCR
"""

import io
import os
import re
import shutil
import hashlib
import subprocess
import zipfile
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
import pandas as pd

# Opsional / deteksi library
try:
    import docx
except ImportError:
    docx = None

try:
    import openpyxl
except ImportError:
    openpyxl = None

try:
    import xlrd
except ImportError:
    xlrd = None

try:
    import olefile
except ImportError:
    olefile = None

try:
    import pymupdf as fitz
except ImportError:
    try:
        import fitz
    except ImportError:
        fitz = None

try:
    import pypdf
except ImportError:
    pypdf = None

try:
    from PIL import Image
except ImportError:
    Image = None


SUPPORTED_WORD_EXTENSIONS = ["docx", "doc", "docm", "dotx", "dotm", "rtf", "odt"]
SUPPORTED_EXCEL_EXTENSIONS = ["xlsx", "xls", "xlsm", "xltx", "xltm", "csv", "tsv", "ods"]
SUPPORTED_PDF_EXTENSIONS = ["pdf"]
SUPPORTED_IMAGE_EXTENSIONS = ["png", "jpg", "jpeg", "tiff", "tif", "bmp", "webp"]

ALL_SUPPORTED_EXTENSIONS = (
    SUPPORTED_WORD_EXTENSIONS +
    SUPPORTED_EXCEL_EXTENSIONS +
    SUPPORTED_PDF_EXTENSIONS +
    SUPPORTED_IMAGE_EXTENSIONS
)


@dataclass
class DocumentAnalysisResult:
    doc_type: str                   # 'Word', 'Excel', 'PDF', 'Image', 'Text', 'Unknown'
    filename: str
    extension: str
    file_size_bytes: int
    sha3_256: str
    sha256: str
    title: str = ""
    author: str = ""
    created_at: str = ""
    modified_at: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    extracted_text: str = ""
    summary_stats: Dict[str, Any] = field(default_factory=dict)
    excel_sheets: Dict[str, pd.DataFrame] = field(default_factory=dict)
    is_scanned_pdf: bool = False
    ocr_performed: bool = False
    ocr_engine: str = ""
    ocr_text: str = ""
    page_count: int = 1
    warnings: List[str] = field(default_factory=list)
    error_message: Optional[str] = None


def get_tesseract_binary_path() -> Optional[str]:
    """Mencari path eksekusi binary tesseract di sistem."""
    locations = [
        shutil.which("tesseract"),
        "/opt/homebrew/bin/tesseract",
        "/usr/local/bin/tesseract",
        "/usr/bin/tesseract",
        "/bin/tesseract",
        os.environ.get("TESSERACT_PATH"),
    ]
    for loc in locations:
        if loc and os.path.exists(loc) and os.access(loc, os.X_OK):
            return loc
    return None


def run_tesseract_ocr(image_bytes: bytes, lang: str = "ind+eng") -> Tuple[str, Optional[str]]:
    """Menjalankan Tesseract OCR pada citra biner."""
    tess_bin = get_tesseract_binary_path()
    if not tess_bin:
        return "", "Mesin Tesseract OCR tidak ditemukan di sistem host. Pastikan tesseract telah terpasang."

    try:
        # Jalankan tesseract membaca dari stdin, menulis ke stdout
        cmd = [tess_bin, "stdin", "stdout", "-l", lang, "--psm", "3"]
        proc = subprocess.run(cmd, input=image_bytes, capture_output=True, timeout=30)
        if proc.returncode == 0:
            text = proc.stdout.decode("utf-8", errors="replace").strip()
            return text, None
        else:
            err = proc.stderr.decode("utf-8", errors="replace").strip()
            return "", f"Tesseract error (kode {proc.returncode}): {err}"
    except subprocess.TimeoutExpired:
        return "", "Tesseract OCR waktu habis (timeout > 30 detik)."
    except Exception as e:
        return "", f"Gagal menjalankan OCR: {str(e)}"


def _extract_strings_from_bytes(raw_bytes: bytes, min_len: int = 4) -> str:
    """Ekstraksi teks berbasis string (ASCII & UTF-16LE) dari berkas biner."""
    ascii_re = re.compile(rb"[\x20-\x7E\r\n\t]{" + str(min_len).encode() + rb",}")
    utf16_re = re.compile(rb"(?:[\x20-\x7E\r\n\t]\x00){" + str(min_len).encode() + rb",}")

    extracted_parts = []
    for match in ascii_re.finditer(raw_bytes):
        try:
            s = match.group().decode("ascii").strip()
            if len(s) >= min_len and not re.match(r"^[\W_]+$", s):
                extracted_parts.append(s)
        except Exception:
            pass

    for match in utf16_re.finditer(raw_bytes):
        try:
            s = match.group().decode("utf-16le").strip()
            if len(s) >= min_len and not re.match(r"^[\W_]+$", s):
                extracted_parts.append(s)
        except Exception:
            pass

    return "\n".join(extracted_parts[:500])


def _strip_rtf(rtf_text: str) -> str:
    """Membersihkan sintaks Rich Text Format (RTF) menjadi plain text."""
    # Hilangkan kontrol grup
    pattern = re.compile(r"[\{\}\\]|\\([a-z]{1,32})(-?\d+)? ?|\\\'([0-9a-fA-F]{2})|\\u(-?\d+)\??", re.IGNORECASE)
    out = []
    i = 0
    text_len = len(rtf_text)
    while i < text_len:
        match = pattern.search(rtf_text, i)
        if not match:
            out.append(rtf_text[i:])
            break
        out.append(rtf_text[i:match.start()])
        # Handle unicode escape
        if match.group(4):
            val = int(match.group(4))
            if val < 0:
                val += 65536
            out.append(chr(val))
        elif match.group(3):
            try:
                byte_val = bytes.fromhex(match.group(3))
                out.append(byte_val.decode("latin1"))
            except Exception:
                pass
        i = match.end()
    cleaned = "".join(out)
    return re.sub(r"\n{3,}", "\n\n", cleaned).strip()


def parse_word_document(file_bytes: bytes, ext: str) -> DocumentAnalysisResult:
    """Menganalisis semua jenis dokumen Word (.docx, .doc, .docm, .dotx, .rtf, .odt)."""
    res = DocumentAnalysisResult(
        doc_type="Word",
        filename="",
        extension=ext,
        file_size_bytes=len(file_bytes),
        sha3_256=hashlib.sha3_256(file_bytes).hexdigest(),
        sha256=hashlib.sha256(file_bytes).hexdigest()
    )

    if ext in ["docx", "docm", "dotx", "dotm"]:
        if docx is None:
            res.warnings.append("Pustaka python-docx tidak terpasang. Teks diekstrak melalui pembacaan kontainer zip.")
            try:
                with zipfile.ZipFile(io.BytesIO(file_bytes)) as z:
                    xml_content = z.read("word/document.xml")
                    tree = ET.fromstring(xml_content)
                    texts = [node.text for node in tree.iter() if node.text]
                    res.extracted_text = " ".join(texts)
            except Exception as e:
                res.extracted_text = _extract_strings_from_bytes(file_bytes)
        else:
            try:
                doc_obj = docx.Document(io.BytesIO(file_bytes))
                paragraphs = [p.text for p in doc_obj.paragraphs if p.text.strip()]
                res.extracted_text = "\n\n".join(paragraphs)
                
                # Ekstrak teks tabel jika ada
                table_texts = []
                for table in doc_obj.tables:
                    for row in table.rows:
                        row_data = [cell.text.strip() for cell in row.cells if cell.text.strip()]
                        if row_data:
                            table_texts.append(" | ".join(row_data))
                if table_texts:
                    res.extracted_text += "\n\n[Tabel Dokumen]\n" + "\n".join(table_texts[:30])

                # Metadata dari core properties
                core_props = doc_obj.core_properties
                res.title = core_props.title or ""
                res.author = core_props.author or ""
                res.created_at = str(core_props.created) if core_props.created else ""
                res.modified_at = str(core_props.modified) if core_props.modified else ""
                res.metadata = {
                    "category": core_props.category or "",
                    "comments": core_props.comments or "",
                    "subject": core_props.subject or "",
                    "revision": core_props.revision or 1,
                }
                res.summary_stats = {
                    "paragraf": len(doc_obj.paragraphs),
                    "tabel": len(doc_obj.tables),
                    "kata": len(res.extracted_text.split()),
                    "karakter": len(res.extracted_text)
                }
            except Exception as e:
                res.warnings.append(f"Gagal membaca via python-docx: {e}. Menggunakan parser biner cadangan.")
                res.extracted_text = _extract_strings_from_bytes(file_bytes)

    elif ext == "doc":
        # Legacy Word 97-2003 (Compound File Binary Format / OLE2)
        extracted = False
        if olefile and olefile.isOleFile(io.BytesIO(file_bytes)):
            try:
                ole = olefile.OleFileIO(io.BytesIO(file_bytes))
                res.metadata["ole_format"] = "Microsoft Word 97-2003 OLE2"
                
                # Baca SummaryInformation jika ada
                if ole.exists("\x05SummaryInformation"):
                    meta = ole.get_metadata()
                    res.title = meta.title or ""
                    res.author = meta.author or ""
                    res.created_at = str(meta.create_time) if meta.create_time else ""
                    res.modified_at = str(meta.last_saved_time) if meta.last_saved_time else ""
                    res.metadata["last_saved_by"] = meta.last_saved_by or ""
                    res.metadata["total_edit_time"] = meta.total_edit_time or 0
                
                if ole.exists("WordDocument"):
                    word_stream = ole.openstream("WordDocument").read()
                    res.extracted_text = _extract_strings_from_bytes(word_stream)
                    extracted = True
                ole.close()
            except Exception as e:
                res.warnings.append(f"Peringatan parsing OLE2 Word: {e}")

        if not extracted or not res.extracted_text.strip():
            res.extracted_text = _extract_strings_from_bytes(file_bytes)
            res.warnings.append("Dokumen Word versi lama (97-2003) dibaca via ekstraksi string biner.")
            
        res.summary_stats = {
            "format": "Legacy Word 97-2003 (.doc)",
            "kata": len(res.extracted_text.split()),
            "karakter": len(res.extracted_text)
        }

    elif ext == "rtf":
        try:
            raw_text = file_bytes.decode("utf-8", errors="replace")
            res.extracted_text = _strip_rtf(raw_text)
            res.summary_stats = {
                "format": "Rich Text Format (.rtf)",
                "kata": len(res.extracted_text.split()),
                "karakter": len(res.extracted_text)
            }
        except Exception as e:
            res.extracted_text = _extract_strings_from_bytes(file_bytes)
            res.warnings.append(f"Peringatan parsing RTF: {e}")

    elif ext == "odt":
        try:
            with zipfile.ZipFile(io.BytesIO(file_bytes)) as z:
                xml_data = z.read("content.xml")
                root = ET.fromstring(xml_data)
                texts = []
                for elem in root.iter():
                    if elem.tag.endswith("p") or elem.tag.endswith("h"):
                        t = "".join(elem.itertext()).strip()
                        if t:
                            texts.append(t)
                res.extracted_text = "\n\n".join(texts)
                res.summary_stats = {
                    "format": "OpenDocument Text (.odt)",
                    "paragraf": len(texts),
                    "kata": len(res.extracted_text.split()),
                    "karakter": len(res.extracted_text)
                }
        except Exception as e:
            res.extracted_text = _extract_strings_from_bytes(file_bytes)
            res.warnings.append(f"Gagal membaca kontainer ODT: {e}")

    return res


def parse_excel_document(file_bytes: bytes, ext: str) -> DocumentAnalysisResult:
    """Menganalisis semua jenis dokumen Excel (.xlsx, .xls, .xlsm, .xltx, .csv, .tsv, .ods)."""
    res = DocumentAnalysisResult(
        doc_type="Excel",
        filename="",
        extension=ext,
        file_size_bytes=len(file_bytes),
        sha3_256=hashlib.sha3_256(file_bytes).hexdigest(),
        sha256=hashlib.sha256(file_bytes).hexdigest()
    )

    if ext in ["xlsx", "xlsm", "xltx", "xltm"]:
        if openpyxl is not None:
            try:
                wb = openpyxl.load_workbook(io.BytesIO(file_bytes), data_only=True)
                sheet_names = wb.sheetnames
                res.metadata["sheet_names"] = sheet_names
                
                # Metadata dokumen Excel
                props = wb.properties
                if props:
                    res.title = props.title or ""
                    res.author = props.creator or ""
                    res.created_at = str(props.created) if props.created else ""
                    res.modified_at = str(props.modified) if props.modified else ""

                total_rows = 0
                total_cols = 0
                text_snippets = []

                for sheet in sheet_names:
                    try:
                        df = pd.read_excel(io.BytesIO(file_bytes), sheet_name=sheet)
                        res.excel_sheets[sheet] = df
                        total_rows += len(df)
                        total_cols = max(total_cols, len(df.columns))
                        # Buat representasi teks untuk AI audit
                        snippet = f"--- Lembar Kerja: {sheet} ({len(df)} baris x {len(df.columns)} kolom) ---\n"
                        snippet += df.head(10).to_string()
                        text_snippets.append(snippet)
                    except Exception as e_sheet:
                        res.warnings.append(f"Gagal membaca sheet '{sheet}': {e_sheet}")

                res.extracted_text = "\n\n".join(text_snippets)
                res.summary_stats = {
                    "total_sheets": len(sheet_names),
                    "sheet_names": sheet_names,
                    "total_rows_approx": total_rows,
                    "max_columns": total_cols,
                }
            except Exception as e:
                res.warnings.append(f"Gagal membaca workbook openpyxl: {e}")
                res.extracted_text = _extract_strings_from_bytes(file_bytes)
        else:
            res.warnings.append("openpyxl tidak tersedia.")

    elif ext == "xls":
        # Legacy Excel 97-2003 BIFF8
        try:
            excel_file = pd.ExcelFile(io.BytesIO(file_bytes), engine="xlrd")
            sheet_names = excel_file.sheet_names
            res.metadata["sheet_names"] = sheet_names
            res.metadata["format"] = "Legacy Excel 97-2003 (.xls)"
            
            text_snippets = []
            for sheet in sheet_names:
                df = pd.read_excel(excel_file, sheet_name=sheet)
                res.excel_sheets[sheet] = df
                text_snippets.append(f"--- Sheet: {sheet} ({len(df)} baris) ---\n" + df.head(10).to_string())
            
            res.extracted_text = "\n\n".join(text_snippets)
            res.summary_stats = {
                "format": "Legacy Excel (.xls)",
                "total_sheets": len(sheet_names),
                "sheet_names": sheet_names
            }
        except Exception as e:
            res.warnings.append(f"Gagal membaca berkas .xls: {e}")
            res.extracted_text = _extract_strings_from_bytes(file_bytes)

    elif ext in ["csv", "tsv"]:
        sep = "\t" if ext == "tsv" else None
        # Coba beberapa encoding umum
        df = None
        for enc in ["utf-8", "utf-8-sig", "latin1", "cp1252"]:
            try:
                df = pd.read_csv(io.BytesIO(file_bytes), sep=sep, encoding=enc, engine="python")
                break
            except Exception:
                continue

        if df is not None:
            res.excel_sheets["Data"] = df
            res.extracted_text = f"--- Berkas CSV/TSV ({len(df)} baris x {len(df.columns)} kolom) ---\n" + df.head(15).to_string()
            res.summary_stats = {
                "format": f"Delimited Text ({ext.upper()})",
                "baris": len(df),
                "kolom": len(df.columns),
                "daftar_kolom": list(df.columns)
            }
        else:
            res.warnings.append("Gagal mem-parsing berkas CSV/TSV sebagai tabel terstruktur.")
            res.extracted_text = file_bytes.decode("utf-8", errors="replace")

    elif ext == "ods":
        try:
            excel_file = pd.ExcelFile(io.BytesIO(file_bytes), engine="odf")
            for sheet in excel_file.sheet_names:
                df = pd.read_excel(excel_file, sheet_name=sheet)
                res.excel_sheets[sheet] = df
            res.extracted_text = f"OpenDocument Spreadsheet: {len(res.excel_sheets)} sheet."
        except Exception as e:
            res.warnings.append(f"Gagal membaca format ODS: {e}")
            res.extracted_text = _extract_strings_from_bytes(file_bytes)

    return res


def parse_pdf_document(file_bytes: bytes, run_ocr_forced: bool = False, lang: str = "ind+eng") -> DocumentAnalysisResult:
    """Menganalisis semua jenis dokumen PDF (Digital, Scanned, Terenkripsi) dilengkapi deteksi OCR."""
    res = DocumentAnalysisResult(
        doc_type="PDF",
        filename="",
        extension="pdf",
        file_size_bytes=len(file_bytes),
        sha3_256=hashlib.sha3_256(file_bytes).hexdigest(),
        sha256=hashlib.sha256(file_bytes).hexdigest()
    )

    page_texts: List[str] = []
    page_count = 0
    is_scanned = False

    pymupdf_success = False
    if fitz is not None:
        try:
            doc = fitz.open(stream=file_bytes, filetype="pdf")
            page_count = len(doc)
            res.page_count = page_count
            
            # Ekstrak metadata PDF
            meta = doc.metadata or {}
            res.title = meta.get("title", "")
            res.author = meta.get("author", "")
            res.created_at = meta.get("creationDate", "")
            res.modified_at = meta.get("modDate", "")
            res.metadata = {
                "producer": meta.get("producer", ""),
                "creator": meta.get("creator", ""),
                "format": meta.get("format", "PDF"),
                "encrypted": doc.is_encrypted,
            }

            # Ekstrak teks digital dari tiap halaman
            for pno in range(page_count):
                page = doc[pno]
                ptext = page.get_text().strip()
                page_texts.append(ptext)

            total_chars = sum(len(t) for t in page_texts)
            avg_chars_per_page = total_chars / max(1, page_count)

            # Jika rata-rata karakter per halaman < 20, kemungkinan besar PDF hasil scan citra
            if avg_chars_per_page < 20:
                is_scanned = True
                res.is_scanned_pdf = True
                res.warnings.append("Dokumen terdeteksi sebagai PDF Hasil Pindai (Scanned/Grafis murni).")

            res.extracted_text = "\n\n--- Halaman Baru ---\n\n".join(page_texts)

            # Eksekusi OCR jika dokumen scan ATAU jika user meminta force OCR
            if (is_scanned or run_ocr_forced) and get_tesseract_binary_path():
                res.ocr_performed = True
                res.ocr_engine = f"Tesseract OCR ({lang})"
                ocr_pages = []
                # Render halaman sebagai citra dan jalankan OCR (maksimal 10 halaman pertama untuk efisiensi)
                max_ocr_pages = min(page_count, 10)
                for pno in range(max_ocr_pages):
                    page = doc[pno]
                    pix = page.get_pixmap(dpi=150)
                    img_bytes = pix.tobytes("png")
                    txt, err = run_tesseract_ocr(img_bytes, lang=lang)
                    if txt:
                        ocr_pages.append(f"[Halaman {pno+1} - Hasil OCR]:\n{txt}")
                    elif err:
                        res.warnings.append(f"Halaman {pno+1}: {err}")

                res.ocr_text = "\n\n".join(ocr_pages)
                if not res.extracted_text.strip() or run_ocr_forced:
                    res.extracted_text = res.ocr_text

            res.summary_stats = {
                "halaman": page_count,
                "karakter_digital": total_chars,
                "apakah_scan": is_scanned,
                "apakah_terenkripsi": doc.is_encrypted,
                "ocr_aktif": res.ocr_performed
            }
            doc.close()
            pymupdf_success = True

        except Exception as e:
            res.warnings.append(f"Peringatan pymupdf: {e}. Menggunakan fallback pypdf.")
            pymupdf_success = False

    if not pymupdf_success and pypdf is not None:
        try:
            reader = pypdf.PdfReader(io.BytesIO(file_bytes))
            page_count = len(reader.pages)
            res.page_count = page_count
            res.metadata["encrypted"] = reader.is_encrypted

            for p in reader.pages:
                txt = p.extract_text() or ""
                page_texts.append(txt.strip())

            res.extracted_text = "\n\n".join(page_texts)
            res.summary_stats = {"halaman": page_count}
        except Exception as e:
            res.warnings.append(f"Gagal membaca PDF via pypdf: {e}")
            res.extracted_text = _extract_strings_from_bytes(file_bytes)

    return res


def parse_image_document(file_bytes: bytes, ext: str, lang: str = "ind+eng") -> DocumentAnalysisResult:
    """Menganalisis citra dokumen pindai (.png, .jpg, .tiff, dll) menggunakan mesin OCR."""
    res = DocumentAnalysisResult(
        doc_type="Image",
        filename="",
        extension=ext,
        file_size_bytes=len(file_bytes),
        sha3_256=hashlib.sha3_256(file_bytes).hexdigest(),
        sha256=hashlib.sha256(file_bytes).hexdigest(),
        is_scanned_pdf=True,
        ocr_performed=True,
        ocr_engine=f"Tesseract OCR ({lang})"
    )

    if Image is not None:
        try:
            img = Image.open(io.BytesIO(file_bytes))
            res.metadata = {
                "format": img.format,
                "mode": img.mode,
                "dimensi": f"{img.width} x {img.height} piksel"
            }
        except Exception as e:
            res.warnings.append(f"Gagal membaca metadata gambar: {e}")

    # Eksekusi OCR
    txt, err = run_tesseract_ocr(file_bytes, lang=lang)
    if txt:
        res.ocr_text = txt
        res.extracted_text = txt
        res.summary_stats = {
            "kata_ocr": len(txt.split()),
            "karakter_ocr": len(txt)
        }
    else:
        res.warnings.append(err or "OCR tidak menghasilkan teks.")

    return res


def analyze_document_unified(
    file_bytes: bytes,
    filename: str,
    run_ocr_forced: bool = False,
    ocr_lang: str = "ind+eng"
) -> DocumentAnalysisResult:
    """
    Titik masuk utama untuk menganalisis dan memvalidasi semua jenis dokumen:
    Word, Excel, PDF, dan Citra Pindai.
    """
    ext = filename.split(".")[-1].lower() if "." in filename else ""
    
    if ext in SUPPORTED_WORD_EXTENSIONS:
        res = parse_word_document(file_bytes, ext)
    elif ext in SUPPORTED_EXCEL_EXTENSIONS:
        res = parse_excel_document(file_bytes, ext)
    elif ext in SUPPORTED_PDF_EXTENSIONS:
        res = parse_pdf_document(file_bytes, run_ocr_forced=run_ocr_forced, lang=ocr_lang)
    elif ext in SUPPORTED_IMAGE_EXTENSIONS:
        res = parse_image_document(file_bytes, ext, lang=ocr_lang)
    else:
        # Coba deteksi konten dari magic bytes
        if file_bytes.startswith(b"%PDF"):
            res = parse_pdf_document(file_bytes, run_ocr_forced=run_ocr_forced, lang=ocr_lang)
        elif file_bytes.startswith(b"PK\x03\x04"):
            # Zip container: bisa docx atau xlsx
            try:
                with zipfile.ZipFile(io.BytesIO(file_bytes)) as z:
                    names = z.namelist()
                    if any("word/" in n for n in names):
                        res = parse_word_document(file_bytes, "docx")
                    elif any("xl/" in n for n in names):
                        res = parse_excel_document(file_bytes, "xlsx")
                    else:
                        res = parse_word_document(file_bytes, "docx")
            except Exception:
                res = parse_word_document(file_bytes, "docx")
        elif file_bytes.startswith(b"\xd0\xcf\x11\xe0"):
            # OLE2 compound file: Word (.doc) atau Excel (.xls)
            res = parse_word_document(file_bytes, "doc")
        else:
            res = DocumentAnalysisResult(
                doc_type="Text",
                filename=filename,
                extension=ext or "txt",
                file_size_bytes=len(file_bytes),
                sha3_256=hashlib.sha3_256(file_bytes).hexdigest(),
                sha256=hashlib.sha256(file_bytes).hexdigest(),
                extracted_text=file_bytes.decode("utf-8", errors="replace")
            )

    res.filename = filename
    return res
