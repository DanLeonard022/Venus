import speech_recognition as sr
import pyttsx3
import pywhatkit
import datetime
import wikipedia
import pyjokes
import sys
import webbrowser
import subprocess
import geocoder
import requests
import random
from transformers import pipeline, set_seed
import serial
import time
import torch
from PyDictionary import PyDictionary
import math


# Initialize GPT-2 model
generator = pipeline('text-generation', model='gpt2')
set_seed(42)

# Initialize speech recognition and TTS
listener = sr.Recognizer()
engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)

# Initialize Arduino
try:
    arduino = serial.Serial('COM3', 9600)  # Change to your port
    time.sleep(2)
except:
    arduino = None

remember_file = "remembered.txt"


dictionary = PyDictionary()

# Safe calculator using eval but only with math context
def calculate_expression(expr):
    try:
        allowed_names = {k: v for k, v in math.__dict__.items() if not k.startswith("__")}
        result = eval(expr, {"__builtins__": None}, allowed_names)
        talk(f"The result is {result}")
    except Exception as e:
        talk("Sorry, I couldn't calculate that.")

# Define word using dictionary
def define_word(word):
    try:
        url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
        response = requests.get(url)
        data = response.json()

        if isinstance(data, list) and "meanings" in data[0]:
            definition = data[0]["meanings"][0]["definitions"][0]["definition"]
            talk(f"{word} means: {definition}")
        else:
            talk("Sorry, I couldn't find the definition.")
    except Exception as e:
        talk("There was an error retrieving the definition.")
        print(e)


def answer_question(query):
    try:
        search_results = wikipedia.search(query)
        if not search_results:
            talk("Sorry, I couldn't find the answer.")
            return
        answer = wikipedia.summary(search_results[0], sentences=2)
        talk(answer)
    except wikipedia.exceptions.DisambiguationError as e:
        talk("Your question is too broad. Can you be more specific?")
    except Exception as e:
        talk("Sorry, I couldn't find the answer.")
        print(e)


thank_you_responses = [
    "You're welcome, sir!",
    "No problem at all!",
    "Glad to help, boss!",
    "Anytime, sir!",
    "You're very welcome!",
    "Walang anuman!",
    "Always here for you!",
    "No worries!",
    "Happy to assist you!",
    "With pleasure!"
]

def read_sensor_data():
    arduino.write(b't')  # Request temp/humidity
    time.sleep(2)
    while arduino.in_waiting > 0:
        data = arduino.readline().decode().strip()
        if "Temp" in data:
            print(data)
            talk(f"{data}")
            break
        
def talk(text):
    fillers = ["Okay,", "Hmm,", "Alright,", "Sure,", "Got it,", "Boss,"]
    
    if arduino:
        try:
            arduino.write(b'x')  # Trigger OLED waveform animation
            time.sleep(0.1)
        except:
            pass

    engine.say(random.choice(fillers) + " " + text)
    engine.runAndWait()

    if arduino:
        try:
            arduino.write(b'y')  # Return to OLED eyes
            time.sleep(0.1)
        except:
            pass


# Global conversation memory
conversation_history = "The following is a friendly conversation between an AI assistant named Venus and her boss Dan Leonard.\n"

# Greeting
talk('Hello, I am Venius, Your personal A.I assistant, how can i help you?')

def take_command():
    command = ""
    try:
        with sr.Microphone() as source:
            print('Listening...')
            voice = listener.listen(source, timeout=30)
            command = listener.recognize_google(voice)
            command = command.lower()
    except:
        pass
    return command

def gpt2_chat(prompt):
    global conversation_history
    conversation_history += f"\nBoss: {prompt}\nVenus:"
    talk("Let me think about that...")
    responses = generator(conversation_history, max_length=200, num_return_sequences=1, pad_token_id=50256)
    reply = responses[0]['generated_text'][len(conversation_history):].strip().split("\n")[0]
    conversation_history += f" {reply}"
    print("Venus:", reply)
    talk(reply)

def run_alexa():
    global conversation_history
    command = take_command()
    print("Command:", command)
    # Load remembered info at start
    try:
        with open(remember_file, "r") as file:
            remembered_info = file.read()
    except FileNotFoundError:
        remembered_info = ""
    
    if 'play' in command:
        song = command.replace('play', '')
        talk('Playing ' + song)
        pywhatkit.playonyt(song)

    elif 'time' in command:
        time_now = datetime.datetime.now().strftime('%I:%M %p')
        talk('Current time is ' + time_now)

    elif 'what is your name' in command:
        talk('I am Venus, your AI assistant.')

    elif 'what is my name' in command:
        talk('You are Sir Dan Leonard Belmonte, My one and only Boss!')

    elif 'joke' in command:
        talk(pyjokes.get_joke())

    elif 'who is' in command:
        human = command.replace('who is', '')
        try:
            info = wikipedia.summary(human, sentences=1)
            print(info)
            talk(info)
        except:
            talk("Sorry, I couldn't find that.")
    elif "check distance" in command or "is someone near" in command:
        arduino.write(b'u')
        time.sleep(0.5)
        while arduino.in_waiting:
            response = arduino.readline().decode().strip()
            if "Distance:" in response:
                distance = float(response.replace("Distance:", ""))
                if distance < 50:
                    talk(f"Yes, someone is nearby. Distance is {distance:.1f} centimeters.")
                else:
                    talk(f"No one is close. Distance is {distance:.1f} centimeters.")
                break
    elif "search" in command:
        query = command.replace("search", "").strip()
        if query:
            talk(f"Searching Google for {query}")
            pywhatkit.search(query)
        else:
            talk("What do you want me to search?")

    elif 'news today' in command:
        talk("Fetching the latest news headlines from the Philippines.")
        try:
            api_key = "6e10c98254744aa9aa2bc1f83fa1653e"  # ← Replace with your actual NewsAPI key
            url = f"https://newsapi.org/v2/top-headlines?country=ph&apiKey={api_key}"
            response = requests.get(url)
            data = response.json()

            if data["status"] == "ok":
                articles = data["articles"][:3]  # Limit to top 3 headlines
                if articles:
                    for idx, article in enumerate(articles, 1):
                        headline = article['title']
                        talk(f"Headline {idx}: {headline}")
                else:
                    talk("Sorry, no news articles are available at the moment.")
            else:
                talk("There was a problem fetching the news.")
        except Exception as e:
            talk("Sorry, I couldn't fetch the news right now.")
            print("Error:", e)
    
    elif "define" in command:
        word = command.replace("define", "").strip()
        define_word(word)

    elif "calculate" in command:
        expr = command.replace("calculate", "").strip()
        calculate_expression(expr)

    elif "what is" in command:
        question = command.replace("what is", "").strip()
        answer_question(question)

    elif 'remember that' in command:
        talk("What would you like me to remember?")
        remembered_info = take_command()
        with open(remember_file, "w") as file:
            file.write(remembered_info)
        talk("Got it. I will remember that.")

    elif 'what did you remember' in command:
        if remembered_info:
            talk(f"You asked me to remember: {remembered_info}")
        else:
            talk("I don't remember anything yet.")
        
    elif 'location' in command:
        talk('Please specify the location.')
        location = take_command()
        location_coordinates = geocoder.arcgis(location)
        if location_coordinates.ok:
            lat, lon = location_coordinates.latlng
            map_url = f"https://www.google.com/maps/place/{lat},{lon}"
            talk(f"Here is the location of {location} on Google Maps.")
            webbrowser.open(map_url)
        else:
            talk(f"Sorry, I couldn't find {location}.")

    elif 'weather' in command:
        talk('Sure, which city?')
        city = take_command()
        api_key = '8b62dd7f560bf879b712aab9a5477df3'
        base_url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric'
        response = requests.get(base_url)
        weather_data = response.json()
        if weather_data['cod'] == 200:
            desc = weather_data['weather'][0]['description']
            temp = weather_data['main']['temp']
            humid = weather_data['main']['humidity']
            talk(f"The weather in {city} is {desc}. Temperature: {temp}°C. Humidity: {humid}%.")
        else:
            talk(f"Sorry, I couldn't get weather info for {city}.")

    elif 'turn on the green light' in command:
        talk("Turning on green light.")
        arduino.write(b'1')

    elif 'turn off the green light' in command:
        talk("Turning off green light.")
        arduino.write(b'0')

    elif 'turn on the yellow light' in command:
        talk("Turning on yellow light.")
        arduino.write(b'4')

    elif 'turn off the yellow light' in command:
        talk("Turning off yellow light.")
        arduino.write(b'5')

    elif 'turn on the red light' in command:
        talk("Turning on red light.")
        arduino.write(b'6')

    elif 'turn off the red light' in command:
        talk("Turning off red light.")
        arduino.write(b'7')

    elif 'turn on all lights' in command:
        talk("Turning on all lights.")
        arduino.write(b'8')

    elif 'turn off all lights' in command:
        talk("Turning off all lights.")
        arduino.write(b'9')

    elif 'turn on the alarm' in command:
        talk("Turning on the alarm.")
        arduino.write(b'2')

    elif 'turn off the alarm' in command:
        talk("Turning off the alarm.")
        arduino.write(b'3')
    elif "activate emergency mode" in command:
        talk("Emergency mode activated.")
        arduino.write(b'e')

    elif "stop emergency mode" in command:
        talk("Emergency mode deactivated.")
        arduino.write(b'f')

    elif "chase led" in command:
        talk("Starting chase LED effect.")
        arduino.write(b'g')

    elif "blink led" in command:
        talk("Blinking all LEDs.")
        arduino.write(b'h')

    elif 'smile' in command:
        talk("I'm smiling now!")
        arduino.write(b's')

    elif 'angry' in command or 'angry' in command:
        talk("I'm angry now!")
        arduino.write(b'a')

    elif 'sad' in command or 'sad' in command:
        talk("I'm feeling sad.")
        arduino.write(b'l')

    elif 'wink' in command:
        talk("Here's a wink!")
        arduino.write(b'w')

    elif 'sleep' in command or 'sleep' in command:
        talk("Going to sleep.")
        arduino.write(b'z')

    elif 'wake up' in command or 'wake up' in command:
        talk("I'm awake!")
        arduino.write(b'e')


    elif 'rotate to 0' in command:
        talk("Rotating to 0 degrees.")
        arduino.write(b'a')

    elif 'rotate to 90' in command:
        talk("Rotating to 90 degrees.")
        arduino.write(b'b')

    elif 'rotate to 180' in command:
        talk("Rotating to 180 degrees.")
        arduino.write(b'c')

    elif 'what is the temperature' in command or 'humidity' in command:
        talk("Reading temperature and humidity. Please wait.")
        if arduino:
            arduino.write(b'd')  # Command to Arduino to send temp/humidity
            time.sleep(2)        # Give Arduino time to respond

            if arduino.in_waiting:
                data = arduino.readline().decode().strip()
                print("Arduino says:", data)
                talk(data)  # AI says it out loud!
            else:
                talk("Sorry, I could not read the sensor data.")

    elif 'thank you' in command or 'thanks' in command:
        response = random.choice(thank_you_responses)
        talk(response)  

    elif 'reset conversation' in command:
        conversation_history = "The following is a friendly conversation between an AI assistant named Venus and her boss Dan Leonard.\n"
        talk("Conversation memory has been reset.")

    elif 'venus' in command or 'ai chat' in command:
        talk("What would you like to talk about?")
        prompt = take_command()
        if prompt:
            gpt2_chat(prompt)
        else:
            talk("I didn't catch that. Can you repeat it?")

    elif command != "":
        gpt2_chat(command)
    
    

    else:
        talk('Sorry, I didn’t hear anything.')

while True:
    run_alexa()


