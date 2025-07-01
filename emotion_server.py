from flask import Flask, jsonify
import cv2
from deepface import DeepFace
import time
from collections import Counter
import threading

app = Flask(__name__)

def detect_emotion():
    cap = cv2.VideoCapture(0)
    detected_emotions = []
    start_time = time.time()
    frame_count = 0

    def analyze_frame(frame):
        try:
            small_frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)  # Resize for faster processing
            analysis = DeepFace.analyze(small_frame, actions=['emotion'], enforce_detection=False)
            emotion = analysis[0]['dominant_emotion']
            detected_emotions.append(emotion)
        except:
            detected_emotions.append("neutral")

    while time.time() - start_time < 10:
        ret, frame = cap.read()
        if not ret:
            continue

        frame_count += 1
        if frame_count % 5 == 0:  # Process 1 out of every 5 frames
            threading.Thread(target=analyze_frame, args=(frame,)).start()

    cap.release()

    if detected_emotions:
        most_common_emotion = Counter(detected_emotions).most_common(1)[0][0]
    else:
        most_common_emotion = "neutral"

    return {"emotion": most_common_emotion}

@app.route('/detect_emotion', methods=['GET'])
def get_emotion():
    emotion_data = detect_emotion()
    return jsonify(emotion_data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
