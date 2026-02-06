# parser.py

import pdfplumber
import docx
from pathlib import Path


def extract_text(file_path: str) -> str:
    path = Path(file_path)

    if path.suffix.lower() == ".pdf":
        return _from_pdf(file_path)

    elif path.suffix.lower() in [".docx", ".doc"]:
        return _from_docx(file_path)

    else:
        raise ValueError("Unsupported file type")


def _from_pdf(path):
    text = ""
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    return text.lower()


def _from_docx(path):
    doc = docx.Document(path)
    return "\n".join(p.text for p in doc.paragraphs).lower()