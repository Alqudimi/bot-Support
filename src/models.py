import uuid
from flask_sqlalchemy import SQLAlchemy 
from datetime import datetime
from sqlalchemy import JSON
from sqlalchemy.sql import exists


db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    user_id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(100), nullable=False)
    gender = db.Column(db.String(20), nullable=False)
    approximate_age = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # العلاقات
    messages = db.relationship('Message', back_populates='user', cascade='all, delete-orphan')
    emotion_histories = db.relationship('EmotionHistory', back_populates='user')
    
    

class Message(db.Model):
    __tablename__ = 'messages'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(50), db.ForeignKey('users.user_id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    dominant_emotion = db.Column(db.String(50))
    
    
    user = db.relationship('User', back_populates='messages')
    emotion_history = db.relationship('EmotionHistory', back_populates='message', cascade='all, delete-orphan')
    

class EmotionHistory(db.Model):
    __tablename__ = 'emotion_history'
    id = db.Column(db.Integer, primary_key=True)
    message_id = db.Column(db.String(36), db.ForeignKey('messages.id'), nullable=False)
    user_id = db.Column(db.String(50), db.ForeignKey('users.user_id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', back_populates='emotion_histories')
    message = db.relationship('Message', back_populates='emotion_history')
    entries = db.relationship('EmotionEntry', back_populates='history', cascade='all, delete-orphan')
    
    
    __table_args__ = (
        db.Index('idx_emotion_history_user', 'user_id'),
        db.Index('idx_emotion_history_message', 'message_id'),
        db.Index('idx_emotion_history_timestamp', 'timestamp'),
    )


class EmotionEntry(db.Model):
    __tablename__ = 'emotion_entries'
    
    id = db.Column(db.Integer, primary_key=True)
    history_id = db.Column(db.Integer, db.ForeignKey('emotion_history.id'), nullable=False)
    predictions = db.Column(JSON)
    
    
    history = db.relationship('EmotionHistory', back_populates='entries')
    
   

#=====================Users fun=========================
# إنشاء مستخدم جديد
def create_user(name, gender, approximate_age):
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


def check_user_exists(user_id):
    """
    تتحقق من وجود مستخدم بالمعرف المحدد (أكثر كفاءة)
    :param user_id: معرف المستخدم المراد البحث عنه
    :return: True إذا كان المستخدم موجوداً، False إذا غير موجود
    """
    return db.session.query(exists().where(User.user_id == user_id)).scalar()

#================================Message===================
# إنشاء رسالة جديدة
def create_message(user_id, content, dominant_emotion):
    try:
        new_message = Message(
            id=str(uuid.uuid4()),
            user_id=user_id,
            content=content,
            dominant_emotion=dominant_emotion
        )
        new_history = EmotionHistory(
            message_id=new_message.id,
            user_id=user_id,
        )
        
        db.session.add(new_message)
        db.session.add(new_history)
        db.session.commit()
        return new_message,new_history
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
def create_emotion_history(message_id):
    try:
        new_history = EmotionHistory(
            message_id=message_id,
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

def get_user_emotion_history_detailed(user_id):
    """
    تسترجع جميع سجلات المشاعر (EmotionHistory) لمستخدم معين
    مع الرسائل المرتبطة بها
    
    :param user_id: معرف المستخدم (String)
    :return: قائمة من سجلات EmotionHistory أو None إذا لم يوجد
    """
    try:
        from sqlalchemy.orm import joinedload
        history_records = db.session.query(EmotionHistory)\
            .filter(EmotionHistory.user_id == user_id)\
            .options(
                joinedload(EmotionHistory.message),  # تحميل الرسالة المرتبطة
                joinedload(EmotionHistory.entries)   # تحميل المدخلات المرتبطة
            )\
            .order_by(EmotionHistory.timestamp.desc())\
            .all()
        
        if not history_records:
            return None
            
        # تحويل النتائج إلى قاموس قابل للتسلسل
        result = []
        for record in history_records:
            result.append({
                "id": record.id,
                "user_id": record.user_id,
                "message_id": record.message_id,
                "timestamp": record.timestamp.isoformat(),
                "message_content": record.message.content if record.message else None,
                "entries_count": len(record.entries)
            })
            
        return result
        
    except Exception as e:
        print(f"Error fetching emotion history for user {user_id}: {str(e)}")
        raise
