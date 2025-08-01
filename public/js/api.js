const API_BASE_URL = 'http://127.0.0.1:5000/api';

/**
 * دالة عامة لاستدعاء API
 * @param {string} endpoint - نقطة النهاية للAPI
 * @param {string} method - طريقة HTTP (GET, POST, PUT, DELETE)
 * @param {Object} data - البيانات المرسلة (للطرق POST, PUT)
 * @returns {Promise} - النتيجة من الخادم
 */
async function callApi(endpoint, method = 'GET', data = null) {
    const url = `${API_BASE_URL}${endpoint}`;
    const options = {
        method,
        headers: {
            'Content-Type': 'application/json',
        },
    };

    if (data) {
        options.body = JSON.stringify(data);
    }

    try {
        const response = await fetch(url, options);
        const result = await response.json();
        if (!response.ok) {
            throw new Error(result.error || 'Something went wrong');
        }
        return result;
    } catch (error) {
        console.error(`API call to ${endpoint} failed:`, error);
        throw error;
    }
}

/**
 * معالجة البيانات الواردة وتحويلها لتنسيق مناسب للخادم
 * @param {Object} messageData - بيانات الرسالة بالتنسيق الجديد
 * @returns {Object} - البيانات بالتنسيق المطلوب للخادم
 */
function processMessageData(messageData) {
    return {
        user_id: messageData.user_id || null,
        message_content: messageData.message_content,
        dominant_emotion: messageData.dominant_emotion,
        emotion_history_20s: messageData.emotion_history_20s || []
    };
}

/**
 * معالجة بيانات المستخدم
 * @param {Object} userData - بيانات المستخدم
 * @returns {Object} - البيانات بالتنسيق المطلوب للخادم
 */
function processUserData(userData) {
    return {
        name: userData.sender_name || userData.name,
        gender: userData.gender,
        approximate_age: userData.approximate_age
    };
}

// User API functions
export const createUser = (userData) => callApi('/users/create', 'POST', userData);
export const deleteUser = (userId) => callApi(`/users/${userId}/delete`, 'DELETE');
export const getUser = (userId) => callApi(`/users/${userId}/get`);
export const getAllUsers = () => callApi('/users/get_all');
export const updateUser = (userId, userData) => callApi(`/users/${userId}/update`, 'PUT', userData);
export const searchUsers = (name) => callApi(`/users/search?name=${name}`);
export const getUsersCount = () => callApi('/users/count');

// Message API functions
export const addMessage = (messageData) => callApi('/messages/add', 'POST', messageData);
export const getMessage = (messageId) => callApi(`/messages/${messageId}/get`);
export const getUserMessages = (userId, limit = null) => {
    const query = limit ? `?limit=${limit}` : '';
    return callApi(`/messages/user/${userId}${query}`);
};
export const getRecentMessages = (limit = null) => {
    const query = limit ? `?limit=${limit}` : '';
    return callApi(`/messages/recent${query}`);
};
export const searchMessagesContent = (query) => callApi(`/messages/search_content?query=${query}`);
export const getMessagesByEmotion = (emotion) => callApi(`/messages/by_emotion?emotion=${emotion}`);
export const updateMessage = (messageId, messageData) => callApi(`/messages/${messageId}/update`, 'PUT', messageData);
export const deleteMessage = (messageId) => callApi(`/messages/${messageId}/delete`, 'DELETE');
export const getMessagesCount = () => callApi('/messages/count');

// Emotion History API functions
export const getMessageEmotionHistory = (messageId) => callApi(`/history/message/${messageId}`);
export const getUserEmotionHistory = (userId) => callApi(`/history/user/${userId}`);
export const updateEmotionHistoryTimestamp = (historyId, newTimestamp) => callApi(`/history/${historyId}/update_timestamp`, 'PUT', { new_timestamp: newTimestamp });
export const deleteEmotionHistory = (historyId) => callApi(`/history/${historyId}/delete`, 'DELETE');




// ==================== دوال إدارة المستخدمين ====================

/**
 * إنشاء مستخدم جديد
 * @param {Object} userData - بيانات المستخدم
 * @returns {Promise} - نتيجة إنشاء المستخدم
 */
export const createUser = (userData) => {
    const processedData = processUserData(userData);
    return callApi('/users/create', 'POST', processedData);
};

/**
 * حذف مستخدم
 * @param {string} userId - معرف المستخدم
 * @returns {Promise} - نتيجة حذف المستخدم
 */
export const deleteUser = (userId) => callApi(`/users/${userId}/delete`, 'DELETE');

/**
 * الحصول على بيانات مستخدم
 * @param {string} userId - معرف المستخدم
 * @returns {Promise} - بيانات المستخدم
 */
export const getUser = (userId) => callApi(`/users/${userId}/get`);

/**
 * الحصول على جميع المستخدمين
 * @returns {Promise} - قائمة بجميع المستخدمين
 */
export const getAllUsers = () => callApi('/users/get_all');

/**
 * تحديث بيانات مستخدم
 * @param {string} userId - معرف المستخدم
 * @param {Object} userData - البيانات المحدثة
 * @returns {Promise} - نتيجة التحديث
 */
export const updateUser = (userId, userData) => {
    const processedData = processUserData(userData);
    return callApi(`/users/${userId}/update`, 'PUT', processedData);
};

/**
 * البحث عن المستخدمين بالاسم
 * @param {string} name - اسم المستخدم للبحث
 * @returns {Promise} - قائمة المستخدمين المطابقين
 */
export const searchUsers = (name) => callApi(`/users/search?name=${encodeURIComponent(name)}`);

/**
 * الحصول على عدد المستخدمين
 * @returns {Promise} - عدد المستخدمين
 */
export const getUsersCount = () => callApi('/users/count');

// ==================== دوال إدارة الرسائل ====================

/**
 * إضافة رسالة جديدة مع تحليل المشاعر
 * @param {Object} messageData - بيانات الرسالة
 * @returns {Promise} - نتيجة إضافة الرسالة
 */
export const addMessage = (messageData) => {
    const processedData = processMessageData(messageData);
    return callApi('/messages/add', 'POST', processedData);
};

/**
 * معالجة رسالة كاملة (إنشاء مستخدم إذا لم يكن موجوداً + إضافة رسالة)
 * @param {Object} fullMessageData - البيانات الكاملة للرسالة
 * @returns {Promise} - نتيجة المعالجة
 */
export const processFullMessage = async (fullMessageData) => {
    try {
        // محاولة إنشاء المستخدم أولاً
        let userId = fullMessageData.user_id;
        
        if (!userId) {
            const userResult = await createUser({
                sender_name: fullMessageData.sender_name,
                gender: fullMessageData.gender,
                approximate_age: fullMessageData.approximate_age
            });
            userId = userResult.user_id;
        }
        
        // إضافة الرسالة
        const messageResult = await addMessage({
            user_id: userId,
            message_content: fullMessageData.message_content,
            dominant_emotion: fullMessageData.dominant_emotion,
            emotion_history_20s: fullMessageData.emotion_history_20s
        });
        
        return {
            user_id: userId,
            message_result: messageResult
        };
    } catch (error) {
        throw new Error(`فشل في معالجة الرسالة: ${error.message}`);
    }
};

/**
 * الحصول على رسالة بالمعرف
 * @param {string} messageId - معرف الرسالة
 * @returns {Promise} - بيانات الرسالة
 */
export const getMessage = (messageId) => callApi(`/messages/${messageId}/get`);

/**
 * الحصول على رسائل مستخدم معين
 * @param {string} userId - معرف المستخدم
 * @param {number} limit - الحد الأقصى لعدد الرسائل (اختياري)
 * @returns {Promise} - قائمة رسائل المستخدم
 */
export const getUserMessages = (userId, limit = null) => {
    const query = limit ? `?limit=${limit}` : '';
    return callApi(`/messages/user/${userId}${query}`);
};

/**
 * الحصول على أحدث الرسائل
 * @param {number} limit - الحد الأقصى لعدد الرسائل (اختياري)
 * @returns {Promise} - قائمة أحدث الرسائل
 */
export const getRecentMessages = (limit = null) => {
    const query = limit ? `?limit=${limit}` : '';
    return callApi(`/messages/recent${query}`);
};

/**
 * البحث في محتوى الرسائل
 * @param {string} query - كلمة البحث
 * @returns {Promise} - قائمة الرسائل المطابقة
 */
export const searchMessagesContent = (query) => callApi(`/messages/search_content?query=${encodeURIComponent(query)}`);

/**
 * الحصول على الرسائل حسب نوع المشاعر
 * @param {string} emotion - نوع المشاعر
 * @returns {Promise} - قائمة الرسائل المطابقة
 */
export const getMessagesByEmotion = (emotion) => callApi(`/messages/by_emotion?emotion=${emotion}`);

/**
 * تحديث رسالة
 * @param {string} messageId - معرف الرسالة
 * @param {Object} messageData - البيانات المحدثة
 * @returns {Promise} - نتيجة التحديث
 */
export const updateMessage = (messageId, messageData) => callApi(`/messages/${messageId}/update`, 'PUT', messageData);

/**
 * حذف رسالة
 * @param {string} messageId - معرف الرسالة
 * @returns {Promise} - نتيجة الحذف
 */
export const deleteMessage = (messageId) => callApi(`/messages/${messageId}/delete`, 'DELETE');

/**
 * الحصول على عدد الرسائل
 * @returns {Promise} - عدد الرسائل
 */
export const getMessagesCount = () => callApi('/messages/count');

// ==================== دوال سجل المشاعر ====================

/**
 * الحصول على سجل مشاعر رسالة معينة
 * @param {string} messageId - معرف الرسالة
 * @returns {Promise} - سجل مشاعر الرسالة
 */
export const getMessageEmotionHistory = (messageId) => callApi(`/history/message/${messageId}`);

/**
 * الحصول على سجل مشاعر مستخدم معين
 * @param {string} userId - معرف المستخدم
 * @returns {Promise} - سجل مشاعر المستخدم
 */
export const getUserEmotionHistory = (userId) => callApi(`/history/user/${userId}`);

/**
 * تحديث وقت سجل المشاعر
 * @param {string} historyId - معرف سجل المشاعر
 * @param {string} newTimestamp - الوقت الجديد بتنسيق ISO
 * @returns {Promise} - نتيجة التحديث
 */
export const updateEmotionHistoryTimestamp = (historyId, newTimestamp) => 
    callApi(`/history/${historyId}/update_timestamp`, 'PUT', { new_timestamp: newTimestamp });

/**
 * حذف سجل مشاعر
 * @param {string} historyId - معرف سجل المشاعر
 * @returns {Promise} - نتيجة الحذف
 */
export const deleteEmotionHistory = (historyId) => callApi(`/history/${historyId}/delete`, 'DELETE');

// ==================== دوال مساعدة ====================

/**
 * معالجة مجموعة من الرسائل
 * @param {Array} messagesArray - مصفوفة الرسائل
 * @returns {Promise} - نتائج معالجة جميع الرسائل
 */
export const processBatchMessages = async (messagesArray) => {
    const results = [];
    
    for (const messageData of messagesArray) {
        try {
            const result = await processFullMessage(messageData);
            results.push({
                success: true,
                data: result,
                original: messageData
            });
        } catch (error) {
            results.push({
                success: false,
                error: error.message,
                original: messageData
            });
        }
    }
    
    return results;
};

/**
 * الحصول على إحصائيات شاملة
 * @returns {Promise} - إحصائيات النظام
 */
export const getSystemStats = async () => {
    try {
        const [usersCount, messagesCount] = await Promise.all([
            getUsersCount(),
            getMessagesCount()
        ]);
        
        return {
            users_count: usersCount.count,
            messages_count: messagesCount.count,
            timestamp: new Date().toISOString()
        };
    } catch (error) {
        throw new Error(`فشل في الحصول على الإحصائيات: ${error.message}`);
    }
};

/**
 * تحليل المشاعر لفترة زمنية معينة
 * @param {string} startDate - تاريخ البداية
 * @param {string} endDate - تاريخ النهاية
 * @returns {Promise} - تحليل المشاعر للفترة
 */
export const getEmotionAnalysisForPeriod = async (startDate, endDate) => {
    try {
        const recentMessages = await getRecentMessages(100);
        
        // تصفية الرسائل حسب الفترة الزمنية
        const filteredMessages = recentMessages.filter(message => {
            const messageDate = new Date(message.timestamp);
            return messageDate >= new Date(startDate) && messageDate <= new Date(endDate);
        });
        
        // تحليل المشاعر
        const emotionCounts = {};
        filteredMessages.forEach(message => {
            const emotion = message.dominant_emotion;
            emotionCounts[emotion] = (emotionCounts[emotion] || 0) + 1;
        });
        
        return {
            period: { start: startDate, end: endDate },
            total_messages: filteredMessages.length,
            emotion_distribution: emotionCounts,
            messages: filteredMessages
        };
    } catch (error) {
        throw new Error(`فشل في تحليل المشاعر للفترة: ${error.message}`);
    }
};

// تصدير جميع الدوال كوحدة واحدة
export default {
    // إدارة المستخدمين
    createUser,
    deleteUser,
    getUser,
    getAllUsers,
    updateUser,
    searchUsers,
    getUsersCount,
    
    // إدارة الرسائل
    addMessage,
    processFullMessage,
    getMessage,
    getUserMessages,
    getRecentMessages,
    searchMessagesContent,
    getMessagesByEmotion,
    updateMessage,
    deleteMessage,
    getMessagesCount,
    
    // سجل المشاعر
    getMessageEmotionHistory,
    getUserEmotionHistory,
    updateEmotionHistoryTimestamp,
    deleteEmotionHistory,
    
    // دوال مساعدة
    processBatchMessages,
    getSystemStats,
    getEmotionAnalysisForPeriod,
    
    // دوال المعالجة
    processMessageData,
    processUserData
};

