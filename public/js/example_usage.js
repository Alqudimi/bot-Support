// مثال على استخدام API.js مع البيانات المقدمة

import EmotionAPI from './api.js';

// البيانات المثال المقدمة من المستخدم
const sampleData = [
  {
    "timestamp": "2025-08-01T15:27:00Z",
    "sender_name": "محمد",
    "gender": "ذكر",
    "approximate_age": 30,
    "dominant_emotion": "سعيد",
    "emotion_history_20s": [
      {
        "timestamp": "2025-08-01T15:26:40Z",
        "emotion_percentage": {
          "happy": 75,
          "neutral": 15,
          "sad": 10
        }
      },
      {
        "timestamp": "2025-08-01T15:26:50Z",
        "emotion_percentage": {
          "happy": 85,
          "neutral": 10,
          "sad": 5
        }
      },
      {
        "timestamp": "2025-08-01T15:27:00Z",
        "emotion_percentage": {
          "happy": 90,
          "neutral": 8,
          "sad": 2
        }
      }
    ],
    "message_content": "مرحباً بالجميع، أنا سعيد جداً بانضمامي إلى هذا المشروع!"
  },
  {
    "timestamp": "2025-08-01T15:28:15Z",
    "sender_name": "فاطمة",
    "gender": "أنثى",
    "approximate_age": 25,
    "dominant_emotion": "محايد",
    "emotion_history_20s": [
      {
        "timestamp": "2025-08-01T15:27:55Z",
        "emotion_percentage": {
          "neutral": 80,
          "surprised": 10,
          "angry": 10
        }
      },
      {
        "timestamp": "2025-08-01T15:28:05Z",
        "emotion_percentage": {
          "neutral": 95,
          "surprised": 5,
          "angry": 0
        }
      },
      {
        "timestamp": "2025-08-01T15:28:15Z",
        "emotion_percentage": {
          "neutral": 98,
          "surprised": 2,
          "angry": 0
        }
      }
    ],
    "message_content": "شكراً جزيلاً على التحديث. سأراجع المستندات الآن."
  }
];

// ==================== أمثلة على الاستخدام ====================

/**
 * مثال 1: معالجة رسالة واحدة
 */
async function processSingleMessage() {
    try {
        console.log('معالجة رسالة واحدة...');
        const result = await EmotionAPI.processFullMessage(sampleData[0]);
        console.log('نتيجة معالجة الرسالة:', result);
        return result;
    } catch (error) {
        console.error('خطأ في معالجة الرسالة:', error.message);
    }
}

/**
 * مثال 2: معالجة مجموعة من الرسائل
 */
async function processBatchMessages() {
    try {
        console.log('معالجة مجموعة من الرسائل...');
        const results = await EmotionAPI.processBatchMessages(sampleData);
        console.log('نتائج معالجة المجموعة:', results);
        return results;
    } catch (error) {
        console.error('خطأ في معالجة المجموعة:', error.message);
    }
}

/**
 * مثال 3: إنشاء مستخدم يدوياً
 */
async function createUserManually() {
    try {
        console.log('إنشاء مستخدم يدوياً...');
        const userData = {
            sender_name: "أحمد",
            gender: "ذكر",
            approximate_age: 28
        };
        
        const result = await EmotionAPI.createUser(userData);
        console.log('نتيجة إنشاء المستخدم:', result);
        return result;
    } catch (error) {
        console.error('خطأ في إنشاء المستخدم:', error.message);
    }
}

/**
 * مثال 4: البحث عن المستخدمين
 */
async function searchForUsers() {
    try {
        console.log('البحث عن المستخدمين...');
        const users = await EmotionAPI.searchUsers("محمد");
        console.log('نتائج البحث:', users);
        return users;
    } catch (error) {
        console.error('خطأ في البحث:', error.message);
    }
}

/**
 * مثال 5: الحصول على إحصائيات النظام
 */
async function getSystemStatistics() {
    try {
        console.log('الحصول على إحصائيات النظام...');
        const stats = await EmotionAPI.getSystemStats();
        console.log('إحصائيات النظام:', stats);
        return stats;
    } catch (error) {
        console.error('خطأ في الحصول على الإحصائيات:', error.message);
    }
}

/**
 * مثال 6: تحليل المشاعر لفترة زمنية
 */
async function analyzeEmotionsForPeriod() {
    try {
        console.log('تحليل المشاعر لفترة زمنية...');
        const startDate = '2025-08-01T00:00:00Z';
        const endDate = '2025-08-01T23:59:59Z';
        
        const analysis = await EmotionAPI.getEmotionAnalysisForPeriod(startDate, endDate);
        console.log('تحليل المشاعر:', analysis);
        return analysis;
    } catch (error) {
        console.error('خطأ في تحليل المشاعر:', error.message);
    }
}

/**
 * مثال 7: الحصول على رسائل مستخدم معين
 */
async function getUserMessagesExample(userId) {
    try {
        console.log(`الحصول على رسائل المستخدم ${userId}...`);
        const messages = await EmotionAPI.getUserMessages(userId, 10);
        console.log('رسائل المستخدم:', messages);
        return messages;
    } catch (error) {
        console.error('خطأ في الحصول على رسائل المستخدم:', error.message);
    }
}

/**
 * مثال 8: البحث في محتوى الرسائل
 */
async function searchInMessages() {
    try {
        console.log('البحث في محتوى الرسائل...');
        const results = await EmotionAPI.searchMessagesContent("سعيد");
        console.log('نتائج البحث في الرسائل:', results);
        return results;
    } catch (error) {
        console.error('خطأ في البحث في الرسائل:', error.message);
    }
}

/**
 * مثال 9: الحصول على الرسائل حسب نوع المشاعر
 */
async function getMessagesByEmotionType() {
    try {
        console.log('الحصول على الرسائل حسب نوع المشاعر...');
        const happyMessages = await EmotionAPI.getMessagesByEmotion("سعيد");
        console.log('الرسائل السعيدة:', happyMessages);
        return happyMessages;
    } catch (error) {
        console.error('خطأ في الحصول على الرسائل حسب المشاعر:', error.message);
    }
}

/**
 * مثال 10: سيناريو كامل - معالجة البيانات والحصول على التحليلات
 */
async function completeWorkflow() {
    try {
        console.log('بدء السيناريو الكامل...');
        
        // 1. معالجة البيانات المثال
        console.log('1. معالجة البيانات...');
        const processResults = await EmotionAPI.processBatchMessages(sampleData);
        
        // 2. الحصول على الإحصائيات
        console.log('2. الحصول على الإحصائيات...');
        const stats = await EmotionAPI.getSystemStats();
        
        // 3. تحليل المشاعر
        console.log('3. تحليل المشاعر...');
        const emotionAnalysis = await EmotionAPI.getEmotionAnalysisForPeriod(
            '2025-08-01T00:00:00Z', 
            '2025-08-01T23:59:59Z'
        );
        
        // 4. عرض النتائج
        const summary = {
            processed_messages: processResults.filter(r => r.success).length,
            failed_messages: processResults.filter(r => !r.success).length,
            system_stats: stats,
            emotion_analysis: emotionAnalysis
        };
        
        console.log('ملخص السيناريو الكامل:', summary);
        return summary;
        
    } catch (error) {
        console.error('خطأ في السيناريو الكامل:', error.message);
    }
}

// ==================== تشغيل الأمثلة ====================

// يمكن استدعاء هذه الدوال حسب الحاجة
export {
    processSingleMessage,
    processBatchMessages,
    createUserManually,
    searchForUsers,
    getSystemStatistics,
    analyzeEmotionsForPeriod,
    getUserMessagesExample,
    searchInMessages,
    getMessagesByEmotionType,
    completeWorkflow
};

// مثال على التشغيل التلقائي (يمكن إلغاء التعليق عند الحاجة)
/*
(async () => {
    console.log('بدء تشغيل الأمثلة...');
    
    await processSingleMessage();
    await createUserManually();
    await getSystemStatistics();
    
    console.log('انتهاء تشغيل الأمثلة.');
})();
*/

