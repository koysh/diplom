import io
from pdfminer.high_level import extract_text

def extract_pdf_text(file):
    try:
        # Чтение файла из объекта FileStorage
        file_stream = io.BytesIO(file.read())
        
        # Извлечение текста с использованием pdfminer
        text = extract_text(file_stream)
        
        return text
    except Exception as e:
        # Обработка возможных ошибок
        print(f"Ошибка при извлечении текста из PDF: {e}")
        return ""
