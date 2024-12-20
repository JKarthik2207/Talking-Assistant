from flask import Flask, request, jsonify, render_template
import speech_recognition as sr
import pyttsx3
import google.generativeai as genai

app = Flask(__name__)

# Configure Google Generative AI API
genai.configure(api_key="AIzaSyDaq6jzrKBIAkQyVPzyVaDyeQ6STB4y8fo")

# Initialize text-to-speech engine
def speak_text(text, language="en"):
    engine = pyttsx3.init()
    voices = engine.getProperty("voices")
    for voice in voices:
        if language in voice.languages:
            engine.setProperty("voice", voice.id)
            break
    engine.say(text)
    engine.runAndWait()

# Function for speech-to-text
def recognize_speech(language="en-US"):
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        audio = recognizer.listen(source)
        try:
            text = recognizer.recognize_google(audio, language=language)
            return text
        except sr.UnknownValueError:
            return "Error: Could not understand audio"
        except sr.RequestError:
            return "Error: Service unavailable"

# Function for generating a conversational response
def generate_response(question, language="en"):
    try:
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            generation_config={
                "temperature": 0.9,
                "top_p": 0.95,
                "top_k": 50,
                "max_output_tokens": 50,
                "response_mime_type": "text/plain",
            },
            system_instruction="You are a friendly, multilingual assistant."
        )
        response = model.generate_content(question,duration=1)
        return response.text
    except Exception as e:
        return f"Oops! Something went wrong: {str(e)}"

@app.route('/')
def index():
    return render_template('mic_ui.html')

@app.route('/conversation', methods=['POST'])
def conversation():
    language = request.json.get("language", "en-US")  # Default to English
    user_input = recognize_speech(language=language)
    if "exit" in user_input.lower():
        return jsonify()
    
    if "Error" in user_input:
        return jsonify()

    response = generate_response(user_input, language=language.split("-")[0])
    speak_text(response, language=language.split("-")[0])
    return jsonify({"response": response})

if __name__ == "__main__":
    app.run(debug=True)
