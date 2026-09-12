import pdfplumber
import docx


def extract_text_from_pdf(file):
    """Extract text from a PDF file object."""
    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text


def extract_text_from_docx(file):
    """Extract text from a DOCX file object."""
    document = docx.Document(file)
    text = ""
    for paragraph in document.paragraphs:
        text += paragraph.text + "\n"
    return text


def extract_resume_text(uploaded_file):
    """
    Detects file type and extracts text accordingly.
    uploaded_file: Streamlit UploadedFile object
    """
    file_type = uploaded_file.name.split(".")[-1].lower()

    if file_type == "pdf":
        return extract_text_from_pdf(uploaded_file)
    elif file_type == "docx":
        return extract_text_from_docx(uploaded_file)
    else:
        return None