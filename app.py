from flask import Flask, request, jsonify
import sqlite3
from datetime import datetime
import os

app = Flask(__name__)
DB_NAME = "reviews.db"

# Создание таблицы, если не существует
def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS reviews (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                text TEXT NOT NULL,
                sentiment TEXT NOT NULL,
                created_at TEXT NOT NULL
            );
        ''')
        conn.commit()

# Простая логика определения настроения
def analyze_sentiment(text):
    text = text.lower()
    positives = ["хорош", "люблю"]
    negatives = ["плохо", "ненавиж"]

    if any(word in text for word in positives):
        return "positive"
    elif any(word in text for word in negatives):
        return "negative"
    else:
        return "neutral"

@app.route("/reviews", methods=["POST"])
def add_review():
    data = request.get_json()
    text = data.get("text", "")
    if not text.strip():
        return jsonify({"error": "Отзыв не может быть пустым"}), 400

    sentiment = analyze_sentiment(text)
    created_at = datetime.utcnow().isoformat()

    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO reviews (text, sentiment, created_at)
            VALUES (?, ?, ?)
        ''', (text, sentiment, created_at))
        review_id = cursor.lastrowid
        conn.commit()

    return jsonify({
        "id": review_id,
        "text": text,
        "sentiment": sentiment,
        "created_at": created_at
    }), 201

@app.route("/reviews", methods=["GET"])
def get_reviews():
    sentiment = request.args.get("sentiment")
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        if sentiment:
            cursor.execute('SELECT * FROM reviews WHERE sentiment = ?', (sentiment,))
        else:
            cursor.execute('SELECT * FROM reviews')
        rows = cursor.fetchall()

    results = []
    for row in rows:
        results.append({
            "id": row[0],
            "text": row[1],
            "sentiment": row[2],
            "created_at": row[3]
        })

    return jsonify(results)

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
