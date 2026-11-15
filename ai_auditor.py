"""ai_auditor.py - Modul Asisten AI Anti-Halusinasi untuk Audit Dokumen Resmi (Word, Excel, PDF).
Menerapkan Strict Grounding, Temperature 0.0, dan Verbatim Citation.
Membaca API Key secara aman dari environment variable atau Streamlit Secrets.
"""
from __future__ import annotations
import json
import os
import urllib.request
import urllib.error

# Ambil kunci API dari Environment Variable atau Streamlit Secrets
def get_groq_api_key() -> str:
    # 1. Dari OS Environment
    key = os.environ.get("GROQ_API_KEY", "")
    if key:
        return key.strip()
        
    # 2. Dari Streamlit Secrets (jika berjalan di Streamlit Cloud)
    try:
        import streamlit as st
        if hasattr(st, "secrets") and "GROQ_API_KEY" in st.secrets:
            return str(st.secrets["GROQ_API_KEY"]).strip()
    except Exception:
        pass
        
    return ""

DEFAULT_MODEL = "qwen/qwen3.8-27b"

SYSTEM_PROMPT_ANTI_HALU = """Kamu adalah Auditor Forensik Dokumen Institusi Resmi yang sangat teliti, objektif, dan berpijak 100% pada fakta.

TUGAS UTAMA:
Analisis teks dokumen resmi (Word/Excel/PDF) yang dilampirkan dan sajikan fakta secara terstruktur.

ATURAN ANTI-HALUSINASI (WAJIB DIPATUHI):
1. STRICT GROUNDING: Seluruh jawabanmu HANYA boleh bersumber dari teks dokumen yang dilampirkan.
2. DILARANG BERASUMSI: Jangan menambahkan asumsi, interpretasi bebas, pengetahuan luar, atau mereka-reka informasi yang tidak tertulis eksplisit.
3. PRINSIP TIDAK DITEMUKAN: Jika ada fakta atau pertanyaan yang tidak tertulis jelas di dalam teks, kamu WAJIB menjawab: "Informasi tidak ditemukan di dalam dokumen". Jangan mencoba menebak.
4. BUKTI KUTIPAN (CITATION): Setiap kali kamu menyebutkan fakta atau klausul penting, wajib sertakan kutipan langsung persis (verbatim quote) dari teks di dalam tanda kutip dua "...".
5. OBJEKTIF: Fokus pada nomor surat, tanggal, para pihak berwenang, nominal uang, hak, kewajiban, dan potensi anomali.
"""

def call_groq_api(messages: list[dict], api_key: str | None = None, model: str = DEFAULT_MODEL, temperature: float = 0.0) -> str:
    """Memanggil API Groq Cloud secara aman."""
    active_key = api_key or get_groq_api_key()
    if not active_key:
        return "⚠️ Kunci API Groq belum disetel. Masukkan GROQ_API_KEY di Streamlit Secrets atau form input."

    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {active_key.strip()}",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
    }
    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": 1500
    }
    
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            res_json = json.loads(resp.read().decode("utf-8"))
            return res_json["choices"][0]["message"]["content"]
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8")
        return f"❌ Error API Groq ({e.code}): {error_body}"
    except Exception as e:
        return f"❌ Gagal memanggil AI: {str(e)}"

def analyze_document_content(doc_text: str, doc_name: str = "Dokumen", custom_question: str | None = None, api_key: str | None = None) -> str:
    """Menganalisis isi dokumen Word/Excel/PDF dengan jaminan anti-halusinasi."""
    if not doc_text or len(doc_text.strip()) == 0:
        return "⚠️ Dokumen kosong atau teks tidak dapat diekstraksi."
        
    truncated_text = doc_text[:12000]
    
    if custom_question:
        user_prompt = f"""[DOKUMEN RESMI: {doc_name}]
{truncated_text}
[AKHIR DOKUMEN]

PERTANYAAN PENGGUNA:
{custom_question}

Instruksi: Jawab pertanyaan di atas HANYA berdasarkan dokumen. Jika jawabannya tidak ada di dokumen, nyatakan secara eksplisit bahwa tidak ditemukan. Sertakan kutipan langsung jika ada."""
    else:
        user_prompt = f"""[DOKUMEN RESMI: {doc_name}]
{truncated_text}
[AKHIR DOKUMEN]

INSTRUKSI AUDIT FAKTUAL:
1. Ringkasan Eksekutif (Maksimal 3 butir fakta utama).
2. Identitas Dokumen (Nomor surat, tanggal pengesahan, dan instansi pembuat).
3. Para Pihak / Pejabat Berwenang yang disebutkan dalam teks.
4. Klausul Kunci / Nominal Anggaran Penting (wajib kutipan langsung persis).
5. Potensi Risiko / Catatan Auditor (misal: tanggal kedaluwarsa, denda, atau selang nominal). Jika tidak ada, sebutkan "Tidak terdeteksi klausul berisiko"."""

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT_ANTI_HALU},
        {"role": "user", "content": user_prompt}
    ]
    
    return call_groq_api(messages, api_key=api_key, temperature=0.0)
