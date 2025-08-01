import cv2
import numpy as np
import os
import pickle

class FaceRecognitionSystem:
    def __init__(self, data_path='face_data.pkl'):
        self.data_path = data_path
        self.known_face_encodings = []
        self.known_face_names = []
        
        self.face_detector = cv2.dnn.readNetFromCaffe(
            os.path.join(os.getcwd(), 'deploy.prototxt.txt'),
            os.path.join(os.getcwd(), 'res10_300x300_ssd_iter_140000.caffemodel')
        )
        
        # Load OpenFace model for face embedding
        self.face_embedder = cv2.dnn.readNetFromTorch(
            os.path.join(os.getcwd(), 'openface_nn4.small2.v1.t7')
        )

        self._load_data()

    def _load_data(self):
        if os.path.exists(self.data_path):
            with open(self.data_path, 'rb') as f:
                data = pickle.load(f)
                self.known_face_encodings = data.get('encodings', [])
                self.known_face_names = data.get('names', [])

    def _save_data(self):
        with open(self.data_path, 'wb') as f:
                pickle.dump({'encodings': self.known_face_encodings, 'names': self.known_face_names}, f)

    def _get_face_encoding(self, image_path):
        image = cv2.imread(image_path)
        if image is None:
            print(f"Error: Could not load image from {image_path}")
            return None
        
        (h, w) = image.shape[:2]
        blob = cv2.dnn.blobFromImage(cv2.resize(image, (300, 300)), 1.0, (300, 300), (104.0, 177.0, 123.0))
        self.face_detector.setInput(blob)
        detections = self.face_detector.forward()

        faces = []
        for i in range(0, detections.shape[2]):
            confidence = detections[0, 0, i, 2]
            if confidence > 0.5: # Confidence threshold
                box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                (startX, startY, endX, endY) = box.astype("int")
                faces.append((startX, startY, endX - startX, endY - startY))

        if len(faces) == 0:
            print("No face found in the image.")
            return None
        elif len(faces) > 1:
            print("Multiple faces found. Please provide an image with a single face.")
            return None
        
        # Extract face ROI
        x, y, w, h = faces[0]
        face_roi = image[y:y+h, x:x+w]

        # Get face embedding using OpenFace model
        face_blob = cv2.dnn.blobFromImage(face_roi, 1.0 / 255, (96, 96), (0, 0, 0), swapRB=True, crop=False)
        self.face_embedder.setInput(face_blob)
        vec = self.face_embedder.forward()
        return vec.flatten()

    def register_face(self, image_path, name):
        encoding = self._get_face_encoding(image_path)
        if encoding is not None:
            self.known_face_encodings.append(encoding)
            self.known_face_names.append(name)
            self._save_data()
            print(f"Face of {name} registered successfully.")
            return True
        return False

    def recognize_face(self, image_path):
        unknown_encoding = self._get_face_encoding(image_path)
        if unknown_encoding is None:
            return None

        if not self.known_face_encodings:
            print("No registered faces found.")
            return None

        # Calculate Euclidean distances
        distances = [np.linalg.norm(known_encoding - unknown_encoding) for known_encoding in self.known_face_encodings]
        min_distance_index = np.argmin(distances)
        min_distance = distances[min_distance_index]

        # Threshold for recognition (this value needs to be tuned based on your dataset)
        if min_distance < 0.6:  # A common threshold for OpenFace embeddings
            return self.known_face_names[min_distance_index]
        else:
            return "Unknown"

    def delete_face(self, name):
        if name in self.known_face_names:
            indices_to_delete = [i for i, n in enumerate(self.known_face_names) if n == name]
            for index in sorted(indices_to_delete, reverse=True):
                del self.known_face_encodings[index]
                del self.known_face_names[index]
            self._save_data()
            print(f"Face(s) of {name} deleted successfully.")
            return True
        else:
            print(f"No registered face found for {name}.")
            return False

if __name__ == "__main__":
    system = FaceRecognitionSystem()

    # Register a face
    # Make sure you have an image named 'person1.jpg' in the same directory
    # system.register_face('person1.jpg', 'Alice')

    # Recognize a face
    # Make sure you have an image named 'person2.jpg' in the same directory
    # recognized_name = system.recognize_face('person2.jpg')
    # if recognized_name:
    #     print(f"Recognized: {recognized_name}")
    # else:
    #     print("Could not recognize face.")

    # Delete a face
    # system.delete_face('Alice')

