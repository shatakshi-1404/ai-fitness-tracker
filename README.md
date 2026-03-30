# ⚡ AI Fitness Trainer

Real-time AI-powered fitness trainer using Computer Vision — tracks body posture, counts exercise reps, and provides live visual feedback via webcam.

---

## 📁 Folder Structure

```
ai-fitness-trainer/
├── app.py                  # Flask backend — routes, streaming, state
├── requirements.txt        # Python dependencies
├── setup.sh                # Linux/Mac auto-setup
├── setup.bat               # Windows auto-setup
├── README.md
│
├── utils/
│   ├── __init__.py
│   ├── angle_calculator.py # Joint angle math (NumPy)
│   └── pose_detector.py    # MediaPipe pose + ExerciseCounter class
│
├── templates/
│   └── index.html          # Main UI (Jinja2)
│
└── static/
    ├── css/
    │   └── style.css       # Dark athletic UI theme
    └── js/
        └── app.js          # Frontend logic — polling, UI updates
```

---

## 🚀 Quick Start

### 1. Prerequisites
- Python 3.9+
- Webcam
- VS Code (recommended)

### 2. Install

**Mac / Linux:**
```bash
cd ai-fitness-trainer
chmod +x setup.sh
./setup.sh
```

**Windows:**
```cmd
cd ai-fitness-trainer
setup.bat
```

**Manual (any platform):**
```bash
python -m venv venv
source venv/bin/activate       # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Run
```bash
source venv/bin/activate        # activate venv
python app.py
```

Open **http://127.0.0.1:5000** in your browser.

---

## 🎮 Usage

1. Click **START CAMERA** — grant webcam permissions in browser
2. Select an exercise from the left panel (Squats, Push-Ups, Curls, Lunges)
3. Stand/position yourself so your full body is visible
4. Perform the exercise — the app will:
   - Detect body landmarks (green skeleton overlay)
   - Calculate joint angles in real time
   - Detect UP/DOWN stages
   - Count reps automatically
   - Show feedback at the bottom of the feed
5. Monitor stats in the right panel (total reps, calories, rep log)
6. Click **RESET CURRENT** to reset the active exercise, or **RESET ALL** to clear everything

---

## 🏋️ Exercises & Angles

| Exercise     | Joint Tracked         | UP Threshold | DOWN Threshold |
|--------------|-----------------------|-------------|----------------|
| Squats       | Hip – Knee – Ankle    | > 160°      | < 90°          |
| Push-Ups     | Shoulder – Elbow – Wrist | > 160°   | < 70°          |
| Bicep Curls  | Shoulder – Elbow – Wrist | < 40°    | > 150°         |
| Lunges       | Hip – Knee – Ankle    | > 160°      | < 90°          |

---

## 🛠 Tech Stack

| Layer      | Technology                          |
|------------|-------------------------------------|
| Backend    | Python 3, Flask 3.0                 |
| CV Engine  | OpenCV 4.9                          |
| Pose Model | MediaPipe Pose (BlazePose)          |
| Math       | NumPy                               |
| Frontend   | Vanilla HTML/CSS/JS (no frameworks) |
| Streaming  | MJPEG via Flask Response generator  |

---

## 💡 VS Code Tips

1. Install the **Python** extension
2. Select the venv interpreter: `Ctrl+Shift+P → Python: Select Interpreter`
3. Run with `F5` or the terminal: `python app.py`
4. Set breakpoints in `utils/pose_detector.py` to debug angle logic

---

## 🔮 Roadmap / Extensions

- [ ] Voice feedback (pyttsx3 / gTTS)
- [ ] Posture correction alerts (spine angle)
- [ ] Rep tempo analysis
- [ ] Workout history stored in SQLite
- [ ] MERN stack full dashboard
- [ ] Mobile responsive layout
- [ ] Multiple camera support

---

## ⚠️ Troubleshooting

| Issue | Fix |
|-------|-----|
| Camera not found | Check device index in `app.py` — try `cv2.VideoCapture(1)` |
| Slow FPS | Reduce resolution in `app.py` (`CAP_PROP_FRAME_WIDTH 640`) |
| mediapipe install fails | Use Python 3.9–3.11; mediapipe doesn't yet support 3.12+ fully |
| Blank video feed | Allow camera permissions in browser, refresh page |
