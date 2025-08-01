import uuid
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime


db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    user_id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(100), nullable=False)
    gender = db.Column(db.String(20), nullable=False)
    approximate_age = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # العلاقات
    messages = db.relationship('Message', backref='user', lazy=True)
    emotion_entries = db.relationship('EmotionEntry', backref='user', lazy=True)

class Message(db.Model):
    __tablename__ = 'messages'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(50), db.ForeignKey('users.user_id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, index=True)
    dominant_emotion = db.Column(db.String(50))
    
    emotion_history = db.relationship('EmotionHistory', backref='message', lazy=True)

class EmotionHistory(db.Model):
    __tablename__ = 'emotion_history'
    
    id = db.Column(db.Integer, primary_key=True)
    message_id = db.Column(db.Integer, db.ForeignKey('messages.id'), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)
    
    emotion_entries = db.relationship('EmotionEntry', backref='emotion_history', lazy=True)

class EmotionEntry(db.Model):
    __tablename__ = 'emotion_entries'
    
    id = db.Column(db.Integer, primary_key=True)
    history_id = db.Column(db.Integer, db.ForeignKey('emotion_history.id'), nullable=False)
    user_id = db.Column(db.String(50), db.ForeignKey('users.user_id'), nullable=False)
    emotion_type = db.Column(db.String(50), nullable=False)
    percentage = db.Column(db.Float, nullable=False)
    
    __table_args__ = (
        db.UniqueConstraint('history_id', 'emotion_type', name='unique_emotion_per_history'),
    )

#=====================EmotionAnalysis fun=========================

# الحصول على أكثر المشاعر شيوعاً لدى مستخدم
def get_user_dominant_emotion(user_id):
    from sqlalchemy import func
    
    result = db.session.query(
        EmotionEntry.emotion_type,
        func.sum(EmotionEntry.percentage).label('total')
    ).filter_by(user_id=user_id
    ).group_by(EmotionEntry.emotion_type
    ).order_by(func.sum(EmotionEntry.percentage).desc()
    ).first()
    
    return result.emotion_type if result else None

# تحليل تطور المشاعر مع الوقت لمستخدم معين
def get_emotion_timeline(user_id, emotion_type):
    return db.session.query(
        EmotionHistory.timestamp,
        EmotionEntry.percentage
    ).join(EmotionEntry
    ).filter(EmotionEntry.user_id == user_id,
             EmotionEntry.emotion_type == emotion_type
    ).order_by(EmotionHistory.timestamp
    ).all()

# الحصول على المستخدمين الأكثر سعادة بناءً على مشاعرهم
def get_happiest_users(limit=5):
    from sqlalchemy import func
    
    return db.session.query(
        User,
        func.avg(EmotionEntry.percentage).label('happiness_score')
    ).join(EmotionEntry
    ).filter(EmotionEntry.emotion_type == 'happy'
    ).group_by(User.user_id
    ).order_by(func.avg(EmotionEntry.percentage).desc()
    ).limit(limit
    ).all()

def add_message(data):
    """إضافة رسالة جديدة مع بيانات المشاعر المرتبطة بها"""
    try:
        # إنشاء أو تحديث المستخدم
        user = User.query.get(data['user_id'])
        if not user:
            user = User(
                user_id=data['user_id'],
                name=data['sender_name'],
                gender=data['gender'],
                approximate_age=data['approximate_age']
            )
            db.session.add(user)
        
        # إنشاء الرسالة
        message = Message(
            user_id=user.user_id,
            content=data['message_content'],
            timestamp=datetime.fromisoformat(data['timestamp']),
            dominant_emotion=data['dominant_emotion']
        )
        db.session.add(message)
        
        # إضافة سجل المشاعر
        for emotion_record in data['emotion_history_20s']:
            history = EmotionHistory(
                message=message,
                timestamp=datetime.fromisoformat(emotion_record['timestamp'])
            )
            db.session.add(history)
            
            for emotion, percentage in emotion_record['emotion_percentage'].items():
                entry = EmotionEntry(
                    emotion_history=history,
                    user_id=user.user_id,
                    emotion_type=emotion,
                    percentage=percentage
                )
                db.session.add(entry)
        
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        print(f"Error adding message: {str(e)}")
        return False

def get_user_messages(user_id):
    """الحصول على جميع رسائل مستخدم معين"""
    return Message.query.filter_by(user_id=user_id).order_by(Message.timestamp.desc()).all()

def get_emotion_analysis(user_id):
    """تحليل المشاعر السائدة لمستخدم"""
    from sqlalchemy import func
    
    return db.session.query(
        Message.dominant_emotion,
        func.count(Message.id)
    ).filter_by(user_id=user_id
    ).group_by(Message.dominant_emotion
    ).all()

def get_emotion_trend(user_id):
    """تتبع تغير المشاعر عبر الوقت لمستخدم"""
    return db.session.query(
        EmotionHistory.timestamp,
        EmotionEntry.emotion_type,
        EmotionEntry.percentage
    ).join(EmotionEntry
    ).filter(EmotionEntry.user_id == user_id
    ).order_by(EmotionHistory.timestamp
    ).all()

#=====================Users fun=========================
# إنشاء مستخدم جديد
def create_user( name, gender, approximate_age):
    try:
        new_user = User(
            name=name,
            gender=gender,
            approximate_age=approximate_age
        )
        db.session.add(new_user)
        db.session.commit()
        return new_user
    except Exception as e:
        db.session.rollback()
        raise e

# الحصول على مستخدم بواسطة المعرف
def get_user_by_id(user_id):
    return User.query.get(user_id)

# الحصول على جميع المستخدمين
def get_all_users():
    return User.query.order_by(User.created_at.desc()).all()

# تحديث بيانات المستخدم
def update_user(user_id, **kwargs):
    try:
        user = User.query.get(user_id)
        if not user:
            return None
        
        for key, value in kwargs.items():
            if hasattr(user, key):
                setattr(user, key, value)
        
        db.session.commit()
        return user
    except Exception as e:
        db.session.rollback()
        raise e

# حذف مستخدم
def delete_user(user_id):
    try:
        user = User.query.get(user_id)
        if not user:
            return False
        
        db.session.delete(user)
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        raise e

def search_users_by_name(name):
    return User.query.filter(User.name.ilike(f'%{name}%')).all()

# الحصول على عدد المستخدمين
def get_users_count():
    return User.query.count()

#================================Message===================
# إنشاء رسالة جديدة
def create_message(user_id, content, timestamp, dominant_emotion):
    try:
        new_message = Message(
            user_id=user_id,
            content=content,
            timestamp=timestamp,
            dominant_emotion=dominant_emotion
        )
        db.session.add(new_message)
        db.session.commit()
        return new_message
    except Exception as e:
        db.session.rollback()
        raise e

# الحصول على رسالة بواسطة المعرف
def get_message_by_id(message_id):
    return Message.query.get(message_id)

# الحصول على جميع رسائل مستخدم معين
def get_user_messages(user_id, limit=None):
    query = Message.query.filter_by(user_id=user_id).order_by(Message.timestamp.desc())
    if limit:
        query = query.limit(limit)
    return query.all()

# الحصول على أحدث الرسائل
def get_recent_messages(limit=10):
    return Message.query.order_by(Message.timestamp.desc()).limit(limit).all()

# البحث في محتوى الرسائل
def search_messages_content(search_term):
    return Message.query.filter(Message.content.ilike(f'%{search_term}%')).all()

# الحصول على رسائل حسب المشاعر السائدة
def get_messages_by_emotion(emotion):
    return Message.query.filter_by(dominant_emotion=emotion).all()

# تحديث رسالة
def update_message(message_id, **kwargs):
    try:
        message = Message.query.get(message_id)
        if not message:
            return None
        
        for key, value in kwargs.items():
            if hasattr(message, key):
                setattr(message, key, value)
        
        db.session.commit()
        return message
    except Exception as e:
        db.session.rollback()
        raise e

# حذف رسالة
def delete_message(message_id):
    try:
        message = Message.query.get(message_id)
        if not message:
            return False
        
        db.session.delete(message)
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        raise e

# الحصول على عدد الرسائل
def get_messages_count():
    return Message.query.count()
#================================EmotionHistory===================
# إنشاء سجل مشاعر جديد
def create_emotion_history(message_id, timestamp):
    try:
        new_history = EmotionHistory(
            message_id=message_id,
            timestamp=timestamp
        )
        db.session.add(new_history)
        db.session.commit()
        return new_history
    except Exception as e:
        db.session.rollback()
        raise e

# الحصول على سجل مشاعر بواسطة المعرف
def get_emotion_history_by_id(history_id):
    return EmotionHistory.query.get(history_id)

# الحصول على سجل المشاعر لرسالة معينة
def get_message_emotion_history(message_id):
    return EmotionHistory.query.filter_by(message_id=message_id).order_by(EmotionHistory.timestamp).all()

# الحصول على سجل المشاعر لمستخدم معين
def get_user_emotion_history(user_id, limit=None):
    query = EmotionHistory.query.join(Message).filter(Message.user_id == user_id).order_by(EmotionHistory.timestamp.desc())
    if limit:
        query = query.limit(limit)
    return query.all()

# تحديث وقت سجل المشاعر
def update_emotion_history_timestamp(history_id, new_timestamp):
    try:
        history = EmotionHistory.query.get(history_id)
        if not history:
            return None
        
        history.timestamp = new_timestamp
        db.session.commit()
        return history
    except Exception as e:
        db.session.rollback()
        raise e

# حذف سجل مشاعر
def delete_emotion_history(history_id):
    try:
        history = EmotionHistory.query.get(history_id)
        if not history:
            return False
        
        db.session.delete(history)
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        raise e
#================================EmotionEntry===================
# إنشاء مدخل مشاعر جديد
def create_emotion_entry(history_id, user_id, emotion_type, percentage):
    try:
        new_entry = EmotionEntry(
            history_id=history_id,
            user_id=user_id,
            emotion_type=emotion_type,
            percentage=percentage
        )
        db.session.add(new_entry)
        db.session.commit()
        return new_entry
    except Exception as e:
        db.session.rollback()
        raise e

# الحصول على مدخل مشاعر بواسطة المعرف
def get_emotion_entry_by_id(entry_id):
    return EmotionEntry.query.get(entry_id)

# الحصول على مدخلات مشاعر لسجل معين
def get_entries_for_history(history_id):
    return EmotionEntry.query.filter_by(history_id=history_id).all()

# الحصول على مدخلات مشاعر لنوع معين
def get_entries_by_emotion_type(emotion_type):
    return EmotionEntry.query.filter_by(emotion_type=emotion_type).all()

# الحصول على متوسط مشاعر مستخدم معين
def get_user_emotion_average(user_id):
    from sqlalchemy import func
    
    result = db.session.query(
        EmotionEntry.emotion_type,
        func.avg(EmotionEntry.percentage).label('average')
    ).filter_by(user_id=user_id
    ).group_by(EmotionEntry.emotion_type
    ).all()
    
    return {row.emotion_type: row.average for row in result}

# تحديث نسبة المشاعر في مدخل معين
def update_emotion_entry_percentage(entry_id, new_percentage):
    try:
        entry = EmotionEntry.query.get(entry_id)
        if not entry:
            return None
        
        entry.percentage = new_percentage
        db.session.commit()
        return entry
    except Exception as e:
        db.session.rollback()
        raise e

# حذف مدخل مشاعر
def delete_emotion_entry(entry_id):
    try:
        entry = EmotionEntry.query.get(entry_id)
        if not entry:
            return False
        
        db.session.delete(entry)
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        raise e

# الحصول على توزيع المشاعر لرسالة معينة
def get_message_emotion_distribution(message_id):
    from sqlalchemy import func
    
    return db.session.query(
        EmotionEntry.emotion_type,
        func.avg(EmotionEntry.percentage).label('average')
    ).join(EmotionHistory
    ).filter(EmotionHistory.message_id == message_id
    ).group_by(EmotionEntry.emotion_type
    ).all()