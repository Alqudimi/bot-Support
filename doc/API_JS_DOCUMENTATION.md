# توثيق مكتبة API.js - نظام تحليل المشاعر

## نظرة عامة

مكتبة API.js هي مكتبة JavaScript شاملة تسهل التفاعل مع نظام تحليل المشاعر. توفر المكتبة دوال جاهزة لجميع العمليات المدعومة في النظام.

## التثبيت والإعداد

### التضمين في HTML
```html
<script src="api.js"></script>
```

### الإعداد الأساسي
```javascript
// تعيين عنوان الخادم (اختياري - القيمة الافتراضية)
const API_BASE_URL = 'http://127.0.0.1:5000/api';
```

### الاستيراد كوحدة ES6
```javascript
import EmotionAPI from './api.js';
// أو استيراد دوال محددة
import { createUser, addMessage, getSystemStats } from './api.js';
```

---

## الدوال الأساسية

### callApi(endpoint, method, data)
الدالة الأساسية للتواصل مع API.

**المعاملات:**
- `endpoint` (string): نقطة النهاية في API
- `method` (string): نوع الطلب (GET, POST, PUT, DELETE)
- `data` (object, اختياري): البيانات المرسلة

**المثال:**
```javascript
const result = await callApi('/users/count', 'GET');
```

### processUserData(userData)
معالجة وتنسيق بيانات المستخدم.

**المعاملات:**
- `userData` (object): بيانات المستخدم الخام

**الإرجاع:**
```javascript
{
    name: "اسم المستخدم",
    gender: "الجنس",
    approximate_age: العمر
}
```

### processMessageData(messageData)
معالجة وتنسيق بيانات الرسالة.

**المعاملات:**
- `messageData` (object): بيانات الرسالة الخام

**الإرجاع:**
```javascript
{
    user_id: "معرف المستخدم",
    message_content: "محتوى الرسالة",
    dominant_emotion: "المشاعر السائدة",
    emotion_history_20s: [...]
}
```

---

## دوال إدارة المستخدمين

### createUser(userData)
إنشاء مستخدم جديد في النظام.

**المعاملات:**
```javascript
{
    sender_name: "أحمد محمد",    // مطلوب
    gender: "ذكر",              // مطلوب
    approximate_age: 25         // مطلوب
}
```

**المثال:**
```javascript
const userData = {
    sender_name: "فاطمة أحمد",
    gender: "أنثى",
    approximate_age: 28
};

try {
    const result = await createUser(userData);
    console.log('معرف المستخدم الجديد:', result.user_id);
} catch (error) {
    console.error('خطأ في إنشاء المستخدم:', error.message);
}
```

### getUser(userId)
الحصول على بيانات مستخدم محدد.

**المعاملات:**
- `userId` (string): معرف المستخدم

**المثال:**
```javascript
const user = await getUser("user_123456789");
console.log('بيانات المستخدم:', user);
```

### getAllUsers()
الحصول على جميع المستخدمين.

**المثال:**
```javascript
const allUsers = await getAllUsers();
console.log('عدد المستخدمين:', allUsers.total_count);
console.log('قائمة المستخدمين:', allUsers.users);
```

### updateUser(userId, userData)
تحديث بيانات مستخدم موجود.

**المعاملات:**
- `userId` (string): معرف المستخدم
- `userData` (object): البيانات المحدثة

**المثال:**
```javascript
const updatedData = {
    name: "أحمد علي محمد",
    approximate_age: 26
};

const result = await updateUser("user_123456789", updatedData);
```

### deleteUser(userId)
حذف مستخدم من النظام.

**المعاملات:**
- `userId` (string): معرف المستخدم

**المثال:**
```javascript
await deleteUser("user_123456789");
console.log('تم حذف المستخدم بنجاح');
```

### searchUsers(name)
البحث عن المستخدمين بالاسم.

**المعاملات:**
- `name` (string): اسم المستخدم للبحث

**المثال:**
```javascript
const searchResults = await searchUsers("أحمد");
console.log('نتائج البحث:', searchResults.users);
```

### getUsersCount()
الحصول على عدد المستخدمين الإجمالي.

**المثال:**
```javascript
const count = await getUsersCount();
console.log('عدد المستخدمين:', count.count);
```

---

## دوال إدارة الرسائل

### addMessage(messageData)
إضافة رسالة جديدة مع تحليل المشاعر.

**المعاملات:**
```javascript
{
    user_id: "user_123456789",           // مطلوب
    message_content: "محتوى الرسالة",    // مطلوب
    dominant_emotion: "سعيد",            // مطلوب
    emotion_history_20s: [...]           // اختياري
}
```

**المثال:**
```javascript
const messageData = {
    user_id: "user_123456789",
    message_content: "أشعر بالسعادة اليوم!",
    dominant_emotion: "سعيد",
    emotion_history_20s: [
        {
            timestamp: new Date().toISOString(),
            emotion_percentage: {
                "سعيد": 85,
                "محايد": 10,
                "متحمس": 5
            }
        }
    ]
};

const result = await addMessage(messageData);
```

### processFullMessage(fullMessageData)
معالجة رسالة كاملة (إنشاء مستخدم إذا لم يكن موجوداً + إضافة رسالة).

**المعاملات:**
```javascript
{
    user_id: "user_123456789",           // اختياري
    sender_name: "أحمد محمد",            // مطلوب إذا لم يكن user_id موجود
    gender: "ذكر",                      // مطلوب إذا لم يكن user_id موجود
    approximate_age: 25,                // مطلوب إذا لم يكن user_id موجود
    message_content: "محتوى الرسالة",    // مطلوب
    dominant_emotion: "سعيد",            // مطلوب
    emotion_history_20s: [...]           // اختياري
}
```

**المثال:**
```javascript
const fullMessageData = {
    sender_name: "سارة أحمد",
    gender: "أنثى",
    approximate_age: 24,
    message_content: "أنا متحمسة لهذا المشروع الجديد!",
    dominant_emotion: "متحمس",
    emotion_history_20s: [
        {
            timestamp: new Date().toISOString(),
            emotion_percentage: {
                "متحمس": 80,
                "سعيد": 15,
                "محايد": 5
            }
        }
    ]
};

const result = await processFullMessage(fullMessageData);
console.log('معرف المستخدم:', result.user_id);
console.log('نتيجة الرسالة:', result.message_result);
```

### getMessage(messageId)
الحصول على بيانات رسالة محددة.

**المعاملات:**
- `messageId` (string): معرف الرسالة

**المثال:**
```javascript
const message = await getMessage("msg_987654321");
console.log('محتوى الرسالة:', message.content);
```

### getUserMessages(userId, limit)
الحصول على رسائل مستخدم معين.

**المعاملات:**
- `userId` (string): معرف المستخدم
- `limit` (number, اختياري): الحد الأقصى لعدد الرسائل

**المثال:**
```javascript
// الحصول على آخر 10 رسائل للمستخدم
const messages = await getUserMessages("user_123456789", 10);
console.log('رسائل المستخدم:', messages.messages);
```

### getRecentMessages(limit)
الحصول على أحدث الرسائل في النظام.

**المعاملات:**
- `limit` (number, اختياري): الحد الأقصى لعدد الرسائل

**المثال:**
```javascript
const recentMessages = await getRecentMessages(20);
console.log('أحدث الرسائل:', recentMessages.messages);
```

### searchMessagesContent(query)
البحث في محتوى الرسائل.

**المعاملات:**
- `query` (string): كلمة البحث

**المثال:**
```javascript
const searchResults = await searchMessagesContent("سعادة");
console.log('الرسائل المطابقة:', searchResults.messages);
```

### getMessagesByEmotion(emotion)
الحصول على الرسائل حسب نوع المشاعر.

**المعاملات:**
- `emotion` (string): نوع المشاعر

**المثال:**
```javascript
const happyMessages = await getMessagesByEmotion("سعيد");
console.log('الرسائل السعيدة:', happyMessages.messages);
```

### updateMessage(messageId, messageData)
تحديث رسالة موجودة.

**المعاملات:**
- `messageId` (string): معرف الرسالة
- `messageData` (object): البيانات المحدثة

**المثال:**
```javascript
const updatedData = {
    message_content: "محتوى محدث للرسالة",
    dominant_emotion: "متحمس"
};

await updateMessage("msg_987654321", updatedData);
```

### deleteMessage(messageId)
حذف رسالة من النظام.

**المعاملات:**
- `messageId` (string): معرف الرسالة

**المثال:**
```javascript
await deleteMessage("msg_987654321");
console.log('تم حذف الرسالة بنجاح');
```

### getMessagesCount()
الحصول على عدد الرسائل الإجمالي.

**المثال:**
```javascript
const count = await getMessagesCount();
console.log('عدد الرسائل:', count.count);
```

---

## دوال سجل المشاعر

### getMessageEmotionHistory(messageId)
الحصول على سجل مشاعر رسالة معينة.

**المعاملات:**
- `messageId` (string): معرف الرسالة

**المثال:**
```javascript
const history = await getMessageEmotionHistory("msg_987654321");
console.log('سجل مشاعر الرسالة:', history.emotion_history);
```

### getUserEmotionHistory(userId)
الحصول على سجل مشاعر مستخدم معين.

**المعاملات:**
- `userId` (string): معرف المستخدم

**المثال:**
```javascript
const userHistory = await getUserEmotionHistory("user_123456789");
console.log('سجل مشاعر المستخدم:', userHistory.emotion_history);
```

### updateEmotionHistoryTimestamp(historyId, newTimestamp)
تحديث وقت سجل المشاعر.

**المعاملات:**
- `historyId` (string): معرف سجل المشاعر
- `newTimestamp` (string): الوقت الجديد بتنسيق ISO

**المثال:**
```javascript
const newTime = new Date().toISOString();
await updateEmotionHistoryTimestamp("hist_111222333", newTime);
```

### deleteEmotionHistory(historyId)
حذف سجل مشاعر.

**المعاملات:**
- `historyId` (string): معرف سجل المشاعر

**المثال:**
```javascript
await deleteEmotionHistory("hist_111222333");
```

---

## دوال مساعدة

### processBatchMessages(messagesArray)
معالجة مجموعة من الرسائل دفعة واحدة.

**المعاملات:**
- `messagesArray` (array): مصفوفة من بيانات الرسائل

**المثال:**
```javascript
const messages = [
    {
        sender_name: "أحمد",
        gender: "ذكر",
        approximate_age: 25,
        message_content: "أنا سعيد اليوم",
        dominant_emotion: "سعيد"
    },
    {
        sender_name: "فاطمة",
        gender: "أنثى",
        approximate_age: 23,
        message_content: "أشعر بالحماس",
        dominant_emotion: "متحمس"
    }
];

const results = await processBatchMessages(messages);
console.log('نتائج المعالجة:', results);

// فحص النتائج
results.forEach((result, index) => {
    if (result.success) {
        console.log(`الرسالة ${index + 1}: نجحت`);
    } else {
        console.log(`الرسالة ${index + 1}: فشلت - ${result.error}`);
    }
});
```

### getSystemStats()
الحصول على إحصائيات شاملة للنظام.

**المثال:**
```javascript
const stats = await getSystemStats();
console.log('إحصائيات النظام:', {
    'عدد المستخدمين': stats.users_count,
    'عدد الرسائل': stats.messages_count,
    'وقت الإحصائية': stats.timestamp
});
```

### getEmotionAnalysisForPeriod(startDate, endDate)
تحليل المشاعر لفترة زمنية معينة.

**المعاملات:**
- `startDate` (string): تاريخ البداية بتنسيق ISO
- `endDate` (string): تاريخ النهاية بتنسيق ISO

**المثال:**
```javascript
const startDate = '2025-08-01T00:00:00Z';
const endDate = '2025-08-01T23:59:59Z';

const analysis = await getEmotionAnalysisForPeriod(startDate, endDate);
console.log('تحليل المشاعر للفترة:', {
    'الفترة': analysis.period,
    'عدد الرسائل': analysis.total_messages,
    'توزيع المشاعر': analysis.emotion_distribution
});
```

---

## معالجة الأخطاء

### أنواع الأخطاء الشائعة

#### خطأ الاتصال
```javascript
try {
    const result = await createUser(userData);
} catch (error) {
    if (error.message.includes('fetch')) {
        console.error('خطأ في الاتصال بالخادم');
    }
}
```

#### خطأ في البيانات
```javascript
try {
    const result = await addMessage(messageData);
} catch (error) {
    if (error.message.includes('400')) {
        console.error('خطأ في البيانات المرسلة');
    }
}
```

#### خطأ عدم وجود المورد
```javascript
try {
    const user = await getUser("invalid_id");
} catch (error) {
    if (error.message.includes('404')) {
        console.error('المستخدم غير موجود');
    }
}
```

### أفضل الممارسات لمعالجة الأخطاء

```javascript
async function safeApiCall(apiFunction, ...args) {
    try {
        const result = await apiFunction(...args);
        return { success: true, data: result };
    } catch (error) {
        console.error('خطأ في API:', error.message);
        return { success: false, error: error.message };
    }
}

// الاستخدام
const result = await safeApiCall(createUser, userData);
if (result.success) {
    console.log('نجح إنشاء المستخدم:', result.data);
} else {
    console.log('فشل إنشاء المستخدم:', result.error);
}
```

---

## أمثلة متقدمة

### تطبيق تحليل المشاعر التفاعلي

```javascript
class EmotionAnalyzer {
    constructor() {
        this.users = new Map();
        this.messages = [];
    }
    
    async addUserMessage(userData, messageContent, emotion) {
        try {
            // إنشاء أو الحصول على المستخدم
            let userId = this.users.get(userData.name);
            if (!userId) {
                const userResult = await createUser(userData);
                userId = userResult.user_id;
                this.users.set(userData.name, userId);
            }
            
            // إضافة الرسالة
            const messageData = {
                user_id: userId,
                message_content: messageContent,
                dominant_emotion: emotion,
                emotion_history_20s: [
                    {
                        timestamp: new Date().toISOString(),
                        emotion_percentage: this.generateEmotionPercentage(emotion)
                    }
                ]
            };
            
            const messageResult = await addMessage(messageData);
            this.messages.push(messageResult);
            
            return messageResult;
        } catch (error) {
            console.error('خطأ في إضافة الرسالة:', error);
            throw error;
        }
    }
    
    generateEmotionPercentage(dominantEmotion) {
        const emotions = ["سعيد", "حزين", "غاضب", "محايد", "متحمس", "قلق"];
        const percentage = {};
        
        // إعطاء النسبة الأكبر للمشاعر السائدة
        percentage[dominantEmotion] = 70 + Math.random() * 20;
        
        // توزيع باقي النسب
        const remaining = 100 - percentage[dominantEmotion];
        emotions.filter(e => e !== dominantEmotion).forEach(emotion => {
            percentage[emotion] = Math.random() * remaining / emotions.length;
        });
        
        return percentage;
    }
    
    async getAnalytics() {
        const stats = await getSystemStats();
        const recentMessages = await getRecentMessages(50);
        
        return {
            totalUsers: stats.users_count,
            totalMessages: stats.messages_count,
            recentActivity: recentMessages.messages,
            emotionTrends: this.analyzeEmotionTrends(recentMessages.messages)
        };
    }
    
    analyzeEmotionTrends(messages) {
        const emotionCounts = {};
        messages.forEach(message => {
            const emotion = message.dominant_emotion;
            emotionCounts[emotion] = (emotionCounts[emotion] || 0) + 1;
        });
        
        return emotionCounts;
    }
}

// الاستخدام
const analyzer = new EmotionAnalyzer();

// إضافة رسائل
await analyzer.addUserMessage(
    { name: "أحمد", gender: "ذكر", approximate_age: 25 },
    "أنا سعيد جداً اليوم!",
    "سعيد"
);

// الحصول على التحليلات
const analytics = await analyzer.getAnalytics();
console.log('تحليلات النظام:', analytics);
```

### مراقب المشاعر في الوقت الفعلي

```javascript
class RealTimeEmotionMonitor {
    constructor(updateInterval = 5000) {
        this.updateInterval = updateInterval;
        this.isMonitoring = false;
        this.callbacks = [];
    }
    
    addCallback(callback) {
        this.callbacks.push(callback);
    }
    
    async startMonitoring() {
        this.isMonitoring = true;
        
        while (this.isMonitoring) {
            try {
                const recentMessages = await getRecentMessages(10);
                const stats = await getSystemStats();
                
                const data = {
                    timestamp: new Date().toISOString(),
                    recentMessages: recentMessages.messages,
                    stats: stats
                };
                
                // استدعاء جميع callbacks
                this.callbacks.forEach(callback => {
                    try {
                        callback(data);
                    } catch (error) {
                        console.error('خطأ في callback:', error);
                    }
                });
                
                // انتظار قبل التحديث التالي
                await new Promise(resolve => setTimeout(resolve, this.updateInterval));
                
            } catch (error) {
                console.error('خطأ في المراقبة:', error);
                await new Promise(resolve => setTimeout(resolve, this.updateInterval));
            }
        }
    }
    
    stopMonitoring() {
        this.isMonitoring = false;
    }
}

// الاستخدام
const monitor = new RealTimeEmotionMonitor(3000); // تحديث كل 3 ثوان

monitor.addCallback((data) => {
    console.log('تحديث جديد:', {
        'وقت التحديث': data.timestamp,
        'عدد الرسائل الحديثة': data.recentMessages.length,
        'إجمالي المستخدمين': data.stats.users_count
    });
});

// بدء المراقبة
monitor.startMonitoring();

// إيقاف المراقبة بعد دقيقة
setTimeout(() => {
    monitor.stopMonitoring();
    console.log('تم إيقاف المراقبة');
}, 60000);
```

---

## التحسين والأداء

### تخزين مؤقت للبيانات

```javascript
class CachedEmotionAPI {
    constructor(cacheTimeout = 60000) { // دقيقة واحدة
        this.cache = new Map();
        this.cacheTimeout = cacheTimeout;
    }
    
    async getCachedData(key, fetchFunction) {
        const cached = this.cache.get(key);
        const now = Date.now();
        
        if (cached && (now - cached.timestamp) < this.cacheTimeout) {
            return cached.data;
        }
        
        const data = await fetchFunction();
        this.cache.set(key, {
            data: data,
            timestamp: now
        });
        
        return data;
    }
    
    async getUsers() {
        return this.getCachedData('all_users', getAllUsers);
    }
    
    async getStats() {
        return this.getCachedData('system_stats', getSystemStats);
    }
    
    clearCache() {
        this.cache.clear();
    }
}

// الاستخدام
const cachedAPI = new CachedEmotionAPI();
const users = await cachedAPI.getUsers(); // سيتم جلبها من الخادم
const usersAgain = await cachedAPI.getUsers(); // سيتم جلبها من التخزين المؤقت
```

### معالجة الطلبات المتوازية

```javascript
async function processMultipleOperations() {
    try {
        // تنفيذ عدة عمليات بالتوازي
        const [users, messages, stats] = await Promise.all([
            getAllUsers(),
            getRecentMessages(20),
            getSystemStats()
        ]);
        
        console.log('تم الحصول على جميع البيانات:', {
            usersCount: users.total_count,
            messagesCount: messages.total_count,
            systemStats: stats
        });
        
        return { users, messages, stats };
    } catch (error) {
        console.error('خطأ في العمليات المتوازية:', error);
        throw error;
    }
}
```

---

## الخلاصة

مكتبة API.js توفر واجهة شاملة وسهلة الاستخدام للتفاعل مع نظام تحليل المشاعر. باستخدام الدوال والأمثلة المتوفرة في هذا التوثيق، يمكنك بناء تطبيقات قوية لتحليل المشاعر والنصوص.

### النقاط الرئيسية:
- **سهولة الاستخدام**: دوال بسيطة ومباشرة
- **معالجة شاملة للأخطاء**: رسائل خطأ واضحة ومفيدة
- **مرونة عالية**: دعم لجميع عمليات النظام
- **أداء محسن**: إمكانية التخزين المؤقت والمعالجة المتوازية

للحصول على مساعدة إضافية، راجع الملفات الأخرى في التوثيق أو جرب الأمثلة في `example_usage.js`.

