from pdfminer.high_level import extract_text
import tempfile

def extract_text_from_pdf(file) -> str:
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(file.file.read())
        tmp_path = tmp.name
    return extract_text(tmp_path)
