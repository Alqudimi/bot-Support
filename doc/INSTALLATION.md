# دليل التثبيت - نظام تحليل المشاعر

## المتطلبات الأساسية

### متطلبات النظام
- **نظام التشغيل**: Windows 10/11، macOS 10.14+، أو Linux (Ubuntu 18.04+)
- **الذاكرة**: 2 GB RAM كحد أدنى، 4 GB مُوصى به
- **مساحة القرص**: 500 MB مساحة فارغة
- **الشبكة**: اتصال بالإنترنت لتحميل المتطلبات

### متطلبات البرمجيات
- **Python**: الإصدار 3.8 أو أحدث
- **pip**: مدير حزم Python (يأتي مع Python)
- **متصفح ويب**: Chrome، Firefox، Safari، أو Edge

---

## التحقق من Python

### Windows
1. افتح Command Prompt (cmd)
2. اكتب الأمر التالي:
```cmd
python --version
```
أو
```cmd
python3 --version
```

### macOS/Linux
1. افتح Terminal
2. اكتب الأمر التالي:
```bash
python3 --version
```

إذا لم يكن Python مثبتاً، قم بتحميله من [python.org](https://www.python.org/downloads/)

---

## خطوات التثبيت

### الطريقة الأولى: التثبيت السريع

1. **تحميل المشروع**
   ```bash
   # إذا كان لديك git
   git clone <repository-url>
   cd emotion-analysis-system
   
   # أو قم بتحميل وفك ضغط الملف المضغوط
   ```

2. **تثبيت المتطلبات**
   ```bash
   pip install flask flask-sqlalchemy flask-cors flask-limiter flask-caching
   ```

3. **تشغيل النظام**
   ```bash
   python app.py
   ```

4. **فتح واجهة الاختبار**
   - افتح متصفح الويب
   - اذهب إلى مجلد المشروع
   - افتح ملف `test_api.html`

### الطريقة الثانية: التثبيت المفصل

#### الخطوة 1: إعداد البيئة الافتراضية (مُوصى به)

**Windows:**
```cmd
python -m venv emotion_env
emotion_env\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv emotion_env
source emotion_env/bin/activate
```

#### الخطوة 2: تحديث pip
```bash
pip install --upgrade pip
```

#### الخطوة 3: تثبيت المتطلبات واحداً تلو الآخر
```bash
pip install flask==2.3.3
pip install flask-sqlalchemy==3.1.1
pip install flask-cors==4.0.0
pip install flask-limiter==3.5.0
pip install flask-caching==2.1.0
```

#### الخطوة 4: التحقق من التثبيت
```bash
pip list
```

يجب أن ترى قائمة تحتوي على جميع الحزم المثبتة.

---

## إعداد قاعدة البيانات

النظام يستخدم SQLite ولا يحتاج إعداد إضافي. ستُنشأ قاعدة البيانات تلقائياً عند أول تشغيل.

### التحقق من إنشاء قاعدة البيانات
بعد تشغيل النظام لأول مرة، ستجد ملف `emotion_analysis.db` في مجلد المشروع.

---

## تشغيل النظام

### تشغيل الخادم
```bash
python app.py
```

### رسائل التشغيل الناجح
```
 * Serving Flask app 'app'
 * Debug mode: on
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:5000
 * Running on http://[your-ip]:5000
```

### اختبار النظام
1. افتح متصفح الويب
2. اذهب إلى `http://127.0.0.1:5000/api/users/count`
3. يجب أن ترى استجابة JSON مثل: `{"count": 0}`

---

## حل المشاكل الشائعة

### مشكلة: "python is not recognized"
**الحل:**
- تأكد من تثبيت Python بشكل صحيح
- أضف Python إلى متغير PATH في النظام
- استخدم `python3` بدلاً من `python` في macOS/Linux

### مشكلة: "pip is not recognized"
**الحل:**
```bash
python -m pip install --upgrade pip
```

### مشكلة: "Permission denied"
**الحل (Linux/macOS):**
```bash
sudo pip3 install flask flask-sqlalchemy flask-cors flask-limiter flask-caching
```

### مشكلة: "Port 5000 is already in use"
**الحل:**
1. أوقف أي تطبيق يستخدم المنفذ 5000
2. أو غيّر المنفذ في ملف `app.py`:
```python
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
```

### مشكلة: "ModuleNotFoundError"
**الحل:**
تأكد من تثبيت جميع المتطلبات:
```bash
pip install -r requirements.txt
```

إذا لم يكن ملف requirements.txt موجوداً، قم بتثبيت المتطلبات يدوياً:
```bash
pip install flask flask-sqlalchemy flask-cors flask-limiter flask-caching
```

---

## إنشاء ملف requirements.txt

لسهولة التثبيت في المستقبل، يمكنك إنشاء ملف requirements.txt:

```bash
pip freeze > requirements.txt
```

ثم يمكن للآخرين تثبيت جميع المتطلبات بأمر واحد:
```bash
pip install -r requirements.txt
```

---

## التحقق من التثبيت الناجح

### اختبار API
```bash
curl http://127.0.0.1:5000/api/users/count
```

### اختبار واجهة المستخدم
1. افتح `test_api.html` في المتصفح
2. انقر على زر "عدد المستخدمين"
3. يجب أن ترى النتيجة في الصفحة

---

## إعداد الإنتاج

### استخدام Gunicorn (Linux/macOS)
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### استخدام Waitress (Windows)
```bash
pip install waitress
waitress-serve --host=0.0.0.0 --port=5000 app:app
```

### متغيرات البيئة
```bash
export FLASK_ENV=production
export FLASK_DEBUG=False
```

---

## النسخ الاحتياطي والاستعادة

### نسخ احتياطي لقاعدة البيانات
```bash
cp emotion_analysis.db emotion_analysis_backup.db
```

### استعادة قاعدة البيانات
```bash
cp emotion_analysis_backup.db emotion_analysis.db
```

---

## التحديث

### تحديث المتطلبات
```bash
pip install --upgrade flask flask-sqlalchemy flask-cors flask-limiter flask-caching
```

### تحديث النظام
1. قم بعمل نسخة احتياطية من قاعدة البيانات
2. حمّل الإصدار الجديد
3. شغّل النظام للتحقق من التوافق

---

## الدعم

إذا واجهت أي مشاكل في التثبيت:

1. **تحقق من ملف test_results.md** للمشاكل الشائعة
2. **راجع ملف README.md** للمعلومات العامة
3. **تأكد من إصدار Python** (3.8 أو أحدث)
4. **تحقق من اتصال الإنترنت** لتحميل المتطلبات

---

## ملاحظات مهمة

- **لا تستخدم هذا الإعداد في الإنتاج** بدون إعدادات أمان إضافية
- **قم بعمل نسخ احتياطية منتظمة** لقاعدة البيانات
- **راقب استخدام الموارد** عند التشغيل على خوادم الإنتاج
- **استخدم HTTPS** في بيئة الإنتاج

تم إعداد هذا الدليل ليكون شاملاً وسهل المتابعة. إذا كنت تحتاج مساعدة إضافية، راجع الملفات الأخرى في التوثيق.

