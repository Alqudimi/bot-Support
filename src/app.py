

from flask import Flask, request, jsonify , make_response
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_caching import Cache
import os
import json
import uuid
from datetime import datetime, timedelta
import logging
from logging.handlers import RotatingFileHandler
import bcrypt
import jwt
from functools import wraps
import numpy as np

from models import (
    db, init_db, create_sample_data,
    User, UserSession, EmotionSnapshot, 
    FaceEncoding, SystemLog, EmotionStatistics
)

app = Flask(__name__)

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///emotion_analysis_face_api.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'jwt-secret-change-in-production')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=30)

CORS(app, origins="*", supports_credentials=True)

cache = Cache(app, config={'CACHE_TYPE': 'simple'})

limiter = Limiter(
    app,
    default_limits=["1000 per hour"]
)

limiter._key_func=get_remote_address
if not app.debug:
    if not os.path.exists('logs'):
        os.mkdir('logs')
    file_handler = RotatingFileHandler('logs/emotion_analysis.log', maxBytes=10240000, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('Emotion Analysis System startup')

init_db(app)

def generate_jwt_token(user_id, session_id):
    print(1111)
    
    payload = {
        'user_id': user_id,
        'session_id': session_id,
        'exp': datetime.utcnow() + app.config['JWT_ACCESS_TOKEN_EXPIRES']
    }
    print(1111)
    
    return jwt.encode(payload, app.config['JWT_SECRET_KEY'], algorithm='HS256')

def verify_jwt_token(token):
    try:
        payload = jwt.decode(token, app.config['JWT_SECRET_KEY'], algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def require_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        if token and token.startswith('Bearer '):
            token = token[7:]
            payload = verify_jwt_token(token)
            if payload:
                request.current_user_id = payload['user_id']
                request.current_session_id = payload['session_id']
                return f(*args, **kwargs)
        
        return jsonify({'success': False, 'error': 'Authentication required'}), 401
    return decorated_function

def log_system_event(event_type, message, level='info', user_id=None, session_id=None, additional_data=None):
    try:
        log_entry = SystemLog(
            event_type=event_type,
            level=level,
            message=message,
            user_id=user_id,
            session_id=session_id,
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )
        
        if additional_data:
            log_entry.set_additional_data(additional_data)
        
        db.session.add(log_entry)
        db.session.commit()
        
    except Exception as e:
        app.logger.error(f"Failed to log system event: {e}")


@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '2.0.0-face-api',
        'database': 'connected',
        'cache': 'active'
    })


@app.route('/api/auth/register', methods=['POST'])
def register_user():
    data = request.get_json()
    print(data)
    try:
        
        if not data.get('name'):
            return jsonify({'success': False, 'error': 'Name is required'}), 400
        
        if data.get('email'):
            existing_user = User.query.filter_by(email=data['email']).first()
            if existing_user:
                return jsonify({'success': False, 'error': 'Email already exists'}), 400
        
        user = User(
            name=data['name'],
            email=data.get('email'),
            detected_gender=data.get('detected_gender'),
            detected_age=data.get('detected_age'),
            gender_confidence=data.get('gender_confidence'),
            age_confidence=data.get('age_confidence'),
            is_guest=False
        )
        
        print(1111)
        if data.get('password'):
            password_hash = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt())
            user.password_hash = password_hash.decode('utf-8')
        print(1111)
        
        db.session.add(user)
        db.session.commit()
        
        session_obj = UserSession(
            user_id=user.id,
            user_agent=request.headers.get('User-Agent'),
            ip_address=request.remote_addr
        )
        print(1111)
        
        db.session.add(session_obj)
        db.session.commit()
        
        print(1111)
        
        jwt_token = generate_jwt_token(user.id, session_obj.session_id)
        print(1111)
        
        log_system_event(
            'user_registration', 
            f'New user registered: {user.name}',
            user_id=user.id,
            session_id=session_obj.session_id,
            additional_data={
                'detected_gender': user.detected_gender,
                'detected_age': user.detected_age,
                'gender_confidence': user.gender_confidence,
                'age_confidence': user.age_confidence
            }
        )
        print(1111)
        
        return jsonify({
            'success': True,
            'message': 'User registered successfully',
            'user': user.to_dict(),
            'session_id': session_obj.session_id,
            'jwt_token': jwt_token
        }), 201
        
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Registration error: {e}")
        return jsonify({'success': False, 'error': 'Registration failed'}), 500

@app.route('/api/auth/guest', methods=['POST'])
@limiter.limit("20 per minute")
def create_guest_session():
    try:
        data = request.get_json() or {}
        
        guest_name = data.get('name', f'ضيف_{datetime.now().strftime("%Y%m%d_%H%M%S")}')
        
        user = User(
            name=guest_name,
            detected_gender=data.get('detected_gender'),
            detected_age=data.get('detected_age'),
            gender_confidence=data.get('gender_confidence'),
            age_confidence=data.get('age_confidence'),
            is_guest=True
        )
        
        db.session.add(user)
        db.session.commit()
        
        session_obj = UserSession(
            user_id=user.id,
            user_agent=request.headers.get('User-Agent'),
            ip_address=request.remote_addr
        )
        
        db.session.add(session_obj)
        db.session.commit()
        
        log_system_event(
            'guest_session_created',
            f'Guest session created: {user.name}',
            user_id=user.id,
            session_id=session_obj.session_id
        )
        
        return jsonify({
            'success': True,
            'message': 'Guest session created successfully',
            'user': user.to_dict(),
            'session_id': session_obj.session_id
        }), 201
        
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Guest session error: {e}")
        return jsonify({'success': False, 'error': 'Failed to create guest session'}), 500

@app.route('/api/auth/login', methods=['POST'])
@limiter.limit("10 per minute")
def login_user():
    try:
        data = request.get_json()
        
        if not data.get('email') or not data.get('password'):
            return jsonify({'success': False, 'error': 'Email and password required'}), 400
        
        user = User.query.filter_by(email=data['email'], is_active=True).first()
        
        if not user or not user.password_hash:
            return jsonify({'success': False, 'error': 'Invalid credentials'}), 401
        
        if not bcrypt.checkpw(data['password'].encode('utf-8'), user.password_hash.encode('utf-8')):
            return jsonify({'success': False, 'error': 'Invalid credentials'}), 401
        
        user.last_seen = datetime.utcnow()
        
        session_obj = UserSession(
            user_id=user.id,
            user_agent=request.headers.get('User-Agent'),
            ip_address=request.remote_addr
        )
        
        db.session.add(session_obj)
        db.session.commit()
        
        jwt_token = generate_jwt_token(user.id, session_obj.session_id)
        
        log_system_event(
            'user_login',
            f'User logged in: {user.name}',
            user_id=user.id,
            session_id=session_obj.session_id
        )
        
        return jsonify({
            'success': True,
            'message': 'Login successful',
            'user': user.to_dict(),
            'session_id': session_obj.session_id,
            'jwt_token': jwt_token
        })
        
    except Exception as e:
        app.logger.error(f"Login error: {e}")
        return jsonify({'success': False, 'error': 'Login failed'}), 500

@app.route('/api/auth/logout', methods=['POST'])
def logout_user():
    try:
        session_id = request.headers.get('X-Session-ID')
        
        if session_id:
            session_obj = UserSession.query.filter_by(session_id=session_id, is_active=True).first()
            if session_obj:
                session_obj.is_active = False
                session_obj.end_time = datetime.utcnow()
                db.session.commit()
                
                log_system_event(
                    'user_logout',
                    'User logged out',
                    user_id=session_obj.user_id,
                    session_id=session_id
                )
        
        return jsonify({'success': True, 'message': 'Logout successful'})
        
    except Exception as e:
        app.logger.error(f"Logout error: {e}")
        return jsonify({'success': False, 'error': 'Logout failed'}), 500


@app.route('/api/emotions/analyze', methods=['POST'])
@limiter.limit("100 per minute")
def analyze_emotions():
    try:
        data = request.get_json()
        session_id = request.headers.get('X-Session-ID')
        
        if not session_id:
            return jsonify({'success': False, 'error': 'Session ID required'}), 400
        
        session_obj = UserSession.query.filter_by(session_id=session_id, is_active=True).first()
        if not session_obj:
            return jsonify({'success': False, 'error': 'Invalid session'}), 401
        
        emotions_data = data.get('emotions', {})
        face_data = data.get('face_data', {})
        age_gender_data = data.get('age_gender_data', {})
        
        dominant_emotion = 'neutral'
        emotion_intensity = 0.0
        
        if emotions_data:
            dominant_emotion = max(emotions_data, key=emotions_data.get)
            emotion_intensity = emotions_data.get(dominant_emotion, 0.0) / 100.0
        
        snapshot = EmotionSnapshot(
            user_id=session_obj.user_id,
            session_id=session_id,
            dominant_emotion=dominant_emotion,
            emotion_intensity=emotion_intensity,
            face_detected=face_data.get('face_detected', False),
            face_count=face_data.get('face_count', 0),
            face_confidence=face_data.get('face_confidence'),
            detected_age=age_gender_data.get('age'),
            detected_gender=age_gender_data.get('gender'),
            age_confidence=age_gender_data.get('age_confidence'),
            gender_confidence=age_gender_data.get('gender_confidence'),
            is_manual_save=data.get('manual_save', False)
        )
        
        snapshot.set_emotions_data(emotions_data)
        
        if face_data.get('face_box'):
            snapshot.set_face_box(face_data['face_box'])
        
        db.session.add(snapshot)
        
        session_obj.total_snapshots += 1
        session_obj.user.last_seen = datetime.utcnow()
        
        user = session_obj.user
        if age_gender_data.get('age') and age_gender_data.get('age_confidence', 0) > (user.age_confidence or 0):
            user.detected_age = int(age_gender_data['age'])
            user.age_confidence = age_gender_data['age_confidence']
        
        if age_gender_data.get('gender') and age_gender_data.get('gender_confidence', 0) > (user.gender_confidence or 0):
            user.detected_gender = age_gender_data['gender']
            user.gender_confidence = age_gender_data['gender_confidence']
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Emotions analyzed successfully',
            'analysis': {
                'dominant_emotion': dominant_emotion,
                'emotion_intensity': emotion_intensity,
                'face_detected': face_data.get('face_detected', False),
                'processed_at': datetime.utcnow().isoformat()
            },
            'saved': True,
            'auto_save_interval': 5
        })
        
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Emotion analysis error: {e}")
        return jsonify({'success': False, 'error': 'Analysis failed'}), 500

@app.route('/api/emotions/snapshot', methods=['POST'])
@limiter.limit("20 per minute")
def save_emotion_snapshot():
    try:
        data = request.get_json()
        session_id = request.headers.get('X-Session-ID')
        
        if not session_id:
            return jsonify({'success': False, 'error': 'Session ID required'}), 400
        
        session_obj = UserSession.query.filter_by(session_id=session_id, is_active=True).first()
        if not session_obj:
            return jsonify({'success': False, 'error': 'Invalid session'}), 401
        
        snapshot = EmotionSnapshot(
            user_id=session_obj.user_id,
            session_id=session_id,
            dominant_emotion=data.get('dominant_emotion', 'neutral'),
            emotion_intensity=data.get('emotion_intensity', 0.0),
            face_detected=data.get('face_data', {}).get('face_detected', False),
            face_count=data.get('face_data', {}).get('face_count', 0),
            face_confidence=data.get('face_data', {}).get('face_confidence'),
            detected_age=data.get('age_gender_data', {}).get('age'),
            detected_gender=data.get('age_gender_data', {}).get('gender'),
            age_confidence=data.get('age_gender_data', {}).get('age_confidence'),
            gender_confidence=data.get('age_gender_data', {}).get('gender_confidence'),
            is_manual_save=True,
            note=data.get('note')
        )
        
        if data.get('emotions_data'):
            snapshot.set_emotions_data(data['emotions_data'])
        
        db.session.add(snapshot)
        db.session.commit()
        
        log_system_event(
            'manual_snapshot_saved',
            f'Manual emotion snapshot saved: {snapshot.dominant_emotion}',
            user_id=session_obj.user_id,
            session_id=session_id,
            additional_data={'emotion_intensity': snapshot.emotion_intensity}
        )
        
        return jsonify({
            'success': True,
            'message': 'Snapshot saved successfully',
            'snapshot': snapshot.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Snapshot save error: {e}")
        return jsonify({'success': False, 'error': 'Failed to save snapshot'}), 500


@app.route('/api/faces/recognize', methods=['POST'])
@limiter.limit("50 per minute")
def recognize_face():
    """التعرف على وجه باستخدام face-api.js encoding"""
    try:
        data = request.get_json()
        session_id = request.headers.get('X-Session-ID')
        
        if not session_id:
            return jsonify({'success': False, 'error': 'Session ID required'}), 400
        
        face_encoding = data.get('face_encoding')
        if not face_encoding or len(face_encoding) != 128:
            return jsonify({'success': False, 'error': 'Valid face encoding required (128 values)'}), 400
        
        known_faces = FaceEncoding.query.all()
        
        best_match = None
        best_distance = float('inf')
        confidence_threshold = data.get('confidence_threshold', 0.6)
        
        for known_face in known_faces:
            known_encoding = known_face.get_encoding_data()
            if len(known_encoding) == 128:
                distance = np.linalg.norm(np.array(face_encoding) - np.array(known_encoding))
                
                if distance < best_distance and distance < confidence_threshold:
                    best_distance = distance
                    best_match = known_face
        
        if best_match:
            best_match.last_used = datetime.utcnow()
            best_match.usage_count += 1
            db.session.commit()
            
            log_system_event(
                'face_recognized',
                f'Face recognized: {best_match.user.name}',
                user_id=best_match.user_id,
                session_id=session_id,
                additional_data={'confidence': 1 - best_distance, 'distance': best_distance}
            )
            
            return jsonify({
                'success': True,
                'recognized': True,
                'user': best_match.user.to_dict(),
                'confidence': 1 - best_distance,
                'face_id': best_match.id
            })
        else:
            return jsonify({
                'success': True,
                'recognized': False,
                'message': 'No matching face found'
            })
        
    except Exception as e:
        app.logger.error(f"Face recognition error: {e}")
        return jsonify({'success': False, 'error': 'Face recognition failed'}), 500

@app.route('/api/faces/add', methods=['POST'])
@require_auth
@limiter.limit("10 per minute")
def add_face_encoding():
    try:
        data = request.get_json()
        user_id = request.current_user_id
        
        face_encoding = data.get('face_encoding')
        if not face_encoding or len(face_encoding) != 128:
            return jsonify({'success': False, 'error': 'Valid face encoding required (128 values)'}), 400
        
        face_enc = FaceEncoding(
            user_id=user_id,
            label=data.get('label', 'الوجه الرئيسي'),
            confidence_threshold=data.get('confidence_threshold', 0.6),
            face_quality_score=data.get('face_quality_score')
        )
        
        face_enc.set_encoding_data(face_encoding)
        
        db.session.add(face_enc)
        db.session.commit()
        
        log_system_event(
            'face_encoding_added',
            f'Face encoding added for user: {user_id}',
            user_id=user_id,
            session_id=request.current_session_id
        )
        
        return jsonify({
            'success': True,
            'message': 'Face encoding added successfully',
            'face_encoding': face_enc.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Add face encoding error: {e}")
        return jsonify({'success': False, 'error': 'Failed to add face encoding'}), 500


@app.route('/api/stats/user/<int:user_id>', methods=['GET'])
def get_user_stats():
    """الحصول على إحصائيات المستخدم"""
    try:
        session_id = request.headers.get('X-Session-ID')
        period = request.args.get('period', 'week')  # day, week, month
        
        session_obj = UserSession.query.filter_by(session_id=session_id, is_active=True).first()
        if not session_obj or session_obj.user_id != user_id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        if period == 'day':
            start_date = datetime.utcnow() - timedelta(days=1)
        elif period == 'week':
            start_date = datetime.utcnow() - timedelta(weeks=1)
        elif period == 'month':
            start_date = datetime.utcnow() - timedelta(days=30)
        else:
            start_date = datetime.utcnow() - timedelta(weeks=1)
        
        snapshots = EmotionSnapshot.query.filter(
            EmotionSnapshot.user_id == user_id,
            EmotionSnapshot.timestamp >= start_date
        ).all()
        
        total_snapshots = len(snapshots)
        emotion_distribution = {}
        total_analysis_time = 0
        
        for snapshot in snapshots:
            emotion = snapshot.dominant_emotion
            emotion_distribution[emotion] = emotion_distribution.get(emotion, 0) + 1
        
        if total_snapshots > 0:
            for emotion in emotion_distribution:
                emotion_distribution[emotion] = round(
                    (emotion_distribution[emotion] / total_snapshots) * 100, 1
                )
        
        sessions = UserSession.query.filter_by(user_id=user_id).all()
        total_sessions = len(sessions)
        
        return jsonify({
            'success': True,
            'stats': {
                'user_id': user_id,
                'period': period,
                'total_sessions': total_sessions,
                'total_snapshots': total_snapshots,
                'emotion_distribution': emotion_distribution,
                'analysis_period': {
                    'start': start_date.isoformat(),
                    'end': datetime.utcnow().isoformat()
                }
            }
        })
        
    except Exception as e:
        app.logger.error(f"User stats error: {e}")
        return jsonify({'success': False, 'error': 'Failed to get user stats'}), 500

@app.route('/api/stats/system', methods=['GET'])
def get_system_stats():
    try:
        total_users = User.query.count()
        total_guests = User.query.filter_by(is_guest=True).count()
        total_registered = total_users - total_guests
        
        today = datetime.utcnow().date()
        active_today = User.query.filter(
            User.last_seen >= datetime.combine(today, datetime.min.time())
        ).count()
        
        total_sessions = UserSession.query.count()
        total_snapshots = EmotionSnapshot.query.count()
        
        emotion_stats = db.session.query(
            EmotionSnapshot.dominant_emotion,
            db.func.count(EmotionSnapshot.id)
        ).group_by(EmotionSnapshot.dominant_emotion).all()
        
        emotion_distribution = {emotion: count for emotion, count in emotion_stats}
        
        return jsonify({
            'success': True,
            'system_stats': {
                'total_users': total_users,
                'registered_users': total_registered,
                'guest_users': total_guests,
                'active_users_today': active_today,
                'total_sessions': total_sessions,
                'total_snapshots': total_snapshots,
                'emotion_distribution': emotion_distribution,
                'timestamp': datetime.utcnow().isoformat()
            }
        })
        
    except Exception as e:
        app.logger.error(f"System stats error: {e}")
        return jsonify({'success': False, 'error': 'Failed to get system stats'}), 500


@app.route('/api/admin/cleanup', methods=['POST'])
@require_auth
def cleanup_old_data():
    try:
        days = int(request.args.get('days', 30))
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        expired_sessions = UserSession.query.filter(
            UserSession.expires_at < datetime.utcnow(),
            UserSession.is_active == False
        ).count()
        
        UserSession.query.filter(
            UserSession.expires_at < datetime.utcnow(),
            UserSession.is_active == False
        ).delete()
        
        old_logs = SystemLog.query.filter(SystemLog.timestamp < cutoff_date).count()
        SystemLog.query.filter(SystemLog.timestamp < cutoff_date).delete()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Cleanup completed successfully',
            'cleaned': {
                'expired_sessions': expired_sessions,
                'old_logs': old_logs
            }
        })
        
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Cleanup error: {e}")
        return jsonify({'success': False, 'error': 'Cleanup failed'}), 500


@app.errorhandler(404)
def not_found(error):
    return jsonify({'success': False, 'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return jsonify({'success': False, 'error': 'Internal server error'}), 500

@app.errorhandler(429)
def ratelimit_handler(e):
    return jsonify({'success': False, 'error': 'Rate limit exceeded'}), 429

@app.route('/api/dashboard/stats', methods=['GET'])
def get_dashboard_stats():
    try:
        total_users = User.query.count()
        active_users_today = UserSession.query.filter(
            UserSession.start_time >= datetime.utcnow().date()
        ).count()
        total_snapshots = EmotionSnapshot.query.count()
        total_sessions = UserSession.query.count()
        
        emotion_counts = db.session.query(
            EmotionSnapshot.dominant_emotion,
            db.func.count(EmotionSnapshot.id)
        ).group_by(EmotionSnapshot.dominant_emotion).all()
        
        emotion_distribution = {}
        for emotion, count in emotion_counts:
            emotion_distribution[emotion] = count
        
        return jsonify({
            'success': True,
            'data': {
                'total_users': total_users,
                'active_users_today': active_users_today,
                'total_snapshots': total_snapshots,
                'total_sessions': total_sessions,
                'emotion_distribution': emotion_distribution
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/dashboard/active-sessions', methods=['GET'])
def get_active_sessions():
    try:
        sessions = UserSession.query.filter(
            UserSession.end_time.is_(None)
        ).order_by(UserSession.start_time.desc()).limit(10).all()
        
        sessions_data = []
        for session in sessions:
            user = User.query.get(session.user_id)
            snapshots_count = EmotionSnapshot.query.filter_by(session_id=session.id).count()
            
            duration = datetime.utcnow() - session.start_time
            duration_str = f"{duration.seconds // 60}:{duration.seconds % 60:02d}"
            
            sessions_data.append({
                'id': session.id,
                'user_name': user.name if user else f"ضيف_{session.id}",
                'user_type': 'مسجل' if user and not user.is_guest else 'ضيف',
                'start_time': session.start_time.strftime('%Y-%m-%d %H:%M:%S'),
                'duration': duration_str,
                'snapshots': snapshots_count,
                'status': 'نشط'
            })
        
        return jsonify({
            'success': True,
            'data': sessions_data
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/dashboard/system-logs', methods=['GET'])
def get_system_logs():
    try:
        level_filter = request.args.get('level', 'all')
        
        query = SystemLog.query
        if level_filter != 'all':
            query = query.filter_by(level=level_filter)
        
        logs = query.order_by(SystemLog.timestamp.desc()).limit(50).all()
        
        logs_data = []
        for log in logs:
            user = User.query.get(log.user_id) if log.user_id else None
            logs_data.append({
                'id': log.id,
                'timestamp': log.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                'level': log.level,
                'event_type': log.event_type,
                'message': log.message,
                'user_name': user.name if user else '-'
            })
        
        return jsonify({
            'success': True,
            'data': logs_data
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/statistics/overview', methods=['GET'])
def get_statistics_overview():
    """جلب إحصائيات شاملة"""
    try:
        period = request.args.get('period', 'week')
        
        end_date = datetime.utcnow()
        if period == 'today':
            start_date = end_date.replace(hour=0, minute=0, second=0, microsecond=0)
        elif period == 'week':
            start_date = end_date - timedelta(days=7)
        elif period == 'month':
            start_date = end_date - timedelta(days=30)
        elif period == 'year':
            start_date = end_date - timedelta(days=365)
        else:
            start_date = end_date - timedelta(days=7)
        
        total_analyses = EmotionSnapshot.query.filter(
            EmotionSnapshot.timestamp >= start_date
        ).count()
        
        avg_session_duration = db.session.query(
            db.func.avg(
                db.func.julianday(UserSession.end_time) - 
                db.func.julianday(UserSession.start_time)
            ) * 24 * 60  
        ).filter(
            UserSession.start_time >= start_date,
            UserSession.end_time.isnot(None)
        ).scalar() or 0
        
        unique_users = db.session.query(
            db.func.count(db.func.distinct(EmotionSnapshot.user_id))
        ).filter(
            EmotionSnapshot.timestamp >= start_date
        ).scalar() or 0
        
        face_detection_accuracy = 94.5
        
        emotion_distribution = db.session.query(
            EmotionSnapshot.dominant_emotion,
            db.func.count(EmotionSnapshot.id)
        ).filter(
            EmotionSnapshot.timestamp >= start_date
        ).group_by(EmotionSnapshot.dominant_emotion).all()
        
        emotions_data = {}
        for emotion, count in emotion_distribution:
            emotions_data[emotion] = count
        
        emotion_trends = {}
        for i in range(7):
            date = (end_date - timedelta(days=i)).date()
            day_emotions = db.session.query(
                EmotionSnapshot.dominant_emotion,
                db.func.count(EmotionSnapshot.id)
            ).filter(
                db.func.date(EmotionSnapshot.timestamp) == date
            ).group_by(EmotionSnapshot.dominant_emotion).all()
            
            emotion_trends[date.strftime('%Y-%m-%d')] = dict(day_emotions)
        
        return jsonify({
            'success': True,
            'data': {
                'overview': {
                    'total_emotion_analyses': total_analyses,
                    'avg_session_duration': round(avg_session_duration, 1),
                    'face_detection_accuracy': face_detection_accuracy,
                    'unique_users': unique_users
                },
                'emotion_distribution': emotions_data,
                'emotion_trends': emotion_trends,
                'period': period
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/users/list', methods=['GET'])
def get_users_list():
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        search = request.args.get('search', '')
        user_type = request.args.get('type', 'all')
        status = request.args.get('status', 'all')
        
        query = User.query
        
        if search:
            query = query.filter(
                db.or_(
                    User.name.contains(search),
                    User.email.contains(search)
                )
            )
        
        if user_type != 'all':
            if user_type == 'guest':
                query = query.filter_by(is_guest=True)
            else:
                query = query.filter_by(is_guest=False)
        
        if status != 'all':
            if status == 'active':
                yesterday = datetime.utcnow() - timedelta(days=1)
                active_user_ids = db.session.query(UserSession.user_id).filter(
                    UserSession.start_time >= yesterday
                ).distinct().subquery()
                query = query.filter(User.id.in_(active_user_ids))
        
        pagination = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        users_data = []
        for user in pagination.items:
            sessions_count = UserSession.query.filter_by(user_id=user.id).count()
            
            last_session = UserSession.query.filter_by(user_id=user.id).order_by(
                UserSession.start_time.desc()
            ).first()
            
            last_activity = last_session.start_time if last_session else user.created_at
            
            yesterday = datetime.utcnow() - timedelta(days=1)
            is_active = last_activity >= yesterday
            
            users_data.append({
                'id': user.id,
                'name': user.name,
                'type': 'guest' if user.is_guest else 'registered',
                'gender': user.gender or 'غير محدد',
                'age': user.age or 0,
                'email': user.email or '-',
                'registration_date': user.created_at.strftime('%Y-%m-%d'),
                'last_activity': last_activity.strftime('%Y-%m-%d %H:%M:%S'),
                'sessions': sessions_count,
                'status': 'active' if is_active else 'inactive'
            })
        
        return jsonify({
            'success': True,
            'data': {
                'users': users_data,
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': pagination.total,
                    'pages': pagination.pages,
                    'has_prev': pagination.has_prev,
                    'has_next': pagination.has_next
                }
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/users/<int:user_id>', methods=['GET'])
def get_user_details(user_id):
    try:
        user = User.query.get_or_404(user_id)
        
        sessions_count = UserSession.query.filter_by(user_id=user.id).count()
        snapshots_count = EmotionSnapshot.query.filter_by(user_id=user.id).count()
        
        last_session = UserSession.query.filter_by(user_id=user.id).order_by(
            UserSession.start_time.desc()
        ).first()
        
        user_emotions = db.session.query(
            EmotionSnapshot.dominant_emotion,
            db.func.count(EmotionSnapshot.id)
        ).filter_by(user_id=user.id).group_by(
            EmotionSnapshot.dominant_emotion
        ).all()
        
        emotion_distribution = dict(user_emotions)
        
        user_data = {
            'id': user.id,
            'name': user.name,
            'email': user.email,
            'gender': user.gender,
            'age': user.age,
            'is_guest': user.is_guest,
            'created_at': user.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': user.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
            'stats': {
                'sessions_count': sessions_count,
                'snapshots_count': snapshots_count,
                'last_session': last_session.start_time.strftime('%Y-%m-%d %H:%M:%S') if last_session else None,
                'emotion_distribution': emotion_distribution
            }
        }
        
        return jsonify({
            'success': True,
            'data': user_data
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    try:
        user = User.query.get_or_404(user_id)
        data = request.get_json()
        
        if 'name' in data:
            user.name = data['name']
        if 'email' in data:
            user.email = data['email']
        if 'status' in data:
            pass
        
        user.updated_at = datetime.utcnow()
        db.session.commit()
        
        log_entry = SystemLog(
            level='info',
            event_type='user_update',
            message=f'تم تحديث بيانات المستخدم {user.name}',
            user_id=user.id
        )
        db.session.add(log_entry)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'تم تحديث بيانات المستخدم بنجاح'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    try:
        user = User.query.get_or_404(user_id)
        user_name = user.name
        
        EmotionSnapshot.query.filter_by(user_id=user.id).delete()
        UserSession.query.filter_by(user_id=user.id).delete()
        SystemLog.query.filter_by(user_id=user.id).delete()
        
        db.session.delete(user)
        db.session.commit()
        
        log_entry = SystemLog(
            level='warning',
            event_type='user_delete',
            message=f'تم حذف المستخدم {user_name}'
        )
        db.session.add(log_entry)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'تم حذف المستخدم بنجاح'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/users/stats', methods=['GET'])
def get_users_stats():
    try:
        total_users = User.query.count()
        registered_users = User.query.filter_by(is_guest=False).count()
        guest_users = User.query.filter_by(is_guest=True).count()
        
        today = datetime.utcnow().date()
        active_today = db.session.query(
            db.func.count(db.func.distinct(UserSession.user_id))
        ).filter(
            db.func.date(UserSession.start_time) == today
        ).scalar() or 0
        
        return jsonify({
            'success': True,
            'data': {
                'total': total_users,
                'registered': registered_users,
                'guest': guest_users,
                'active_today': active_today
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    with app.app_context():
        if app.debug:
            try:
                create_sample_data()
            except:
                pass
    
    
    
    app.run(host='0.0.0.0', port=5000, debug=True)




