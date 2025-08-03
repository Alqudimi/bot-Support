

class EmotionAnalysisAPI {
    constructor(baseURL = 'http://localhost:5000') {
        this.baseURL = baseURL;
        this.token = localStorage.getItem('auth_token');
        this.currentUser = null;
        this.currentSession = null;
    }

    // دوال المساعدة
    async makeRequest(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
                ...(this.token && { 'Authorization': `Bearer ${this.token}` })
            }
        };

        const finalOptions = { ...defaultOptions, ...options };
        
        try {
            const response = await fetch(url, finalOptions);
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.error || `HTTP error! status: ${response.status}`);
            }
            
            return data;
        } catch (error) {
            console.error('API Request Error:', error);
            throw error;
        }
    }

    // دوال المصادقة والمستخدمين
    async registerUser(userData) {
        try {
            const response = await this.makeRequest('/api/users/register', {
                method: 'POST',
                body: JSON.stringify(userData)
            });
            
            if (response.success && response.token) {
                this.token = response.token;
                localStorage.setItem('auth_token', this.token);
                this.currentUser = response.user;
            }
            
            return response;
        } catch (error) {
            console.error('Registration error:', error);
            throw error;
        }
    }

    async loginAsGuest() {
        try {
            const response = await this.makeRequest('/api/users/guest', {
                method: 'POST'
            });
            
            if (response.success && response.token) {
                this.token = response.token;
                localStorage.setItem('auth_token', this.token);
                this.currentUser = response.user;
            }
            
            return response;
        } catch (error) {
            console.error('Guest login error:', error);
            throw error;
        }
    }

    async getCurrentUser() {
        if (!this.token) return null;
        
        try {
            const response = await this.makeRequest('/api/users/me');
            if (response.success) {
                this.currentUser = response.user;
                return response.user;
            }
        } catch (error) {
            console.error('Get current user error:', error);
            this.logout();
        }
        return null;
    }

    logout() {
        this.token = null;
        this.currentUser = null;
        this.currentSession = null;
        localStorage.removeItem('auth_token');
    }

    // دوال الجلسات
    async startSession() {
        try {
            const response = await this.makeRequest('/api/sessions/start', {
                method: 'POST'
            });
            
            if (response.success) {
                this.currentSession = response.session;
            }
            
            return response;
        } catch (error) {
            console.error('Start session error:', error);
            throw error;
        }
    }

    async endSession() {
        if (!this.currentSession) return;
        
        try {
            const response = await this.makeRequest(`/api/sessions/${this.currentSession.id}/end`, {
                method: 'POST'
            });
            
            if (response.success) {
                this.currentSession = null;
            }
            
            return response;
        } catch (error) {
            console.error('End session error:', error);
            throw error;
        }
    }

    // دوال حفظ بيانات المشاعر
    async saveEmotionSnapshot(emotionData) {
        if (!this.currentSession) {
            console.warn('No active session for saving emotion data');
            return;
        }

        try {
            const snapshotData = {
                session_id: this.currentSession.id,
                timestamp: new Date().toISOString(),
                dominant_emotion: emotionData.dominantEmotion,
                emotion_scores: emotionData.emotions,
                age: emotionData.age,
                gender: emotionData.gender,
                face_landmarks: emotionData.landmarks,
                confidence_scores: {
                    emotion: emotionData.emotionConfidence || 0.8,
                    age: emotionData.ageConfidence || 0.7,
                    gender: emotionData.genderConfidence || 0.9
                }
            };

            const response = await this.makeRequest('/api/emotions/snapshot', {
                method: 'POST',
                body: JSON.stringify(snapshotData)
            });

            return response;
        } catch (error) {
            console.error('Save emotion snapshot error:', error);
            throw error;
        }
    }

    // دوال لوحة التحكم
    async getDashboardStats() {
        try {
            return await this.makeRequest('/api/dashboard/stats');
        } catch (error) {
            console.error('Get dashboard stats error:', error);
            throw error;
        }
    }

    async getActiveSessions() {
        try {
            return await this.makeRequest('/api/dashboard/active-sessions');
        } catch (error) {
            console.error('Get active sessions error:', error);
            throw error;
        }
    }

    async getSystemLogs(level = 'all') {
        try {
            return await this.makeRequest(`/api/dashboard/system-logs?level=${level}`);
        } catch (error) {
            console.error('Get system logs error:', error);
            throw error;
        }
    }

    // دوال الإحصائيات
    async getStatisticsOverview(period = 'week') {
        try {
            return await this.makeRequest(`/api/statistics/overview?period=${period}`);
        } catch (error) {
            console.error('Get statistics overview error:', error);
            throw error;
        }
    }

    // دوال إدارة المستخدمين
    async getUsersList(params = {}) {
        try {
            const queryParams = new URLSearchParams(params).toString();
            return await this.makeRequest(`/api/users/list?${queryParams}`);
        } catch (error) {
            console.error('Get users list error:', error);
            throw error;
        }
    }

    async getUserDetails(userId) {
        try {
            return await this.makeRequest(`/api/users/${userId}`);
        } catch (error) {
            console.error('Get user details error:', error);
            throw error;
        }
    }

    async updateUser(userId, userData) {
        try {
            return await this.makeRequest(`/api/users/${userId}`, {
                method: 'PUT',
                body: JSON.stringify(userData)
            });
        } catch (error) {
            console.error('Update user error:', error);
            throw error;
        }
    }

    async deleteUser(userId) {
        try {
            return await this.makeRequest(`/api/users/${userId}`, {
                method: 'DELETE'
            });
        } catch (error) {
            console.error('Delete user error:', error);
            throw error;
        }
    }

    async getUsersStats() {
        try {
            return await this.makeRequest('/api/users/stats');
        } catch (error) {
            console.error('Get users stats error:', error);
            throw error;
        }
    }

    // دوال مساعدة للواجهة
    formatDate(dateString) {
        const date = new Date(dateString);
        return date.toLocaleDateString('ar-SA', {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit'
        });
    }

    formatDuration(seconds) {
        const minutes = Math.floor(seconds / 60);
        const remainingSeconds = seconds % 60;
        return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
    }

    getEmotionLabel(emotion) {
        const emotionLabels = {
            'happy': 'سعيد',
            'sad': 'حزين',
            'angry': 'غاضب',
            'surprised': 'متفاجئ',
            'fearful': 'خائف',
            'disgusted': 'مشمئز',
            'neutral': 'محايد'
        };
        return emotionLabels[emotion] || emotion;
    }

    getGenderLabel(gender) {
        const genderLabels = {
            'male': 'ذكر',
            'female': 'أنثى'
        };
        return genderLabels[gender] || gender;
    }

    // دالة لحفظ البيانات تلقائياً كل 5 ثوانٍ
    startAutoSave(getEmotionDataCallback) {
        if (this.autoSaveInterval) {
            clearInterval(this.autoSaveInterval);
        }

        this.autoSaveInterval = setInterval(async () => {
            try {
                const emotionData = getEmotionDataCallback();
                if (emotionData && this.currentSession) {
                    await this.saveEmotionSnapshot(emotionData);
                    console.log('Auto-saved emotion data');
                }
            } catch (error) {
                console.error('Auto-save error:', error);
            }
        }, 5000); // كل 5 ثوانٍ
    }

    stopAutoSave() {
        if (this.autoSaveInterval) {
            clearInterval(this.autoSaveInterval);
            this.autoSaveInterval = null;
        }
    }

    // دالة لتحديث بيانات المستخدم من face-api.js
    async updateUserFromFaceAPI(faceData) {
        if (!this.currentUser || this.currentUser.is_guest) return;

        try {
            const updateData = {};
            
            // تحديث العمر إذا لم يكن محدداً
            if (!this.currentUser.age && faceData.age) {
                updateData.age = Math.round(faceData.age);
            }
            
            // تحديث الجنس إذا لم يكن محدداً
            if (!this.currentUser.gender && faceData.gender) {
                updateData.gender = faceData.gender;
            }

            if (Object.keys(updateData).length > 0) {
                const response = await this.updateUser(this.currentUser.id, updateData);
                if (response.success) {
                    // تحديث البيانات المحلية
                    Object.assign(this.currentUser, updateData);
                    console.log('Updated user data from face-api:', updateData);
                }
            }
        } catch (error) {
            console.error('Update user from face-api error:', error);
        }
    }
}

// إنشاء مثيل عام للاستخدام
const emotionAPI = new EmotionAnalysisAPI();

// تصدير للاستخدام في modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = EmotionAnalysisAPI;
}

