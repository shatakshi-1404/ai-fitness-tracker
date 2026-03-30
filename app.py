import cv2
import threading
import time
from flask import Flask, Response, render_template, jsonify, request
from utils.pose_detector import PoseDetector, ExerciseCounter

app = Flask(__name__)

# ── Global state ─────────────────────────────────────────────────────────────
camera = None
camera_lock = threading.Lock()
detector = PoseDetector()
counter = ExerciseCounter()
streaming = False
frame_buffer = None
buffer_lock = threading.Lock()

# Stats
session_start = time.time()
fps_counter = {'frames': 0, 'last_time': time.time(), 'fps': 0}


# ── Camera management ─────────────────────────────────────────────────────────
def get_camera():
    global camera
    if camera is None or not camera.isOpened():
        camera = cv2.VideoCapture(0)
        camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        camera.set(cv2.CAP_PROP_FPS, 30)
    return camera


def release_camera():
    global camera, streaming
    streaming = False
    with camera_lock:
        if camera and camera.isOpened():
            camera.release()
            camera = None


def capture_frames():
    """Background thread: continuously reads and processes frames."""
    global frame_buffer, streaming

    while streaming:
        with camera_lock:
            cam = get_camera()
            success, frame = cam.read()

        if not success:
            time.sleep(0.05)
            continue

        # Flip horizontally (mirror)
        frame = cv2.flip(frame, 1)

        # Pose detection
        results = detector.process_frame(frame)
        frame = detector.draw_landmarks(frame, results)
        frame = counter.process(results, frame)

        # FPS tracking
        fps_counter['frames'] += 1
        now = time.time()
        elapsed = now - fps_counter['last_time']
        if elapsed >= 1.0:
            fps_counter['fps'] = round(fps_counter['frames'] / elapsed, 1)
            fps_counter['frames'] = 0
            fps_counter['last_time'] = now

        # Draw FPS
        cv2.putText(frame, f"FPS: {fps_counter['fps']}", (10, frame.shape[0] - 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (180, 180, 180), 1)

        # Encode to JPEG
        ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
        if ret:
            with buffer_lock:
                frame_buffer = buffer.tobytes()


def generate_frames():
    """Generator for MJPEG streaming."""
    while streaming:
        with buffer_lock:
            frame = frame_buffer

        if frame is None:
            time.sleep(0.03)
            continue

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        time.sleep(0.033)  # ~30 fps


# ── Routes ────────────────────────────────────────────────────────────────────
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/video_feed')
def video_feed():
    return Response(
        generate_frames(),
        mimetype='multipart/x-mixed-replace; boundary=frame'
    )


@app.route('/start_stream', methods=['POST'])
def start_stream():
    global streaming
    if not streaming:
        streaming = True
        t = threading.Thread(target=capture_frames, daemon=True)
        t.start()
    return jsonify({'status': 'started'})


@app.route('/stop_stream', methods=['POST'])
def stop_stream():
    release_camera()
    return jsonify({'status': 'stopped'})


@app.route('/set_exercise', methods=['POST'])
def set_exercise():
    data = request.get_json()
    exercise = data.get('exercise', 'squat')
    counter.set_exercise(exercise)
    return jsonify({'status': 'ok', 'exercise': exercise})


@app.route('/reset_counter', methods=['POST'])
def reset_counter():
    data = request.get_json()
    exercise = data.get('exercise', None)
    if exercise:
        counter.reset(exercise)
    else:
        counter.reset_all()
    return jsonify({'status': 'reset'})


@app.route('/stats')
def stats():
    reps = {k: v['count'] for k, v in counter.counters.items()}
    stages = {k: v['stage'] or '---' for k, v in counter.counters.items()}
    feedbacks = {k: v['feedback'] for k, v in counter.counters.items()}
    angles = {k: v['angle'] for k, v in counter.counters.items()}
    elapsed = int(time.time() - session_start)
    return jsonify({
        'reps': reps,
        'stages': stages,
        'feedbacks': feedbacks,
        'angles': angles,
        'fps': fps_counter['fps'],
        'session_time': elapsed,
        'active_exercise': counter.active_exercise,
        'streaming': streaming
    })


if __name__ == '__main__':
    print("\n🏋️  AI Fitness Trainer — Starting server...")
    print("📡  Open your browser at: http://127.0.0.1:5000\n")
    app.run(debug=False, threaded=True, host='0.0.0.0', port=5000)
