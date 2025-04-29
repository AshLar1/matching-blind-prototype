import os
import openai
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)
openai.api_key = os.environ.get(
    "OPENAI_API_KEY")  # ✅ Replace securely in production

conversation_history = [{
    "role":
    "system",
    "content":
    "You are a friendly AI dating coach helping users prepare for love. Ask thoughtful follow-up questions and make it feel natural and personal."
}]


# Home landing page
@app.route('/')
def landing():
    return render_template('landing.html')


# Dashboard after sign-up
@app.route('/app')
def app_page():
    return render_template('app.html')


# Onboarding chat
@app.route('/onboarding')
def onboarding():
    return render_template('onboarding.html')


# Chat API endpoint
@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json['message']
    conversation_history.append({"role": "user", "content": user_input})

    response = openai.ChatCompletion.create(model="gpt-3.5-turbo",
                                            messages=conversation_history)

    reply = response['choices'][0]['message']['content']
    conversation_history.append({"role": "assistant", "content": reply})

    return jsonify({'reply': reply})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
