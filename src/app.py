from flask import Flask, json, jsonify, request
from flask_caching import Cache
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_cors import CORS
from concurrent.futures import ThreadPoolExecutor
from werkzeug.middleware.proxy_fix import ProxyFix
import uuid
from datetime import datetime
import json
import logging
from logging.handlers import RotatingFileHandler
from utils import EmotionAnalyzer
import queue
from models import( 
                   EmotionEntry, db , create_user,delete_user,
                   get_user_by_id,get_all_users,get_users_count,
                   check_user_exists,create_message,get_emotion_history_by_id,
                   update_user, search_users_by_name, get_message_by_id,
                   get_user_messages, get_recent_messages, search_messages_content,
                   get_messages_by_emotion, update_message, delete_message,
                   get_messages_count, get_message_emotion_history,
                   get_user_emotion_history, update_emotion_history_timestamp,
                   delete_emotion_history
                   )

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)
CORS(app, origins="*")

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///emotions.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False
app.config['JSON_SORT_KEYS'] = False
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

handler = RotatingFileHandler('app.log', maxBytes=1000000, backupCount=5)
handler.setLevel(logging.INFO)
app.logger.addHandler(handler)
app.logger.setLevel(logging.INFO)

db.init_app(app)
cache_config = {
    'CACHE_TYPE': 'SimpleCache',
    'CACHE_DEFAULT_TIMEOUT': 300
}

limiter = Limiter(
    app,
    default_limits=["200 per minute", "50 per second","1000 per 5 seconds"]
)
limiter._key_func=get_remote_address
cache = Cache(app, config=cache_config)
task_queue = queue.Queue()
executor = ThreadPoolExecutor(max_workers=100)

with app.app_context():
    db.create_all()

@app.route('/api/users/create', methods=['POST'])
@limiter.limit("200 per minute")
def create_user_route():
    if request.headers.get('Content-Type') != 'application/json':
        return jsonify({"error": "Content-Type must be application/json"}), 415
    data = request.get_json()
    print(data)
    try:
        required_schema = {
            "name": str,
            "gender": str,
            "approximate_age": int,
        }
        
        for field, field_type in required_schema.items():
            if field not in data:
                return jsonify({"error": f"Missing field: {field}"}), 400
            if not isinstance(data[field], field_type):
                return jsonify({"error": f"Field {field} must be {field_type.__name__}"}), 400
        
        new_user=create_user(
            data['name'],
            data['gender'],
            data['approximate_age']
        )
        response = {
            "message": "User created successfully",
            "user_id": new_user.user_id
        }
        return jsonify(response), 200
    
    except json.JSONDecodeError:
        return jsonify({"error": "Invalid JSON format"}), 400
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500

@app.route('/api/users/<user_id>/delete', methods=['DELETE'])
@limiter.limit("200 per minute")
def delete_user_route(user_id):
    try:
        deleted = delete_user(user_id)
        if not deleted:
            return jsonify({"error": "User not found"}), 404
        response = {
            "message": "User deleted successfully"
        }
        return jsonify(response), 200
    
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500

@app.route('/api/users/<user_id>/get', methods=['GET'])
@cache.cached(timeout=60, query_string=True)
@limiter.limit("300 per minute")
def get_user(user_id):
    if request.headers.get('Content-Type') != 'application/json':
        return jsonify({"error": "Content-Type must be application/json"}), 415
    
    try:
        user = get_user_by_id(user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        response = {
            "user_id": user.user_id,
            "name": user.name,
            "gender":user.gender,
            "age":user.approximate_age
            }
        return jsonify(response), 200
    
    except json.JSONDecodeError:
        return jsonify({"error": "Invalid JSON format"}), 400
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500  

@app.route('/api/users/get_all', methods=['GET'])
@cache.cached(timeout=60, query_string=True)
@limiter.limit("300 per minute")
def get_all_users():
    if request.headers.get('Content-Type') != 'application/json':
        return jsonify({"error": "Content-Type must be application/json"}), 415
    
    try:
        users = get_all_users()
        response = []
        for user in users:
            response.append({
                "user_id": user.user_id,
                "name": user.name,
                "gender": user.gender,
                "age": user.approximate_age
            })

        return jsonify(response), 200

    except json.JSONDecodeError:
        return jsonify({"error": "Invalid JSON format"}), 400
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500

@app.route('/api/messages/add', methods=['POST'])
def add_message_route():
    data = request.get_json()
    print(data)
    try:
        user_id = data['user_id']
        message_content = data['message_content']
        dominant_emotion = data['dominant_emotion']
        
        mas,history = create_message(
            user_id=user_id,
            content=message_content,
            dominant_emotion=dominant_emotion
        )
        emotion_history_20s = data['emotion_history_20s']
        analyzerAnalyzer = EmotionAnalyzer({'emotion_history_20s':emotion_history_20s})
        
        predictions = analyzerAnalyzer.get_full_analysis_json()
        
        history_id = history.id
        emotion = EmotionEntry(
            history_id = history_id,
            predictions=predictions   
        )
        db.session.add(emotion)
        db.session.commit()
        print(f"Analysis for user {user_id} saved successfully with history_id: {history_id}")
        
        response = {
            "message": "Message added successfully",
            "history_id":history_id,
            'predictions':predictions
        }
        return jsonify(response), 200
    
    except json.JSONDecodeError:
        return jsonify({"error": "Invalid JSON format"}), 400
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500   

@app.route('/api/history/<user_id>/get', methods=['GET'])
@cache.cached(timeout=60, query_string=True)
@limiter.limit("300 per minute")
def get_history(user_id):
    if request.headers.get('Content-Type') != 'application/json':
        return jsonify({"error": "Content-Type must be application/json"}), 415
    
    try:
        user = get_emotion_history_by_id(user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        response = {
            "timestamp": user.timestamp,
            "entries": user.entries,
        }
        return jsonify(response), 200
    
    except json.JSONDecodeError:
        return jsonify({"error": "Invalid JSON format"}), 400
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500  

@app.route('/api/users/<user_id>/update', methods=['PUT'])
@limiter.limit("200 per minute")
def update_user_route(user_id):
    if request.headers.get('Content-Type') != 'application/json':
        return jsonify({"error": "Content-Type must be application/json"}), 415
    data = request.get_json()
    try:
        updated_user = update_user(user_id, **data)
        if not updated_user:
            return jsonify({"error": "User not found"}), 404
        response = {
            "message": "User updated successfully",
            "user_id": updated_user.user_id,
            "name": updated_user.name,
            "gender": updated_user.gender,
            "age": updated_user.approximate_age
        }
        return jsonify(response), 200
    except json.JSONDecodeError:
        return jsonify({"error": "Invalid JSON format"}), 400
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500

@app.route('/api/users/search', methods=['GET'])
@cache.cached(timeout=60, query_string=True)
@limiter.limit("300 per minute")
def search_users_route():
    name = request.args.get('name')
    if not name:
        return jsonify({"error": "Missing 'name' query parameter"}), 400
    try:
        users = search_users_by_name(name)
        response = []
        for user in users:
            response.append({
                "user_id": user.user_id,
                "name": user.name,
                "gender": user.gender,
                "age": user.approximate_age
            })
        return jsonify(response), 200
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500

@app.route('/api/users/count', methods=['GET'])
@cache.cached(timeout=60)
@limiter.limit("300 per minute")
def get_users_count_route():
    try:
        count = get_users_count()
        return jsonify({"count": count}), 200
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500

@app.route('/api/messages/<message_id>/get', methods=['GET'])
@cache.cached(timeout=60, query_string=True)
@limiter.limit("300 per minute")
def get_message_route(message_id):
    try:
        message = get_message_by_id(message_id)
        if not message:
            return jsonify({"error": "Message not found"}), 404
        response = {
            "id": message.id,
            "user_id": message.user_id,
            "content": message.content,
            "timestamp": message.timestamp.isoformat(),
            "dominant_emotion": message.dominant_emotion
        }
        return jsonify(response), 200
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500

@app.route('/api/messages/user/<user_id>', methods=['GET'])
@cache.cached(timeout=60, query_string=True)
@limiter.limit("300 per minute")
def get_user_messages_route(user_id):
    limit = request.args.get('limit', type=int)
    try:
        messages = get_user_messages(user_id, limit=limit)
        response = []
        for message in messages:
            response.append({
                "id": message.id,
                "user_id": message.user_id,
                "content": message.content,
                "timestamp": message.timestamp.isoformat(),
                "dominant_emotion": message.dominant_emotion
            })
        return jsonify(response), 200
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500

@app.route('/api/messages/recent', methods=['GET'])
@cache.cached(timeout=60, query_string=True)
@limiter.limit("300 per minute")
def get_recent_messages_route():
    limit = request.args.get('limit', type=int)
    try:
        messages = get_recent_messages(limit=limit)
        response = []
        for message in messages:
            response.append({
                "id": message.id,
                "user_id": message.user_id,
                "content": message.content,
                "timestamp": message.timestamp.isoformat(),
                "dominant_emotion": message.dominant_emotion
            })
        return jsonify(response), 200
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500

@app.route('/api/messages/search_content', methods=['GET'])
@cache.cached(timeout=60, query_string=True)
@limiter.limit("300 per minute")
def search_messages_content_route():
    search_term = request.args.get('query')
    if not search_term:
        return jsonify({"error": "Missing 'query' query parameter"}), 400
    try:
        messages = search_messages_content(search_term)
        response = []
        for message in messages:
            response.append({
                "id": message.id,
                "user_id": message.user_id,
                "content": message.content,
                "timestamp": message.timestamp.isoformat(),
                "dominant_emotion": message.dominant_emotion
            })
        return jsonify(response), 200
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500

@app.route('/api/messages/by_emotion', methods=['GET'])
@cache.cached(timeout=60, query_string=True)
@limiter.limit("300 per minute")
def get_messages_by_emotion_route():
    emotion = request.args.get('emotion')
    if not emotion:
        return jsonify({"error": "Missing 'emotion' query parameter"}), 400
    try:
        messages = get_messages_by_emotion(emotion)
        response = []
        for message in messages:
            response.append({
                "id": message.id,
                "user_id": message.user_id,
                "content": message.content,
                "timestamp": message.timestamp.isoformat(),
                "dominant_emotion": message.dominant_emotion
            })
        return jsonify(response), 200
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500

@app.route('/api/messages/<message_id>/update', methods=['PUT'])
@limiter.limit("200 per minute")
def update_message_route(message_id):
    if request.headers.get('Content-Type') != 'application/json':
        return jsonify({"error": "Content-Type must be application/json"}), 415
    data = request.get_json()
    try:
        updated_message = update_message(message_id, **data)
        if not updated_message:
            return jsonify({"error": "Message not found"}), 404
        response = {
            "message": "Message updated successfully",
            "id": updated_message.id,
            "user_id": updated_message.user_id,
            "content": updated_message.content,
            "timestamp": updated_message.timestamp.isoformat(),
            "dominant_emotion": updated_message.dominant_emotion
        }
        return jsonify(response), 200
    except json.JSONDecodeError:
        return jsonify({"error": "Invalid JSON format"}), 400
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500

@app.route('/api/messages/<message_id>/delete', methods=['DELETE'])
@limiter.limit("200 per minute")
def delete_message_route(message_id):
    try:
        deleted = delete_message(message_id)
        if not deleted:
            return jsonify({"error": "Message not found"}), 404
        return jsonify({"message": "Message deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500

@app.route('/api/messages/count', methods=['GET'])
@cache.cached(timeout=60)
@limiter.limit("300 per minute")
def get_messages_count_route():
    try:
        count = get_messages_count()
        return jsonify({"count": count}), 200
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500

@app.route('/api/history/message/<message_id>', methods=['GET'])
@cache.cached(timeout=60, query_string=True)
@limiter.limit("300 per minute")
def get_message_emotion_history_route(message_id):
    try:
        history_records = get_message_emotion_history(message_id)
        if not history_records:
            return jsonify({"error": "Emotion history not found for this message"}), 404
        response = []
        for record in history_records:
            response.append({
                "id": record.id,
                "message_id": record.message_id,
                "user_id": record.user_id,
                "timestamp": record.timestamp.isoformat(),
                "entries": [{"id": entry.id, "predictions": entry.predictions} for entry in record.entries]
            })
        return jsonify(response), 200
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500

@app.route('/api/history/user/<user_id>', methods=['GET'])
@cache.cached(timeout=60, query_string=True)
@limiter.limit("300 per minute")
def get_user_emotion_history_route(user_id):
    try:
        history_records = get_user_emotion_history(user_id)
        if not history_records:
            return jsonify({"error": "Emotion history not found for this user"}), 404
        return jsonify(history_records), 200
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500

@app.route('/api/history/<history_id>/update_timestamp', methods=['PUT'])
@limiter.limit("200 per minute")
def update_emotion_history_timestamp_route(history_id):
    if request.headers.get('Content-Type') != 'application/json':
        return jsonify({"error": "Content-Type must be application/json"}), 415
    data = request.get_json()
    new_timestamp_str = data.get('new_timestamp')
    if not new_timestamp_str:
        return jsonify({"error": "Missing 'new_timestamp' field"}), 400
    try:
        new_timestamp = datetime.fromisoformat(new_timestamp_str)
        updated_history = update_emotion_history_timestamp(history_id, new_timestamp)
        if not updated_history:
            return jsonify({"error": "Emotion history not found"}), 404
        response = {
            "message": "Emotion history timestamp updated successfully",
            "id": updated_history.id,
            "timestamp": updated_history.timestamp.isoformat()
        }
        return jsonify(response), 200
    except ValueError:
        return jsonify({"error": "Invalid timestamp format. Use ISO format (YYYY-MM-DDTHH:MM:SS.ffffff)."}), 400
    except json.JSONDecodeError:
        return jsonify({"error": "Invalid JSON format"}), 400
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500

@app.route('/api/history/<history_id>/delete', methods=['DELETE'])
@limiter.limit("200 per minute")
def delete_emotion_history_route(history_id):
    try:
        deleted = delete_emotion_history(history_id)
        if not deleted:
            return jsonify({"error": "Emotion history not found"}), 404
        return jsonify({"message": "Emotion history deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

