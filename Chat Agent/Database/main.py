from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
import requests
import datetime

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# -------------------------
# MongoDB Connection
# -------------------------
client = MongoClient("mongodb://localhost:27017/")
db = client["amitabh_info"]

# Collections
personal_info = db["personal_info"]
movies = db["movies"]
awards = db["awards"]
tv_shows = db["tv_shows"]
biography = db["biography"]
chats = db["chats"]  # NEW collection for chat history

# -------------------------
# OpenRouter API Setup
# -------------------------
api_key = "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"  # paste your real key here # replace with your real key
url = "https://openrouter.ai/api/v1/chat/completions"

def get_openrouter_response(question, context):
    payload = {
        "model": "z-ai/glm-4.5-air:free",  # free model
        "messages": [
            {"role": "system", "content": "You are a chatbot about Amitabh Bachchan. Answer only using the provided context."},
            {"role": "user", "content": f"Context: {context}\n\nQuestion: {question}"}
        ]
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return data["choices"][0]["message"]["content"]
        else:
            return f"Error: {response.status_code} - {response.text}"
    except Exception as e:
        return f"Error: {str(e)}"

# -------------------------
# Chat Endpoints
# -------------------------
@app.route("/chat", methods=["POST"])
def create_chat():
    chat_id = str(datetime.datetime.utcnow().timestamp())
    chat_doc = {
        "_id": chat_id,
        "created_at": datetime.datetime.utcnow(),
        "messages": []
    }
    chats.insert_one(chat_doc)
    return jsonify({"chat_id": chat_id})

@app.route("/chats", methods=["GET"])
def list_chats():
    chat_list = chats.find({}, {"_id": 1, "created_at": 1})
    return jsonify([
        {"chat_id": c["_id"], "created_at": c["created_at"].isoformat()}
        for c in chat_list
    ])

@app.route("/chat/<chat_id>", methods=["GET"])
def get_chat(chat_id):
    chat = chats.find_one({"_id": chat_id}, {"_id": 1, "messages": 1})
    if chat:
        return jsonify(chat)
    return jsonify({"error": "Chat not found"}), 404

@app.route("/chat/<chat_id>/message", methods=["POST"])
def add_message(chat_id):
    data = request.json
    sender = data.get("sender")
    text = data.get("text", "").strip()

    # If user asks a question, query backend
    if sender == "user":
        # Pull context from MongoDB
        context_parts = []

        bio_doc = biography.find_one()
        if bio_doc and "bio" in bio_doc:
            context_parts.append(bio_doc["bio"])

        for movie in movies.find():
            context_parts.append(f"Movie: {movie.get('title')} ({movie.get('release_year')})")

        for award in awards.find():
            context_parts.append(f"Award: {award.get('name')} ({award.get('year')})")

        for show in tv_shows.find():
            context_parts.append(f"TV Show: {show.get('title')} ({show.get('year')})")

        context = "\n".join(context_parts)

        bot_reply = get_openrouter_response(text, context)
        chats.update_one(
            {"_id": chat_id},
            {"$push": {"messages": {"sender": "user", "text": text, "timestamp": datetime.datetime.utcnow()}}}
        )
        chats.update_one(
            {"_id": chat_id},
            {"$push": {"messages": {"sender": "bot", "text": bot_reply, "timestamp": datetime.datetime.utcnow()}}}
        )
        return jsonify({"sender": "bot", "text": bot_reply})

    else:
        # Save non-user messages
        message = {"sender": sender, "text": text, "timestamp": datetime.datetime.utcnow()}
        chats.update_one({"_id": chat_id}, {"$push": {"messages": message}})
        return jsonify(message)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
