from flask import Flask, json, jsonify, request
from flask_caching import Cache
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
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
                   check_user_exists,create_message,get_emotion_history_by_id
                   )

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

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
    'CACHE_TYPE': 'RedisCache',
    'CACHE_REDIS_URL': 'redis://localhost:6379/0',
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
    
    
    
# def background_worker():
#     while True:
#         task = task_queue.get()
#         try:
#             if task['type'] == 'create_user':
#                 create_user(**task['data'])
#             elif task['type'] == 'add_message':
#                 add_message(**task['data'])
#             task['future'].set_result('Processed successfully')
#         except Exception as e:
#             app.logger.error(f"Background task failed: {str(e)}")
#             task['future'].set_exception(e)
#         finally:
#             task_queue.task_done()

# executor.submit(background_worker)

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
def delete_user(user_id):
    if request.headers.get('Content-Type') != 'application/json':
        return jsonify({"error": "Content-Type must be application/json"}), 415
    
    try:
        delete_user(name=user_id)
        response = {
            "message": "User deleted successfully"
        }
        return jsonify(response), 200
    
    except json.JSONDecodeError:
        return jsonify({"error": "Invalid JSON format"}), 400
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
    # if request.headers.get('Content-Type') != 'application/json':
    #     return jsonify({"error": "Content-Type must be application/json"}), 415
    data = request.get_json()
    print(data)
    try:
        
        user_id = data['user_id']
        message_content = data['message_content']
        dominant_emotion = data['dominant_emotion']
        # if not check_user_exists(user_id):
        #     return jsonify({"error": f"Content-Type must be application/json{user_id}"}), 415
        
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
            "history_id":history_id
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


if __name__ == '__main__':
    app.run(debug=True)