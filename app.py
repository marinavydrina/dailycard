from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import openai
import os
import random

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dailycard_secret")  # for session usage
openai.api_key = os.getenv("OPENAI_API_KEY")

TAROT_CARDS = [
    "The Fool", "The Magician", "The High Priestess", "The Empress",
    "The Emperor", "The Hierophant", "The Lovers", "The Chariot",
    "Strength", "The Hermit", "Wheel of Fortune", "Justice",
    "The Hanged Man", "Death", "Temperance", "The Devil",
    "The Tower", "The Star", "The Moon", "The Sun",
    "Judgement", "The World"
]

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/card")
def card():
    if "card" not in session or "text" not in session:
        return redirect(url_for("index"))
    return render_template("card.html", card=session["card"], image=session["image"], text=session["text"]) 

@app.route("/thanks")
def thanks():
    return render_template("thanks.html")

@app.route("/draw", methods=["POST"])
def draw():
    data = request.get_json()
    question = data.get("question", "")
    card = random.choice(TAROT_CARDS)

    client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    prompt = f"""
You are a tarot reader. A person asked: '{question or 'What do I need to know today?'}'.
You drew the card '{card}'.
Explain the meaning of this card in 200-300 characters, using intuitive and insightful language.
"""

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are an intuitive and mystical tarot reader."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.9,
        max_tokens=300
    )

    interpretation = response.choices[0].message.content.strip()
    card_image = f"/static/cards/{card.lower().replace(' ', '_')}.png"

    # Сохраняем данные в сессию для отображения на /card
    session["card"] = card
    session["image"] = card_image
    session["text"] = interpretation

    return jsonify({"redirect": url_for("card")})

if __name__ == "__main__":
    app.run(debug=True)
