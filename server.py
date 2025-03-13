from flask import Flask,request,jsonify
from flask_cors import CORS
import speech_recognition as sr
import pyttsx3
import subprocess
import platform
import webbrowser
import wikipedia
import datetime

app = Flask(__name__)
CORS(app)

engine = pyttsx3.init()
engine.setProperty("rate",150)
engine.setProperty("volume",1.0)

def speak(text):
    engine.say(text)
    engine.runAndWait()

def open_application(command):
    """Function to open applications based on command"""
    system = platform.system()

    if "chrome" in command:
        if system == "Windows":
            subprocess.run("start chrome", shell=True)  # Windows
        elif system == "Darwin":
            subprocess.run("open -a 'Google Chrome'", shell=True)  # Mac
        elif system == "Linux":
            subprocess.run("google-chrome &", shell=True)  # Linux
        return "Opening Chrome"

    elif "notepad" in command:
        if system == "Windows":
            subprocess.run("notepad", shell=True)
            return "Opening Notepad"
        return "Notepad is only available on Windows"

    elif "vscode" in command or "visual studio code" in command:
        if system == "Windows":
            subprocess.run("code", shell=True)
        elif system == "Darwin":
            subprocess.run("open -a 'Visual Studio Code'", shell=True)
        elif system == "Linux":
            subprocess.run("code &", shell=True)
        return "Opening Visual Studio Code"

    elif "calculator" in command:
        if system == "Windows":
            subprocess.run("calc", shell=True)
        elif system == "Darwin":
            subprocess.run("open -a Calculator", shell=True)
        elif system == "Linux":
            subprocess.run("gnome-calculator &", shell=True)
        return "Opening Calculator"

    return None  # Return None if the application is not recognized


def listen():
    """Capture voice input from the user"""
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)
    
    try:
        command = recognizer.recognize_google(audio).lower()
        print("You said:", command)
        return command
    except sr.UnknownValueError:
        speak("Sorry, I didn't understand that.")
        return None
    except sr.RequestError:
        speak("Could not connect to the recognition service.")
        return None


@app.route("/process_command", methods=["POST"])
def process_command():
    data = request.json
    command = data.get("command", "").lower()

    if not command:
        return jsonify({"response":"No Command Received."})

    response = "I'm not sure how to respond to that"

    appresponse = open_application(command)
    if appresponse:
        response = appresponse

    if "time" in command:
        now = datetime.datetime.now().strftime("%H:%M")
        response = f"The Current time is {now}"
    
    elif "date" in command:
        today = datetime.date.today().strftime("%B %d, %Y")
        response = f"Today's date is {today}"

    elif "search" in command:
        search_query = command.replace("search","").strip()
        webbrowser.open(f"https://www.google.com/search?q={search_query}")
        response = f"searching for {search_query} on Google"

    elif "wikipedia" in command:
        topic = command.replace("wikipedia", "").strip()
        try:
            summary = wikipedia.summary(topic, sentences=2)
            response = f"According to Wikipedia: {summary}"
        except wikipedia.exceptions.DisambiguationError:
            response = f"Multiple results found for {topic}, please be more specific."
        except wikipedia.exceptions.PageError:
            response = f"Sorry, no results found for {topic} on Wikipedia."
    
    elif "exit" in command or "Stop" in command:
        response = "Goodbye! Have a nice day."

    return jsonify({"response" : response})


if __name__ == "__main__":
    app.run(debug=True)
    


