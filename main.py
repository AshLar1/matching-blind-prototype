import os
import openai
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)
openai.api_key = os.environ.get("OPENAI_API_KEY")


@app.route('/')
def landing():
    return render_template('landing.html')


@app.route('/app')
def app_page():
    return render_template('app.html')


@app.route('/onboarding')
def onboarding():
    return render_template('onboarding.html')


@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    messages = data.get("messages", [])

    if not any(msg["role"] == "system" for msg in messages):
        system_message = {
            "role":
            "system",
            "content":
            ("You're Matchie, a warm, flirty AI dating coach. Start with one friendly question, "
             "then guide the user through 5–7 quick-fire questions to learn their key interests, "
             "personality traits, dating goals, messaging style, and what they look for in a partner. "
             "After getting a basic answer on any one topic, move on. Don't ask multiple follow-ups or "
             "go deep on one subject (e.g., travel or food). Don't repeat the user's name or recap past answers. "
             "Keep responses natural, light, and brief—like a friend would. Once you’ve gathered enough info, "
             "wrap up by saying: 'Amazing! I’ve got everything I need 💘 Let’s find your best matches…' "
             "and stop replying after that.")
        }
        messages.insert(0, system_message)

    try:
        response = openai.ChatCompletion.create(model="gpt-3.5-turbo",
                                                messages=messages,
                                                temperature=0.75,
                                                max_tokens=200)
        reply = response.choices[0].message["content"]
        return jsonify({'reply': reply})
    except Exception as e:
        print("❌ OpenAI error:", str(e))
        return jsonify(
            {'reply': "Oops! Something went wrong. Please try again."}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
