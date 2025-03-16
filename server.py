from flask import Flask,request,jsonify
from flask_cors import CORS
from gtts import gTTS
import speech_recognition as sr
import subprocess
import platform
import webbrowser
import wikipedia
import datetime
import pytz

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})


def speak(text):
    tts = gTTS(text=text, lang='en')
    file_path = "response.mp3"
    tts.save(file_path)
    return file_path

def open_application(command,env):
    """Function to open applications based on command"""
    system = platform.system()
    if "chrome" in command:
        if env == "live":
            return "Click here to open Google: https://www.google.com"
        if system == "Windows":
            subprocess.run("start chrome", shell=True)  # Windows
        elif system == "Darwin":
            subprocess.run("open -a 'Google Chrome'", shell=True)  # Mac
        elif system == "Linux":
            subprocess.run("google-chrome &", shell=True)  # Linux
        return "Opening Chrome"

    elif "notepad" in command:
        if env == "live":
            return "You can open Notepad by pressing Win + R and typing 'notepad"
        if system == "Windows":
            subprocess.run("notepad", shell=True)
            return "Opening Notepad"
        return "Notepad is only available on Windows"

    elif "vscode" in command or "visual studio code" in command:
        if env == "live":
            return "You can open VS Code from your start menu or by running 'code' in a terminal."
        if system == "Windows":
            subprocess.run("code", shell=True)
        elif system == "Darwin":
            subprocess.run("open -a 'Visual Studio Code'", shell=True)
        elif system == "Linux":
            subprocess.run("code &", shell=True)
        return "Opening Visual Studio Code"

    elif "calculator" in command:
        if env == "live":
            return "Open the calculator manually on your device."
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

@app.route("/")
def home():
    return "Hello, your Flask app is running!"


@app.route("/process_command", methods=["POST"])
def process_command():
    data = request.json
    command = data.get("command", "").lower()
    user_timezone = data.get("timezone", "UTC")
    
    client_host = request.host  # Gets the host of the request
    # client_ip = request.remote_addr  # Gets the IP of the requester

    if "127.0.0.1" in client_host or "localhost" in client_host:  # Check if local
        environment = "local"
    else:
        environment = "live"

    if not command:
        return jsonify({"response":"No Command Received."})

    response = "I'm not sure how to respond to that"

    appresponse = open_application(command,environment)
    if appresponse:
        response = appresponse

    if "time" in command:
        local_tz = pytz.timezone(user_timezone)
        now = datetime.datetime.now(local_tz).strftime("%H:%M")
        response = f"The Current time is {now}"
    
    elif "date" in command:
        today = datetime.date.today().strftime("%B %d, %Y")
        response = f"Today's date is {today}"

    elif "search" in command:
        search_query = command.replace("search", "").strip()
        try:
            url = f"https://www.google.com/search?q={search_query.replace(' ', '+')}"
            # webbrowser.open(url)
            # response = f"Searching for {search_query} on Google"
            response = {'success': True, 'url': url, 'message': f"Searching for {search_query} on Google.",'searchText':search_query}
        except:
            response = f"Unable to perform search for {search_query}."

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
    from waitress import serve  # Waitress is better for Windows
    print("Starting server on port 8000...")
    serve(app, host="0.0.0.0", port=8000)
   
    


