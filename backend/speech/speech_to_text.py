import speech_recognition as sr

def speech_to_text():

    recognizer = sr.Recognizer()

    with sr.Microphone() as source:

        print("Listening...")

        audio = recognizer.listen(source)

        text = recognizer.recognize_google(audio)

        return text