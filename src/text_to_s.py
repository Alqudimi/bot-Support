import requests
import os
import platform
import subprocess

def convert_text_to_speech(text, output_file="output.mp3", voice_id="EXAVITQu4vr4xnSDxMaL", play_sound=True):
    """
    دالة لتحويل النص العربي إلى صوت باستخدام ElevenLabs API وحفظه وتشغيله
    
    المعطيات:
        text (str): النص المراد تحويله إلى صوت
        output_file (str): اسم ملف الإخراج (افتراضي: "output.mp3")
        voice_id (str): معرف الصوت في ElevenLabs (افتراضي: صوت يدعم العربية)
        play_sound (bool): إذا كان True سيتم تشغيل الصوت بعد التحويل (افتراضي: True)
    """
    API_KEY = ""
    
    headers = {
        "xi-api-key": API_KEY,
        "Content-Type": "application/json"
    }

    data = {
        "text": text,
        "model_id": "eleven_multilingual_v2",  # يدعم العربية
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.5
        }
    }

    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"

    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        output_file = os.path.join('../output/sound',output_file)
        with open(output_file, "wb") as f:
            f.write(response.content)
        print(f"✅ تم حفظ الملف الصوتي بنجاح باسم: {output_file}")
        
        if play_sound:
            try:
                # تشغيل الصوت حسب نظام التشغيل
                if platform.system() == "Windows":
                    os.startfile(output_file)
                elif platform.system() == "Darwin":  # MacOS
                    subprocess.call(["afplay", output_file])
                else:  # Linux وغيرها
                    subprocess.call(["aplay", output_file])
            except Exception as e:
                print(f"⚠️ تعذر تشغيل الصوت: {e}")
                
        return True
    else:
        print(f"❌ فشل الطلب. رمز الاستجابة: {response.status_code}")
        print(response.text)
        return False


if __name__ == "__main__":
    convert_text_to_speech("هذا نص آخر سيتم تحويله إلى صوت", "my_voice.mp3")