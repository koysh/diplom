import io
import speech_recognition as sr

def recognize_speech_from_audio(file):
    try:
        file.seek(0)  # Перемещаем указатель в начало
        recognizer = sr.Recognizer()
        audio_file = sr.AudioFile(io.BytesIO(file.read()))
        with audio_file as source:
            audio = recognizer.record(source)
        return recognizer.recognize_google(audio, language='ru-RU')
    except Exception as e:
        return f"Ошибка при обработке аудио: {e}"
