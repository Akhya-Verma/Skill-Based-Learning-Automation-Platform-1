import io
import re


def extract_text_from_pdf(file_bytes):
    import PyPDF2
    reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
    pages = []
    for page in reader.pages:
        text = page.extract_text()
        if text:
            pages.append(text)
    return "\n".join(pages)


def extract_text_from_docx(file_bytes):
    import docx
    doc = docx.Document(io.BytesIO(file_bytes))
    paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
    return "\n".join(paragraphs)


def parse_resume(file_bytes, filename):
    ext = filename.rsplit(".", 1)[-1].lower()
    if ext == "pdf":
        return extract_text_from_pdf(file_bytes), "pdf"
    elif ext == "docx":
        return extract_text_from_docx(file_bytes), "docx"
    else:
        raise ValueError(f"Unsupported file type: .{ext}")


def extract_email(text):
    matches = re.findall(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}", text)
    return matches[0] if matches else ""


def extract_name(text):
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    for line in lines[:5]:
        if len(line.split()) <= 5 and not any(
            kw in line.lower()
            for kw in ["resume", "curriculum", "cv", "profile", "summary"]
        ):
            return line
    return "Unknown"