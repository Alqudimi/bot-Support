import cv2
from deepface import DeepFace
class AnalyzeEmotion:
    def __init__(self):
        pass
    def _deepface(self,frame):            
        result = DeepFace.analyze(frame, actions=['emotion'], enforce_detection=False)
        return result[0]['dominant_emotion']
            
            
def deepface():
        emotions = AnalyzeEmotion()
        cap = cv2.VideoCapture(0)
        isRun = True
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Error: Could not read frame.")
                break
            
            if isRun:
                emotion = emotions._deepface(frame)
            
            # Display the emotion on the frame
            cv2.putText(frame, f'Emotion: {emotion}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
            
            # Show the frame
            cv2.imshow('Emotion Detection', frame)
            isRun = not isRun
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break


