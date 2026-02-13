import io
import pdfplumber


def pdf_to_text(uploaded_file) -> str:
    """
    Reads a Streamlit uploaded PDF directly from memory (no file path needed).
    Returns extracted text as a single string.
    """
    pdf_bytes = uploaded_file.read()

    text_parts = []
    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
        for page in pdf.pages:
            text = page.extract_text() or ""
            if text.strip():
                text_parts.append(text)

    return "\n".join(text_parts)
