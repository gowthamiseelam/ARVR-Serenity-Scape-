import cv2
from flask import Flask, Response
from deepface import DeepFace

app = Flask(__name__)

# Initialize video capture
cap = cv2.VideoCapture(0)

# Check if the camera opened correctly
if not cap.isOpened():
    print("Error: Could not open video feed")
    exit()

# Video writer to save processed video
fourcc = cv2.VideoWriter_fourcc(*'XVID')
out = cv2.VideoWriter('emotion_output.avi', fourcc, 20.0, (640, 480))

frame_count = 0  # Counter to reduce processing load
last_detected_faces = []  # Store last detected emotions
last_detection_frame = 0  # Frame count when the last emotion was detected
DISPLAY_THRESHOLD = 30  # Number of frames to keep the last detected emotion
CONFIDENCE_THRESHOLD = 50  # Minimum confidence percentage for emotion display

# Generate video stream for Flask response with emotion detection
def gen():
    global frame_count, last_detected_faces, last_detection_frame
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        frame_count += 1

        # Process every 15th frame for better performance
        if frame_count % 15 == 0:
            try:
                results = DeepFace.analyze(frame, actions=['emotion'], enforce_detection=False)

                if isinstance(results, list):
                    # Filter faces with confidence above threshold
                    filtered_faces = []
                    for face in results:
                        emotion_data = face.get('emotion', {})
                        dominant_emotion = face.get('dominant_emotion', 'Unknown')
                        confidence = emotion_data.get(dominant_emotion, 0)

                        # Only update if confidence is high
                        if confidence > CONFIDENCE_THRESHOLD:
                            filtered_faces.append(face)
                    
                    if filtered_faces:
                        last_detected_faces = filtered_faces  # Update detected faces
                        last_detection_frame = frame_count  # Reset display timer

            except Exception as e:
                print(f"Emotion detection error: {e}")

        # Keep displaying last detected emotion for a while (smooth transitions)
        if frame_count - last_detection_frame < DISPLAY_THRESHOLD:
            for face in last_detected_faces:
                emotion = face.get('dominant_emotion', 'Unknown')
                region = face.get('region', {})

                x = region.get('x', 0)
                y = region.get('y', 0)
                w = region.get('w', 50)
                h = region.get('h', 50)

                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(frame, f"{emotion}", (x, y - 10), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

        # Save the frame to video file
        out.write(frame)

        _, jpeg = cv2.imencode('.jpg', frame)
        frame = jpeg.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

# Route for video feed
@app.route('/video_feed')
def video_feed():
    return Response(gen(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

# Home route with styled UI
@app.route('/')
def index():
    return '''
        <html>
            <head>
                <title>Emotion Detection</title>
                <style>
                    body { font-family: Arial, sans-serif; text-align: center; background-color: #f4f4f4; }
                    h1 { color: #333; }
                    .container { margin: 20px auto; padding: 20px; background: white; box-shadow: 0 0 10px rgba(0,0,0,0.1); border-radius: 10px; }
                    img { width: 80%; border-radius: 10px; border: 3px solid #333; }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>Live Emotion Detection</h1>
                    <img src="/video_feed">
                </div>
            </body>
        </html>
    '''

# Handle favicon.ico request
@app.route('/favicon.ico')
def favicon():
    return '', 204  # Return a "no content" response for the favicon request

if __name__ == '__main__':
    # Run the Flask app on host 0.0.0.0 and port 5000
    app.run(host='0.0.0.0', port=5000)

# Release resources when the script stops
cap.release()
out.release()
cv2.destroyAllWindows()
