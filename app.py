# app.py - без внешних API запросов
import os
import json
import logging
import random
from datetime import datetime
from flask import Flask, render_template, request, jsonify, session
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key')

# Эмуляция классификации (работает без интернета)
def classify_text(text):
    """Эмуляция классификации текста"""
    # Простая эмуляция на основе ключевых слов
    positive_words = ['хорош', 'отличн', 'прекрасн', 'замечательн', 'нравит', 'люблю', 'великолепн', 'супер', 'классн', 'крут']
    negative_words = ['плох', 'ужасн', 'отвратительн', 'разочарован', 'ненавиж', 'ужасн', 'кошмарн', 'мусор', 'бесполезн', 'отврат']
    
    text_lower = text.lower()
    
    positive_score = sum(1 for word in positive_words if word in text_lower)
    negative_score = sum(1 for word in negative_words if word in text_lower)
    
    if positive_score > negative_score:
        return [
            {'label': 'POSITIVE', 'score': round(0.7 + random.random() * 0.25, 4)},
            {'label': 'NEGATIVE', 'score': round(random.random() * 0.3, 4)}
        ]
    elif negative_score > positive_score:
        return [
            {'label': 'NEGATIVE', 'score': round(0.7 + random.random() * 0.25, 4)},
            {'label': 'POSITIVE', 'score': round(random.random() * 0.3, 4)}
        ]
    else:
        return [
            {'label': 'NEUTRAL', 'score': round(0.6 + random.random() * 0.3, 4)},
            {'label': 'POSITIVE', 'score': round(random.random() * 0.2, 4)},
            {'label': 'NEGATIVE', 'score': round(random.random() * 0.2, 4)}
        ]

@app.route('/')
def index():
    session.pop('last_result', None)
    return render_template('index.html')

@app.route('/classify', methods=['POST'])
def classify():
    try:
        data = request.get_json()
        if not data or 'text' not in data:
            return jsonify({'error': 'Текст не предоставлен'}), 400
        
        text = data['text'].strip()
        if not text:
            return jsonify({'error': 'Текст пустой'}), 400
        
        logger.info(f"Классификация текста: {text[:50]}...")
        
        # Используем эмуляцию
        result = classify_text(text)
        
        session['last_result'] = {
            'text': text,
            'result': result,
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify({'result': result})
        
    except Exception as e:
        logger.error(f"Ошибка: {e}")
        return jsonify({'error': f'Ошибка: {str(e)}'}), 500

@app.route('/save', methods=['POST'])
def save_result():
    try:
        data = request.get_json()
        if not data or 'text' not in data or 'result' not in data:
            return jsonify({'error': 'Недостаточно данных'}), 400
        
        record = {
            'text': data['text'],
            'result': data['result'],
            'timestamp': datetime.now().isoformat()
        }
        
        history_file = 'history.json'
        history = []
        if os.path.exists(history_file):
            try:
                with open(history_file, 'r', encoding='utf-8') as f:
                    history = json.load(f)
            except:
                history = []
        
        history.append(record)
        
        if len(history) > 100:
            history = history[-100:]
        
        with open(history_file, 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
        
        return jsonify({'success': True, 'message': 'Результат сохранен'})
        
    except Exception as e:
        logger.error(f"Ошибка сохранения: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/history', methods=['GET'])
def get_history():
    history_file = 'history.json'
    if os.path.exists(history_file):
        try:
            with open(history_file, 'r', encoding='utf-8') as f:
                history = json.load(f)
            return jsonify({'history': history[-20:]})
        except:
            return jsonify({'history': []})
    return jsonify({'history': []})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)