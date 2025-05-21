from flask import Flask, render_template, request, jsonify, session
import os
import requests
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "supersecretkey")  # Needed for session

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

HEADERS = {
    "Authorization": f"Bearer {GROQ_API_KEY}",
    "Content-Type": "application/json"
}

user_chats = {}

def get_chatbot_response(user_input, chat_history, user_name=None):
    system_prompt = (
        "You are a compassionate AI mental health chatbot. "
        "Detect the user's emotional state from their message and respond with supportive, thoughtful and motivational advice. "
        "Use emojis to keep the tone friendly, and never ask the user to rate their mood explicitly. "
        "Speak casually like a human, but stay empathetic and mentally supportive."
    )
    if user_name:
        system_prompt += f" The user's name is {user_name}."

    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(chat_history)  # chat_history contains dicts with role & content
    messages.append({"role": "user", "content": user_input})

    body = {
        "model": "llama3-8b-8192",  # Or try "llama3-70b-8192" if needed
        "messages": messages,
        "temperature": 0.7
    }

    response = requests.post(GROQ_API_URL, headers=HEADERS, json=body)

    if response.status_code == 200:
        try:
            data = response.json()
            return data["choices"][0]["message"]["content"].strip()
        except Exception:
            return "⚠️ Sorry, I had trouble understanding that. Can you try again?"
    else:
        return "⚠️ The chatbot is currently unavailable. Please try again later."

@app.route("/")
def home():
    return render_template("chatbot.html")

@app.route("/chat", methods=["POST"])
def chat():
    user_ip = request.remote_addr
    data = request.get_json()
    user_input = data.get("message", "").strip()

    if user_ip not in user_chats:
        user_chats[user_ip] = {
            "name": None,
            "history": []
        }

    user_data = user_chats[user_ip]


    lower_input = user_input.lower()
    if "my name is" in lower_input:
        name = user_input.lower().split("my name is")[-1].strip()
        name = " ".join(w.capitalize() for w in name.split())
        user_data["name"] = name
        response_text = f"Got it! I will remember your name as {name}."
        user_data["history"].append({"role": "user", "content": user_input})
        user_data["history"].append({"role": "assistant", "content": response_text})
        return jsonify({"response": response_text})

    ai_response = get_chatbot_response(user_input, user_data["history"], user_data["name"])

    user_data["history"].append({"role": "user", "content": user_input})
    user_data["history"].append({"role": "assistant", "content": ai_response})

    return jsonify({"response": ai_response})

if __name__ == "__main__":
    app.run(debug=True)
