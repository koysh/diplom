import speech_recognition as sr

def recognize_speech_from_audio(file):
    recognizer = sr.Recognizer()
    audio_file = sr.AudioFile(file)
    with audio_file as source:
        audio = recognizer.record(source)  # Читаем аудиофайл
    return recognizer.recognize_google(audio, language='ru-RU')  # Преобразуем речь в текст