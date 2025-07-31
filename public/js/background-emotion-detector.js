

class BackgroundEmotionDetector {
    constructor() {
        this.video = null;
        this.canvas = null;
        this.ctx = null;
        this.isRunning = false;
        this.detectionInterval = null;
        this.apiUrl = null;
        this.stats = {
            frameCount: 0,
            detectionCount: 0,
            startTime: null,
            lastFrameTime: 0
        };
        this.emotionData = [];
        this.sendInterval = null;
    }

    
    async init(apiUrl, options = {}) {
        this.apiUrl = apiUrl;
        this.options = {
            detectionInterval: options.detectionInterval || 100, // ms
            sendInterval: options.sendInterval || 100, // ms
            videoWidth: options.videoWidth || 640,
            videoHeight: options.videoHeight || 480,
            ...options
        };

        try {
            console.log('🎭 بدء تحميل نماذج تحليل المشاعر...');
            
            // تحميل النماذج المطلوبة
            await this.loadModels();
            
            console.log('✅ تم تحميل النماذج بنجاح');
            
            // طلب صلاحيات الكاميرا وبدء العمل
            await this.requestPermissionsAndStart();
            
        } catch (error) {
            console.error('❌ خطأ في تهيئة النظام:', error);
            throw error;
        }
    }

   
    async loadModels() {
        const modelPath = 'https://justadudewhohacks.github.io/face-api.js/models';
        
        await Promise.all([
            faceapi.nets.tinyFaceDetector.loadFromUri(modelPath),
            faceapi.nets.faceLandmark68Net.loadFromUri(modelPath),
            faceapi.nets.faceRecognitionNet.loadFromUri(modelPath),
            faceapi.nets.faceExpressionNet.loadFromUri(modelPath)
        ]);
    }

    
    async requestPermissionsAndStart() {
        try {
            console.log('📹 طلب صلاحيات الكاميرا...');
            
            // إنشاء عناصر الفيديو والكانفاس (مخفية)
            this.createHiddenElements();
            
            // طلب صلاحية الكاميرا
            const stream = await navigator.mediaDevices.getUserMedia({
                video: { 
                    width: this.options.videoWidth, 
                    height: this.options.videoHeight,
                    facingMode: 'user'
                }
            });

            this.video.srcObject = stream;
            
            // انتظار تحميل الفيديو
            await new Promise((resolve) => {
                this.video.addEventListener('loadedmetadata', () => {
                    this.canvas.width = this.video.videoWidth;
                    this.canvas.height = this.video.videoHeight;
                    resolve();
                });
            });

            console.log('✅ تم الحصول على صلاحيات الكاميرا');
            
            // بدء العمل في الخلفية
            this.startBackgroundDetection();
            
        } catch (error) {
            console.error('❌ خطأ في طلب صلاحيات الكاميرا:', error);
            throw error;
        }
    }

    /**
     * إنشاء عناصر الفيديو والكانفاس المخفية
     */
    createHiddenElements() {
        try {
        // إنشاء عنصر الفيديو
            this.video = document.createElement('video');
            this.video.width = this.options.videoWidth;
            this.video.height = this.options.videoHeight;
            this.video.autoplay = true;
            this.video.muted = true;
            this.video.playsInline = true;
            //this.video.style.display = 'none'; // 
            
            this.video.style.visibility = 'hidden';
            document.body.appendChild(this.video);

            this.canvas = document.createElement('canvas');
            this.canvas.width = this.options.videoWidth;
            this.canvas.height = this.options.videoHeight;
            //this.canvas.style.display = 'none'; // مخفي
            document.body.appendChild(this.canvas);
            
            this.ctx = this.canvas.getContext('2d');
            console.log('loaded createHiddenElements')
        } catch (error) {
            console.error('❌ خطأ في كشف المشاعر:', error);
        }
    }

    /**
     * بدء الكشف في الخلفية
     */
    startBackgroundDetection() {
        this.isRunning = true;
        this.stats.startTime = Date.now();
        
        console.log('🚀 بدء تحليل المشاعر في الخلفية...');
        console.log(this.options.sendInterval);

        this.detectionInterval = setInterval(() => {
            this.detectEmotions();
        }, this.options.detectionInterval);
        
        // بدء إرسال البيانات
        this.sendInterval = setInterval(() => {
            this.sendDataToAPI();
        }, this.options.sendInterval);
    }

    /**
     * كشف المشاعر من الإطار الحالي
     */
    async detectEmotions() {
        if (!this.isRunning || this.video.ended ) return;
        
        try {
            this.stats.frameCount++;

            // كشف الوجوه والمشاعر
            const detections = await faceapi
                .detectAllFaces(this.video, new faceapi.TinyFaceDetectorOptions())
                .withFaceLandmarks()
                .withFaceExpressions();
            
            console.log('detections',detections.length)

            if (detections.length > 0) {
                this.stats.detectionCount++;
                
                // معالجة أول وجه مكتشف
                const detection = detections[0];
                const emotions = detection.expressions;
                //console.log('emotions',emotions);
                // حفظ البيانات
                this.saveEmotionData(emotions);
                
                // طباعة النتائج في الكونسول
                this.logEmotions(emotions);
            }

        } catch (error) {
            console.error('❌ خطأ في كشف المشاعر:', error);
        }
    }

    /**
     * حفظ بيانات المشاعر
     */
    saveEmotionData(emotions) {
        const timestamp = Date.now();
        const emotionEntry = {
            timestamp,
            emotions: { ...emotions },
            dominantEmotion: this.getDominantEmotion(emotions),
            confidence: Math.max(...Object.values(emotions))
        };
        
        this.emotionData.push(emotionEntry);
        
        // الاحتفاظ بآخر 100 قراءة فقط لتوفير الذاكرة
        if (this.emotionData.length > 100) {
            this.emotionData.shift();
        }
    }

    /**
     * طباعة المشاعر في الكونسول
     */
    logEmotions(emotions) {
        const dominantEmotion = this.getDominantEmotion(emotions);
        const confidence = (emotions[dominantEmotion] * 100).toFixed(1);
        
        console.log(`🎭 المشاعر المكتشفة:`, {
            الوقت: new Date().toLocaleTimeString('ar-SA'),
            'المشاعر السائدة': this.getEmotionArabic(dominantEmotion),
            'نسبة الثقة': `${confidence}%`,
            'جميع المشاعر': {
                'سعيد': `${(emotions.happy * 100).toFixed(1)}%`,
                'حزين': `${(emotions.sad * 100).toFixed(1)}%`,
                'غاضب': `${(emotions.angry * 100).toFixed(1)}%`,
                'متفاجئ': `${(emotions.surprised * 100).toFixed(1)}%`,
                'خائف': `${(emotions.fearful * 100).toFixed(1)}%`,
                'مشمئز': `${(emotions.disgusted * 100).toFixed(1)}%`,
                'محايد': `${(emotions.neutral * 100).toFixed(1)}%`
            }
        });
    }

    /**
     * إرسال البيانات إلى API
     */
    async sendDataToAPI() {
        if (!this.apiUrl || this.emotionData.length === 0) return;

        try {
            const dataToSend = {
                timestamp: Date.now(),
                sessionId: this.generateSessionId(),
                stats: {
                    ...this.stats,
                    uptime: Date.now() - this.stats.startTime,
                    fps: this.calculateFPS()
                },
                recentEmotions: this.emotionData.slice(-10), // آخر 10 قراءات
                summary: this.generateSummary()
            };

            console.log('📤 إرسال البيانات إلى API:', this.apiUrl);
            
            const response = await fetch(this.apiUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(dataToSend)
            });

            if (response.ok) {
                console.log('✅ تم إرسال البيانات بنجاح');
            } else {
                console.error('❌ خطأ في إرسال البيانات:', response.status, response.statusText);
            }

        } catch (error) {
            console.error('❌ خطأ في الاتصال بـ API:', error);
        }
    }

    /**
     * توليد معرف جلسة فريد
     */
    generateSessionId() {
        return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    }

    /**
     * حساب FPS
     */
    calculateFPS() {
        const now = Date.now();
        const elapsed = (now - this.stats.startTime) / 1000;
        return elapsed > 0 ? Math.round(this.stats.frameCount / elapsed) : 0;
    }

    /**
     * توليد ملخص للبيانات
     */
    generateSummary() {
        if (this.emotionData.length === 0) return null;

        const emotionCounts = {
            happy: 0, sad: 0, angry: 0, surprised: 0,
            fearful: 0, disgusted: 0, neutral: 0
        };

        let totalConfidence = 0;

        this.emotionData.forEach(entry => {
            const dominant = entry.dominantEmotion;
            emotionCounts[dominant]++;
            totalConfidence += entry.confidence;
        });

        const mostFrequentEmotion = Object.keys(emotionCounts).reduce((a, b) => 
            emotionCounts[a] > emotionCounts[b] ? a : b
        );

        return {
            mostFrequentEmotion: this.getEmotionArabic(mostFrequentEmotion),
            averageConfidence: (totalConfidence / this.emotionData.length * 100).toFixed(1),
            emotionDistribution: emotionCounts,
            totalReadings: this.emotionData.length
        };
    }

    /**
     * الحصول على المشاعر السائدة
     */
    getDominantEmotion(emotions) {
        return Object.keys(emotions).reduce((a, b) => 
            emotions[a] > emotions[b] ? a : b
        );
    }

    /**
     * ترجمة المشاعر إلى العربية
     */
    getEmotionArabic(emotion) {
        const translations = {
            happy: 'سعيد',
            sad: 'حزين',
            angry: 'غاضب',
            surprised: 'متفاجئ',
            fearful: 'خائف',
            disgusted: 'مشمئز',
            neutral: 'محايد'
        };
        return translations[emotion] || emotion;
    }

    /**
     * إيقاف النظام
     */
    stop() {
        console.log('⏹️ إيقاف تحليل المشاعر...');
        
        this.isRunning = false;
        
        // إيقاف الفواصل الزمنية
        if (this.detectionInterval) {
            clearInterval(this.detectionInterval);
            this.detectionInterval = null;
        }
        
        if (this.sendInterval) {
            clearInterval(this.sendInterval);
            this.sendInterval = null;
        }
        
        // إيقاف الكاميرا
        if (this.video && this.video.srcObject) {
            const tracks = this.video.srcObject.getTracks();
            tracks.forEach(track => track.stop());
            this.video.srcObject = null;
        }
        
        // إزالة العناصر المخفية
        if (this.video) {
            document.body.removeChild(this.video);
            this.video = null;
        }
        
        if (this.canvas) {
            document.body.removeChild(this.canvas);
            this.canvas = null;
        }
        
        console.log('✅ تم إيقاف النظام');
    }

    /**
     * الحصول على الإحصائيات الحالية
     */
    getStats() {
        return {
            ...this.stats,
            uptime: this.stats.startTime ? Date.now() - this.stats.startTime : 0,
            fps: this.calculateFPS(),
            isRunning: this.isRunning,
            emotionDataCount: this.emotionData.length
        };
    }

    /**
     * الحصول على آخر البيانات
     */
    getLatestData(count = 10) {
        return this.emotionData.slice(-count);
    }
}

// إنشاء مثيل عام
window.BackgroundEmotionDetector = new BackgroundEmotionDetector();

// تصدير للاستخدام مع ES6 modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = BackgroundEmotionDetector;
}

// رسالة ترحيب
console.log(`
🎭 مكتبة تحليل المشاعر في الخلفية جاهزة!

للاستخدام:
1. تأكد من تضمين face-api.js في صفحتك
2. استدعي: BackgroundEmotionDetector.init('YOUR_API_URL')

مثال:
BackgroundEmotionDetector.init('https://your-api.com/emotions', {
    detectionInterval: 100,  // كشف كل 100ms
    sendInterval: 5000,      // إرسال كل 5 ثوان
    videoWidth: 640,
    videoHeight: 480
});

للإيقاف:
BackgroundEmotionDetector.stop();

للحصول على الإحصائيات:
BackgroundEmotionDetector.getStats();
`);

