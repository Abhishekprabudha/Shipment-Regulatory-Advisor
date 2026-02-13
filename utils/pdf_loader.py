import io
import pdfplumber

def pdf_to_text_from_bytes(pdf_bytes: bytes, max_pages: int | None = 45) -> str:
    """
    Extract text from PDF bytes.
    max_pages caps work for Streamlit Cloud stability.
    """
    text_parts = []
    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
        pages = pdf.pages if max_pages is None else pdf.pages[:max_pages]
        for page in pages:
            t = page.extract_text() or ""
            if t.strip():
                text_parts.append(t)
    return "\n".join(text_parts)
