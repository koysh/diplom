from docx import Document

def extract_docx_text(file):
    doc = Document(file)  # Открываем DOCX-файл
    text = '\n'.join([para.text for para in doc.paragraphs])  # Собираем текст всех параграфов
    return text