from flask import Flask, json, jsonify, request
from flask_caching import Cache
from concurrent.futures import ThreadPoolExecutor
import queue
from models import( 
                   db ,add_message, create_user,delete_user,
                   get_user_by_id,get_all_users,get_users_count
                   )
from face_recognition_system import FaceRecognitionSystem

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///emotions.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False
app.config['JSON_SORT_KEYS'] = False
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

db.init_app(app)
cache_config = {
    'CACHE_TYPE': 'RedisCache',
    'CACHE_REDIS_URL': 'redis://localhost:6379/0',
    'CACHE_DEFAULT_TIMEOUT': 300
}
cache = Cache(app, config=cache_config)
task_queue = queue.Queue()
executor = ThreadPoolExecutor(max_workers=50)



system = FaceRecognitionSystem()
with app.app_context():
    db.create_all()

@app.route('/api/users/create', methods=['POST'])
def create_user():
    if request.headers.get('Content-Type') != 'application/json':
        return jsonify({"error": "Content-Type must be application/json"}), 415
    
    try:
        data = request.get_json()
        
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
            name=data['name'],
            gender=data['gender'],
            approximate_age=data['approximate_age']
        )
        system.register_face(image_path=data['face'],)
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
    if request.headers.get('Content-Type') != 'application/json':
        return jsonify({"error": "Content-Type must be application/json"}), 415
    
    try:
        data = request.get_json()
        
        required_schema = {
            "user_id": str,
            "message": str,
            "emotion": str
        }
        
        for field, field_type in required_schema.items():
            if field not in data:
                return jsonify({"error": f"Missing field: {field}"}), 400
            if not isinstance(data[field], field_type):
                return jsonify({"error": f"Field {field} must be {field_type.__name__}"}), 400
        
        add_message(
            user_id=data['user_id'],
            message=data['message'],
            emotion=data['emotion']
        )
        
        response = {
            "message": "Message added successfully"
        }
        return jsonify(response), 200
    
    except json.JSONDecodeError:
        return jsonify({"error": "Invalid JSON format"}), 400
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500   

if __name__ == '__main__':
    app.run(debug=True)