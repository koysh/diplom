import io
from pdfminer.high_level import extract_text

def extract_pdf_text(file):
    # Чтение файла из объекта FileStorage
    file_stream = io.BytesIO(file.read())
    
    # Извлечение текста с использованием pdfminer
    text = extract_text(file_stream)
    
    return text