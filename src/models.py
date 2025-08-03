

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import json
import uuid

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    password_hash = db.Column(db.String(255), nullable=True)
    
    detected_gender = db.Column(db.String(20), nullable=True)  
    detected_age = db.Column(db.Integer, nullable=True)
    gender_confidence = db.Column(db.Float, nullable=True)
    age_confidence = db.Column(db.Float, nullable=True)
    
    is_guest = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    
    sessions = db.relationship('UserSession', backref='user', lazy=True, cascade='all, delete-orphan')
    emotion_snapshots = db.relationship('EmotionSnapshot', backref='user', lazy=True, cascade='all, delete-orphan')
    face_encodings = db.relationship('FaceEncoding', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'detected_gender': self.detected_gender,
            'detected_age': self.detected_age,
            'gender_confidence': self.gender_confidence,
            'age_confidence': self.age_confidence,
            'is_guest': self.is_guest,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_seen': self.last_seen.isoformat() if self.last_seen else None
        }

class UserSession(db.Model):
    __tablename__ = 'user_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(100), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    start_time = db.Column(db.DateTime, default=datetime.utcnow)
    end_time = db.Column(db.DateTime, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    expires_at = db.Column(db.DateTime, default=lambda: datetime.utcnow() + timedelta(days=30))
    
    user_agent = db.Column(db.Text, nullable=True)
    ip_address = db.Column(db.String(45), nullable=True)
    browser_info = db.Column(db.Text, nullable=True)
    
    total_snapshots = db.Column(db.Integer, default=0)
    total_analysis_time = db.Column(db.Integer, default=0)  
    
    def to_dict(self):
        return {
            'id': self.id,
            'session_id': self.session_id,
            'user_id': self.user_id,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'is_active': self.is_active,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'total_snapshots': self.total_snapshots,
            'total_analysis_time': self.total_analysis_time
        }

class EmotionSnapshot(db.Model):
    __tablename__ = 'emotion_snapshots'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    session_id = db.Column(db.String(100), nullable=False)
    
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    emotions_data = db.Column(db.Text, nullable=False) 
    dominant_emotion = db.Column(db.String(50), nullable=False)
    emotion_intensity = db.Column(db.Float, nullable=False)
    
    face_detected = db.Column(db.Boolean, default=False)
    face_count = db.Column(db.Integer, default=0)
    face_confidence = db.Column(db.Float, nullable=True)
    face_box = db.Column(db.Text, nullable=True) 
    
    detected_age = db.Column(db.Float, nullable=True)
    detected_gender = db.Column(db.String(20), nullable=True)
    age_confidence = db.Column(db.Float, nullable=True)
    gender_confidence = db.Column(db.Float, nullable=True)
    
    is_manual_save = db.Column(db.Boolean, default=False)
    note = db.Column(db.Text, nullable=True)
    
    __table_args__ = (
        db.Index('idx_user_timestamp', 'user_id', 'timestamp'),
        db.Index('idx_session_timestamp', 'session_id', 'timestamp'),
        db.Index('idx_dominant_emotion', 'dominant_emotion'),
    )
    
    def get_emotions_data(self):
        try:
            return json.loads(self.emotions_data) if self.emotions_data else {}
        except:
            return {}
    
    def set_emotions_data(self, data):
        """حفظ بيانات المشاعر كـ JSON"""
        self.emotions_data = json.dumps(data) if data else '{}'
    
    def get_face_box(self):
        """استخراج إحداثيات الوجه من JSON"""
        try:
            return json.loads(self.face_box) if self.face_box else {}
        except:
            return {}
    
    def set_face_box(self, box_data):
        """حفظ إحداثيات الوجه كـ JSON"""
        self.face_box = json.dumps(box_data) if box_data else '{}'
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'session_id': self.session_id,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'emotions_data': self.get_emotions_data(),
            'dominant_emotion': self.dominant_emotion,
            'emotion_intensity': self.emotion_intensity,
            'face_detected': self.face_detected,
            'face_count': self.face_count,
            'face_confidence': self.face_confidence,
            'face_box': self.get_face_box(),
            'detected_age': self.detected_age,
            'detected_gender': self.detected_gender,
            'age_confidence': self.age_confidence,
            'gender_confidence': self.gender_confidence,
            'is_manual_save': self.is_manual_save,
            'note': self.note
        }

class FaceEncoding(db.Model):
    __tablename__ = 'face_encodings'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    encoding_data = db.Column(db.Text, nullable=False)  
    label = db.Column(db.String(100), nullable=True)
    confidence_threshold = db.Column(db.Float, default=0.6)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_used = db.Column(db.DateTime, nullable=True)
    usage_count = db.Column(db.Integer, default=0)
    
    face_image_path = db.Column(db.String(255), nullable=True)
    face_quality_score = db.Column(db.Float, nullable=True)
    
    def get_encoding_data(self):
        try:
            return json.loads(self.encoding_data) if self.encoding_data else []
        except:
            return []
    
    def set_encoding_data(self, data):
        self.encoding_data = json.dumps(data) if data else '[]'
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'encoding_data': self.get_encoding_data(),
            'label': self.label,
            'confidence_threshold': self.confidence_threshold,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_used': self.last_used.isoformat() if self.last_used else None,
            'usage_count': self.usage_count,
            'face_quality_score': self.face_quality_score
        }

class SystemLog(db.Model):
    __tablename__ = 'system_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    event_type = db.Column(db.String(50), nullable=False)  
    level = db.Column(db.String(20), default='info')
    
    message = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, nullable=True)
    session_id = db.Column(db.String(100), nullable=True)
    
    ip_address = db.Column(db.String(45), nullable=True)
    user_agent = db.Column(db.Text, nullable=True)
    additional_data = db.Column(db.Text, nullable=True)  
    
    __table_args__ = (
        db.Index('idx_timestamp', 'timestamp'),
        db.Index('idx_event_type', 'event_type'),
        db.Index('idx_level', 'level'),
        db.Index('idx_user_id', 'user_id'),
    )
    
    def get_additional_data(self):
        try:
            return json.loads(self.additional_data) if self.additional_data else {}
        except:
            return {}
    
    def set_additional_data(self, data):
        self.additional_data = json.dumps(data) if data else '{}'
    
    def to_dict(self):
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'event_type': self.event_type,
            'level': self.level,
            'message': self.message,
            'user_id': self.user_id,
            'session_id': self.session_id,
            'ip_address': self.ip_address,
            'additional_data': self.get_additional_data()
        }

class EmotionStatistics(db.Model):
    __tablename__ = 'emotion_statistics'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    date = db.Column(db.Date, nullable=False)
    period_type = db.Column(db.String(20), default='daily') 
    
    total_snapshots = db.Column(db.Integer, default=0)
    total_analysis_time = db.Column(db.Integer, default=0)  
    
    happy_count = db.Column(db.Integer, default=0)
    sad_count = db.Column(db.Integer, default=0)
    angry_count = db.Column(db.Integer, default=0)
    surprised_count = db.Column(db.Integer, default=0)
    fearful_count = db.Column(db.Integer, default=0)
    disgusted_count = db.Column(db.Integer, default=0)
    neutral_count = db.Column(db.Integer, default=0)
    
    avg_emotion_intensity = db.Column(db.Float, default=0.0)
    
    avg_face_confidence = db.Column(db.Float, default=0.0)
    total_faces_detected = db.Column(db.Integer, default=0)
    
    __table_args__ = (
        db.UniqueConstraint('user_id', 'date', 'period_type', name='unique_user_date_period'),
        db.Index('idx_user_date', 'user_id', 'date'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'date': self.date.isoformat() if self.date else None,
            'period_type': self.period_type,
            'total_snapshots': self.total_snapshots,
            'total_analysis_time': self.total_analysis_time,
            'emotion_distribution': {
                'happy': self.happy_count,
                'sad': self.sad_count,
                'angry': self.angry_count,
                'surprised': self.surprised_count,
                'fearful': self.fearful_count,
                'disgusted': self.disgusted_count,
                'neutral': self.neutral_count
            },
            'avg_emotion_intensity': self.avg_emotion_intensity,
            'avg_face_confidence': self.avg_face_confidence,
            'total_faces_detected': self.total_faces_detected
        }

def init_db(app):
    db.init_app(app)
    
    with app.app_context():
        db.create_all()
        
        try:
            db.engine.execute("""
                CREATE INDEX IF NOT EXISTS idx_emotion_snapshots_user_time_emotion 
                ON emotion_snapshots(user_id, timestamp DESC, dominant_emotion)
            """)
            
            db.engine.execute("""
                CREATE INDEX IF NOT EXISTS idx_user_sessions_active_expires 
                ON user_sessions(is_active, expires_at)
            """)
            
            print(" تم إنشاء قاعدة البيانات والفهارس بنجاح")
            
        except Exception as e:
            print(f" تحذير: لم يتم إنشاء بعض الفهارس: {e}")

def create_sample_data():
    try:
        sample_user = User(
            name="مستخدم تجريبي",
            email="test@example.com",
            detected_gender="male",
            detected_age=25,
            gender_confidence=0.95,
            age_confidence=0.87,
            is_guest=False
        )
        
        db.session.add(sample_user)
        db.session.commit()
        
        sample_session = UserSession(
            user_id=sample_user.id,
            user_agent="Mozilla/5.0 Test Browser",
            ip_address="127.0.0.1"
        )
        
        db.session.add(sample_session)
        db.session.commit()
        
        sample_snapshot = EmotionSnapshot(
            user_id=sample_user.id,
            session_id=sample_session.session_id,
            dominant_emotion="happy",
            emotion_intensity=0.85,
            face_detected=True,
            face_count=1,
            face_confidence=0.92,
            detected_age=25.3,
            detected_gender="male",
            age_confidence=0.87,
            gender_confidence=0.95
        )
        
        sample_snapshot.set_emotions_data({
            "happy": 85.2,
            "neutral": 10.1,
            "surprised": 3.2,
            "sad": 1.5
        })
        
        sample_snapshot.set_face_box({
            "x": 150,
            "y": 100,
            "width": 200,
            "height": 240
        })
        
        db.session.add(sample_snapshot)
        db.session.commit()
        
        print("✅ تم إنشاء البيانات التجريبية بنجاح")
        
    except Exception as e:
        print(f"⚠️ خطأ في إنشاء البيانات التجريبية: {e}")
        db.session.rollback()

