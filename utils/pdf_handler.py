import io
from pdfminer.high_level import extract_text
import logging

logger = logging.getLogger(__name__)

def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Извлекает текст из PDF-файла."""
    try:
        with io.BytesIO(file_bytes) as file_stream:
            text = extract_text(file_stream)
        logger.info(f"Извлеченный текст из PDF: {text}")  # Логируем извлеченный текст
        return text if text.strip() else "Файл пуст или не содержит текста"
    except Exception as e:
        logger.error(f"Ошибка при обработке PDF: {e}")
        return f"Ошибка при обработке PDF: {e}"