import os
import json
import uuid
from flask import Flask, render_template, request, jsonify, redirect, url_for
from werkzeug.utils import secure_filename
from tinydb import TinyDB
from openai import OpenAI

app = Flask(__name__)
client = OpenAI()
db = TinyDB('user_data.json')

UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route('/')
def landing():
    return render_template('landing.html')


@app.route('/app')
def app_page():
    return render_template('app.html')


@app.route('/onboarding')
def onboarding():
    return render_template('onboarding.html')


@app.route('/profile')
def profile():
    user = db.all()[-1] if db.all() else {}
    return render_template('profile.html', user=user)


@app.route('/edit_profile', methods=['POST'])
def edit_profile():
    if db.all():
        user = db.all()[-1]
        doc_id = user.doc_id

        updated_data = {
            'name': request.form.get('name', user.get('name',
                                                      'Not specified')),
            'interests': request.form.get('interests', 'Not specified'),
            'traits': request.form.get('traits', 'Not specified'),
            'goals': request.form.get('goals', 'Not specified'),
            'messaging': request.form.get('messaging', 'Not specified'),
            'what_they_want': request.form.get('what_they_want',
                                               'Not specified'),
            'location': request.form.get('location', 'Not specified'),
            'gender': request.form.get('gender', 'Not specified')
        }

        # Handle profile image upload
        image_file = request.files.get('image_file')
        if image_file and image_file.filename:
            filename = secure_filename(image_file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            image_file.save(filepath)
            updated_data['image_url'] = f"/static/uploads/{filename}"
        else:
            updated_data['image_url'] = user.get('image_url', 'Not specified')

        # Clean list formatting (if user typed in brackets/lists accidentally)
        for key in ['interests', 'traits', 'goals']:
            val = updated_data.get(key, '')
            if val.startswith("[") and val.endswith("]"):
                try:
                    parsed = json.loads(val.replace("'", '"'))
                    if isinstance(parsed, list):
                        updated_data[key] = ', '.join(parsed[:5])
                except:
                    pass

        db.update(updated_data, doc_ids=[doc_id])

    return redirect(url_for('profile'))


@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    messages = data.get("messages", [])

    if not any(msg["role"] == "system" for msg in messages):
        messages.insert(
            0, {
                "role":
                "system",
                "content":
                ("You're Matchie, a warm, flirty AI dating coach. Keep things light and charming. "
                 "Start by asking the user's name, then naturally guide them through a conversational flow "
                 "to learn their interests, personality traits, relationship goals, messaging style, "
                 "and what they look for in a partner. Use relatable, engaging dialogue instead of lists. "
                 "If they give short answers, gently ask follow-ups. Only wrap up when you've collected all key details. "
                 "End with: 'Amazing! I’ve got everything I need 💘 Let’s find your best matches…'"
                 )
            })

    try:
        response = client.chat.completions.create(model="gpt-3.5-turbo",
                                                  messages=messages,
                                                  temperature=0.8,
                                                  max_tokens=200,
                                                  timeout=30)
        reply = response.choices[0].message.content.strip()

        end_triggers = [
            "let’s find your best matches", "let's find your best matches"
        ]
        if any(trigger in reply.lower() for trigger in end_triggers):
            user_answers = [
                m['content'] for m in messages if m['role'] == 'user'
            ]
            combined_text = ' '.join(user_answers).replace("\\", "").strip()

            profile = extract_profile_from_text(combined_text)
            profile['user_id'] = str(uuid.uuid4())

            fields = [
                'name', 'interests', 'traits', 'goals', 'messaging',
                'what_they_want'
            ]
            for field in fields:
                if field not in profile or not profile[field]:
                    profile[field] = user_answers[
                        0] if field == 'name' else "Not specified"

            for key in ['traits', 'interests']:
                if isinstance(profile.get(key), list):
                    profile[key] = profile[key][:5]

            for key in ['traits', 'goals', 'messaging', 'what_they_want']:
                val = profile.get(key, "")
                if isinstance(val, list):
                    val = ', '.join(val)
                if len(val) > 300:
                    profile[key] = val[:300] + "..."

            profile['location'] = "Not specified"
            profile['gender'] = "Not specified"
            profile['image_url'] = "Not specified"

            db.insert(profile)

        return jsonify({'reply': reply})

    except Exception as e:
        print("❌ OpenAI error:", str(e))
        return jsonify(
            {'reply': "Oops! Something went wrong. Please try again."}), 500


def extract_profile_from_text(user_text):
    try:
        user_text = user_text.replace("\\", "").strip()
        prompt = (
            "Extract a structured profile in JSON format from this user conversation.\n\n"
            "Return the following fields:\n"
            "- name\n"
            "- interests\n"
            "- traits\n"
            "- goals\n"
            "- messaging\n"
            "- what_they_want\n\n"
            f"Conversation:\n{user_text}")
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{
                "role":
                "system",
                "content":
                "You're a helpful assistant that extracts dating profiles from conversations."
            }, {
                "role": "user",
                "content": prompt
            }],
            temperature=0.3,
            max_tokens=300,
            timeout=30)
        content = completion.choices[0].message.content.strip()
        return json.loads(content)

    except Exception as e:
        print("❌ GPT profile extraction failed:", e)
        return {}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
