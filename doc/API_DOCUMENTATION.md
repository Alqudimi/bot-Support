# توثيق API - نظام تحليل المشاعر

## نظرة عامة

يوفر نظام تحليل المشاعر واجهة برمجة تطبيقات (API) RESTful شاملة لإدارة المستخدمين والرسائل وسجل المشاعر. جميع endpoints تستخدم تنسيق JSON للطلبات والاستجابات.

## عنوان الخادم الأساسي

```
http://127.0.0.1:5000/api
```

## المصادقة والأمان

- **تحديد معدل الطلبات**: 100 طلب في الدقيقة لكل عنوان IP
- **CORS**: مدعوم للطلبات من جميع المجالات
- **Content-Type**: `application/json` مطلوب لجميع طلبات POST/PUT

## رموز الاستجابة

| الرمز | الوصف |
|-------|--------|
| 200 | نجح الطلب |
| 201 | تم إنشاء المورد بنجاح |
| 400 | خطأ في البيانات المرسلة |
| 404 | المورد غير موجود |
| 429 | تم تجاوز حد الطلبات |
| 500 | خطأ في الخادم |

---

## إدارة المستخدمين

### إنشاء مستخدم جديد

**POST** `/users/create`

إنشاء مستخدم جديد في النظام.

#### طلب البيانات
```json
{
    "name": "أحمد محمد",
    "gender": "ذكر",
    "approximate_age": 25
}
```

#### الاستجابة
```json
{
    "message": "تم إنشاء المستخدم بنجاح",
    "user_id": "user_123456789",
    "user": {
        "id": "user_123456789",
        "name": "أحمد محمد",
        "gender": "ذكر",
        "approximate_age": 25,
        "created_at": "2025-08-01T15:30:00Z"
    }
}
```

### الحصول على بيانات مستخدم

**GET** `/users/{user_id}/get`

الحصول على بيانات مستخدم محدد.

#### المعاملات
- `user_id` (string): معرف المستخدم

#### الاستجابة
```json
{
    "user": {
        "id": "user_123456789",
        "name": "أحمد محمد",
        "gender": "ذكر",
        "approximate_age": 25,
        "created_at": "2025-08-01T15:30:00Z",
        "message_count": 5
    }
}
```

### تحديث بيانات مستخدم

**PUT** `/users/{user_id}/update`

تحديث بيانات مستخدم موجود.

#### طلب البيانات
```json
{
    "name": "أحمد علي محمد",
    "approximate_age": 26
}
```

#### الاستجابة
```json
{
    "message": "تم تحديث المستخدم بنجاح",
    "user": {
        "id": "user_123456789",
        "name": "أحمد علي محمد",
        "gender": "ذكر",
        "approximate_age": 26,
        "updated_at": "2025-08-01T16:00:00Z"
    }
}
```

### حذف مستخدم

**DELETE** `/users/{user_id}/delete`

حذف مستخدم من النظام.

#### الاستجابة
```json
{
    "message": "تم حذف المستخدم بنجاح"
}
```

### عرض جميع المستخدمين

**GET** `/users/get_all`

الحصول على قائمة بجميع المستخدمين.

#### الاستجابة
```json
{
    "users": [
        {
            "id": "user_123456789",
            "name": "أحمد محمد",
            "gender": "ذكر",
            "approximate_age": 25,
            "message_count": 5
        }
    ],
    "total_count": 1
}
```

### البحث عن المستخدمين

**GET** `/users/search?name={name}`

البحث عن المستخدمين بالاسم.

#### المعاملات
- `name` (string): اسم المستخدم للبحث

#### الاستجابة
```json
{
    "users": [
        {
            "id": "user_123456789",
            "name": "أحمد محمد",
            "gender": "ذكر",
            "approximate_age": 25
        }
    ],
    "search_term": "أحمد",
    "results_count": 1
}
```

### عدد المستخدمين

**GET** `/users/count`

الحصول على العدد الإجمالي للمستخدمين.

#### الاستجابة
```json
{
    "count": 42
}
```

---

## إدارة الرسائل

### إضافة رسالة جديدة

**POST** `/messages/add`

إضافة رسالة جديدة مع تحليل المشاعر.

#### طلب البيانات
```json
{
    "user_id": "user_123456789",
    "message_content": "أنا سعيد جداً اليوم!",
    "dominant_emotion": "سعيد",
    "emotion_history_20s": [
        {
            "timestamp": "2025-08-01T15:27:00Z",
            "emotion_percentage": {
                "سعيد": 90,
                "محايد": 8,
                "حزين": 2
            }
        }
    ]
}
```

#### الاستجابة
```json
{
    "message": "تم إضافة الرسالة بنجاح",
    "message_id": "msg_987654321",
    "message_data": {
        "id": "msg_987654321",
        "user_id": "user_123456789",
        "content": "أنا سعيد جداً اليوم!",
        "dominant_emotion": "سعيد",
        "timestamp": "2025-08-01T15:27:00Z"
    }
}
```

### الحصول على رسالة

**GET** `/messages/{message_id}/get`

الحصول على بيانات رسالة محددة.

#### الاستجابة
```json
{
    "message": {
        "id": "msg_987654321",
        "user_id": "user_123456789",
        "content": "أنا سعيد جداً اليوم!",
        "dominant_emotion": "سعيد",
        "timestamp": "2025-08-01T15:27:00Z",
        "user_name": "أحمد محمد"
    }
}
```

### رسائل المستخدم

**GET** `/messages/user/{user_id}?limit={limit}`

الحصول على رسائل مستخدم معين.

#### المعاملات
- `user_id` (string): معرف المستخدم
- `limit` (integer, اختياري): الحد الأقصى لعدد الرسائل

#### الاستجابة
```json
{
    "messages": [
        {
            "id": "msg_987654321",
            "content": "أنا سعيد جداً اليوم!",
            "dominant_emotion": "سعيد",
            "timestamp": "2025-08-01T15:27:00Z"
        }
    ],
    "user_id": "user_123456789",
    "total_count": 5
}
```

### أحدث الرسائل

**GET** `/messages/recent?limit={limit}`

الحصول على أحدث الرسائل في النظام.

#### المعاملات
- `limit` (integer, اختياري): الحد الأقصى لعدد الرسائل

#### الاستجابة
```json
{
    "messages": [
        {
            "id": "msg_987654321",
            "user_id": "user_123456789",
            "user_name": "أحمد محمد",
            "content": "أنا سعيد جداً اليوم!",
            "dominant_emotion": "سعيد",
            "timestamp": "2025-08-01T15:27:00Z"
        }
    ],
    "total_count": 1
}
```

### البحث في محتوى الرسائل

**GET** `/messages/search_content?query={query}`

البحث في محتوى الرسائل.

#### المعاملات
- `query` (string): كلمة البحث

#### الاستجابة
```json
{
    "messages": [
        {
            "id": "msg_987654321",
            "user_name": "أحمد محمد",
            "content": "أنا سعيد جداً اليوم!",
            "dominant_emotion": "سعيد",
            "timestamp": "2025-08-01T15:27:00Z"
        }
    ],
    "search_query": "سعيد",
    "results_count": 1
}
```

### الرسائل حسب المشاعر

**GET** `/messages/by_emotion?emotion={emotion}`

الحصول على الرسائل حسب نوع المشاعر.

#### المعاملات
- `emotion` (string): نوع المشاعر

#### الاستجابة
```json
{
    "messages": [
        {
            "id": "msg_987654321",
            "user_name": "أحمد محمد",
            "content": "أنا سعيد جداً اليوم!",
            "timestamp": "2025-08-01T15:27:00Z"
        }
    ],
    "emotion": "سعيد",
    "results_count": 1
}
```

### تحديث رسالة

**PUT** `/messages/{message_id}/update`

تحديث محتوى رسالة موجودة.

#### طلب البيانات
```json
{
    "message_content": "أنا سعيد جداً اليوم ومتحمس للمستقبل!",
    "dominant_emotion": "متحمس"
}
```

### حذف رسالة

**DELETE** `/messages/{message_id}/delete`

حذف رسالة من النظام.

#### الاستجابة
```json
{
    "message": "تم حذف الرسالة بنجاح"
}
```

### عدد الرسائل

**GET** `/messages/count`

الحصول على العدد الإجمالي للرسائل.

#### الاستجابة
```json
{
    "count": 156
}
```

---

## سجل المشاعر

### سجل مشاعر الرسالة

**GET** `/history/message/{message_id}`

الحصول على سجل مشاعر رسالة معينة.

#### الاستجابة
```json
{
    "emotion_history": [
        {
            "id": "hist_111222333",
            "message_id": "msg_987654321",
            "timestamp": "2025-08-01T15:27:00Z",
            "emotion_percentage": {
                "سعيد": 90,
                "محايد": 8,
                "حزين": 2
            }
        }
    ],
    "message_id": "msg_987654321"
}
```

### سجل مشاعر المستخدم

**GET** `/history/user/{user_id}`

الحصول على سجل مشاعر مستخدم معين.

#### الاستجابة
```json
{
    "emotion_history": [
        {
            "message_id": "msg_987654321",
            "timestamp": "2025-08-01T15:27:00Z",
            "dominant_emotion": "سعيد",
            "emotion_percentage": {
                "سعيد": 90,
                "محايد": 8,
                "حزين": 2
            }
        }
    ],
    "user_id": "user_123456789",
    "total_entries": 1
}
```

### تحديث وقت سجل المشاعر

**PUT** `/history/{history_id}/update_timestamp`

تحديث الوقت في سجل المشاعر.

#### طلب البيانات
```json
{
    "new_timestamp": "2025-08-01T16:00:00Z"
}
```

### حذف سجل مشاعر

**DELETE** `/history/{history_id}/delete`

حذف إدخال من سجل المشاعر.

---

## أمثلة على الاستخدام

### مثال شامل: إضافة مستخدم ورسالة

```javascript
// 1. إنشاء مستخدم جديد
const userData = {
    name: "فاطمة أحمد",
    gender: "أنثى",
    approximate_age: 28
};

const userResponse = await fetch('http://127.0.0.1:5000/api/users/create', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'
    },
    body: JSON.stringify(userData)
});

const userResult = await userResponse.json();
const userId = userResult.user_id;

// 2. إضافة رسالة للمستخدم
const messageData = {
    user_id: userId,
    message_content: "أشعر بالحماس لبدء هذا المشروع الجديد!",
    dominant_emotion: "متحمس",
    emotion_history_20s: [
        {
            timestamp: new Date().toISOString(),
            emotion_percentage: {
                "متحمس": 85,
                "سعيد": 10,
                "محايد": 5
            }
        }
    ]
};

const messageResponse = await fetch('http://127.0.0.1:5000/api/messages/add', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'
    },
    body: JSON.stringify(messageData)
});

const messageResult = await messageResponse.json();
console.log('تم إضافة الرسالة:', messageResult);
```

## معالجة الأخطاء

جميع endpoints تُرجع رسائل خطأ واضحة في حالة الفشل:

```json
{
    "error": "وصف الخطأ",
    "details": "تفاصيل إضافية عن الخطأ",
    "timestamp": "2025-08-01T15:30:00Z"
}
```

## الحدود والقيود

- **حد الطلبات**: 100 طلب في الدقيقة لكل عنوان IP
- **حجم الرسالة**: حد أقصى 1000 حرف
- **طول الاسم**: حد أقصى 100 حرف
- **العمر**: بين 1 و 120 سنة

## نصائح للاستخدام الأمثل

1. **استخدم التخزين المؤقت**: النظام يدعم التخزين المؤقت للاستعلامات المتكررة
2. **معالجة الأخطاء**: تأكد من معالجة جميع رموز الخطأ المحتملة
3. **التحقق من البيانات**: تحقق من صحة البيانات قبل الإرسال
4. **استخدم المعاملات الاختيارية**: لتحسين الأداء وتقليل البيانات المنقولة

---

هذا التوثيق يغطي جميع endpoints المتاحة في نظام تحليل المشاعر. للحصول على مساعدة إضافية، راجع ملف README.md أو ملف USER_GUIDE.md.

