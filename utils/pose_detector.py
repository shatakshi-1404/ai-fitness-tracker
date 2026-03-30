```python
import cv2
import numpy as np
from utils.angle_calculator import calculate_angle

# ✅ MediaPipe Tasks API
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision as mp_vision
from mediapipe.tasks.python.vision import PoseLandmarker, PoseLandmarkerOptions

# ✅ Correct Image import
from mediapipe import Image as MPImage
from mediapipe import ImageFormat


# Landmark index constants
class PoseLandmark:
    LEFT_SHOULDER = 11
    RIGHT_SHOULDER = 12
    LEFT_ELBOW = 13
    RIGHT_ELBOW = 14
    LEFT_WRIST = 15
    RIGHT_WRIST = 16
    LEFT_HIP = 23
    RIGHT_HIP = 24
    LEFT_KNEE = 25
    RIGHT_KNEE = 26
    LEFT_ANKLE = 27
    RIGHT_ANKLE = 28


# Skeleton connections
POSE_CONNECTIONS = [
    (11, 12), (11, 13), (13, 15), (12, 14), (14, 16),
    (11, 23), (12, 24), (23, 24), (23, 25), (24, 26),
    (25, 27), (26, 28)
]


# ---------------- MODEL DOWNLOAD ----------------
def _download_model():
    import os, urllib.request

    model_path = "pose_landmarker.task"

    if not os.path.exists(model_path):
        print("[INFO] Downloading model...")
        url = "https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_lite/float16/latest/pose_landmarker_lite.task"
        urllib.request.urlretrieve(url, model_path)

    return model_path


# ---------------- POSE DETECTOR ----------------
class PoseDetector:
    def __init__(self):
        model_path = _download_model()

        options = PoseLandmarkerOptions(
            base_options=mp_python.BaseOptions(model_asset_path=model_path),
            running_mode=mp_vision.RunningMode.VIDEO,  # ✅ better for real-time
            num_poses=1,
            min_pose_detection_confidence=0.6,
            min_pose_presence_confidence=0.6,
            min_tracking_confidence=0.6,
        )

        self.landmarker = PoseLandmarker.create_from_options(options)

    def process_frame(self, frame):
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        mp_image = MPImage(
            image_format=ImageFormat.SRGB,
            data=rgb
        )

        result = self.landmarker.detect(mp_image)
        return result

    def draw_landmarks(self, frame, result):
        if not result.pose_landmarks:
            return frame

        h, w = frame.shape[:2]
        landmarks = result.pose_landmarks[0]

        # Draw connections
        for (a, b) in POSE_CONNECTIONS:
            lmA = landmarks[a]
            lmB = landmarks[b]

            if lmA.visibility > 0.5 and lmB.visibility > 0.5:
                x1, y1 = int(lmA.x * w), int(lmA.y * h)
                x2, y2 = int(lmB.x * w), int(lmB.y * h)
                cv2.line(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

        # Draw points
        for lm in landmarks:
            if lm.visibility > 0.5:
                cx, cy = int(lm.x * w), int(lm.y * h)
                cv2.circle(frame, (cx, cy), 4, (0, 0, 255), -1)

        return frame

    def release(self):
        self.landmarker.close()


# ---------------- HELPER ----------------
def _get_coord(landmarks, index, w, h):
    lm = landmarks[index]
    return [int(lm.x * w), int(lm.y * h)]


# ---------------- EXERCISE COUNTER ----------------
class ExerciseCounter:
    def __init__(self):
        self.counters = {
            'squat': {'count': 0, 'stage': None, 'angle': 0},
            'pushup': {'count': 0, 'stage': None, 'angle': 0},
        }
        self.active_exercise = 'squat'

    def set_exercise(self, exercise):
        if exercise in self.counters:
            self.active_exercise = exercise

    def process(self, result, frame):
        if not result.pose_landmarks:
            return frame

        landmarks = result.pose_landmarks[0]
        h, w, _ = frame.shape

        if self.active_exercise == 'squat':
            self._process_squat(landmarks, h, w)
        elif self.active_exercise == 'pushup':
            self._process_pushup(landmarks, h, w)

        self._draw_ui(frame)
        return frame

    # ---------------- SQUAT ----------------
    def _process_squat(self, landmarks, h, w):
        hip = _get_coord(landmarks, PoseLandmark.LEFT_HIP, w, h)
        knee = _get_coord(landmarks, PoseLandmark.LEFT_KNEE, w, h)
        ankle = _get_coord(landmarks, PoseLandmark.LEFT_ANKLE, w, h)

        angle = calculate_angle(hip, knee, ankle)
        data = self.counters['squat']
        data['angle'] = angle

        if angle > 160:
            data['stage'] = "UP"
        elif angle < 90 and data['stage'] == "UP":
            data['stage'] = "DOWN"
            data['count'] += 1

    # ---------------- PUSHUP ----------------
    def _process_pushup(self, landmarks, h, w):
        shoulder = _get_coord(landmarks, PoseLandmark.LEFT_SHOULDER, w, h)
        elbow = _get_coord(landmarks, PoseLandmark.LEFT_ELBOW, w, h)
        wrist = _get_coord(landmarks, PoseLandmark.LEFT_WRIST, w, h)

        angle = calculate_angle(shoulder, elbow, wrist)
        data = self.counters['pushup']
        data['angle'] = angle

        if angle > 160:
            data['stage'] = "UP"
        elif angle < 70 and data['stage'] == "UP":
            data['stage'] = "DOWN"
            data['count'] += 1

    # ---------------- UI ----------------
    def _draw_ui(self, frame):
        data = self.counters[self.active_exercise]

        cv2.rectangle(frame, (0, 0), (250, 100), (0, 0, 0), -1)

        cv2.putText(frame, f"{self.active_exercise.upper()}",
                    (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

        cv2.putText(frame, f"REPS: {data['count']}",
                    (10, 70),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

        cv2.putText(frame, f"STAGE: {data['stage']}",
                    (10, 95),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
