/* ── AI Fitness Trainer — Frontend Logic ── */

// ── State ────────────────────────────────────────────
const state = {
  streaming: false,
  activeExercise: 'squat',
  prevCounts: { squat: 0, pushup: 0, curl: 0, lunge: 0 },
  sessionStart: Date.now(),
  repLog: [],
  pollInterval: null,
  timerInterval: null,
};

// Exercise metadata
const EXERCISE_META = {
  squat: {
    name: 'SQUATS',
    guide: {
      title: 'SQUATS',
      steps: [
        'Stand feet shoulder-width apart',
        'Keep back straight, chest up',
        'Lower until knees reach ~90°',
        'Drive through heels to stand',
      ],
      angles: ['↑ UP: angle > 160°', '↓ DOWN: angle < 90°'],
    },
  },
  pushup: {
    name: 'PUSH-UPS',
    guide: {
      title: 'PUSH-UPS',
      steps: [
        'Start in plank position',
        'Keep body in a straight line',
        'Lower chest to near the floor',
        'Push up to full arm extension',
      ],
      angles: ['↑ UP: angle > 160°', '↓ DOWN: angle < 70°'],
    },
  },
  curl: {
    name: 'BICEP CURLS',
    guide: {
      title: 'BICEP CURLS',
      steps: [
        'Stand upright, arm extended',
        'Keep elbow close to your body',
        'Curl the weight up fully',
        'Slowly lower back down',
      ],
      angles: ['↑ UP: angle < 40°', '↓ DOWN: angle > 150°'],
    },
  },
  lunge: {
    name: 'LUNGES',
    guide: {
      title: 'LUNGES',
      steps: [
        'Stand tall, feet together',
        'Step forward with one leg',
        'Lower back knee to near floor',
        'Push back to starting position',
      ],
      angles: ['↑ UP: angle > 160°', '↓ DOWN: angle < 90°'],
    },
  },
};

// ── Stream control ────────────────────────────────────
async function startStream() {
  try {
    const res = await fetch('/start_stream', { method: 'POST' });
    const data = await res.json();
    if (data.status === 'started') {
      state.streaming = true;
      state.sessionStart = Date.now();

      // Show video feed
      const feed = document.getElementById('videoFeed');
      feed.src = '/video_feed?' + Date.now();
      feed.classList.remove('hidden');
      document.getElementById('videoPlaceholder').style.display = 'none';

      // Update nav
      document.getElementById('statusDot').classList.add('live');
      document.getElementById('statusText').textContent = 'LIVE';

      // Buttons
      document.getElementById('startBtn').disabled = true;
      document.getElementById('stopBtn').disabled = false;

      // Start polling stats
      state.pollInterval = setInterval(pollStats, 500);
      state.timerInterval = setInterval(updateTimer, 1000);

      toast('Camera started — let\'s go! 🔥', 'success');
    }
  } catch (e) {
    toast('Could not start camera', 'error');
  }
}

async function stopStream() {
  clearInterval(state.pollInterval);
  clearInterval(state.timerInterval);

  try {
    await fetch('/stop_stream', { method: 'POST' });
  } catch (_) {}

  state.streaming = false;
  const feed = document.getElementById('videoFeed');
  feed.src = '';
  feed.classList.add('hidden');
  document.getElementById('videoPlaceholder').style.display = 'flex';
  document.getElementById('statusDot').classList.remove('live');
  document.getElementById('statusText').textContent = 'OFFLINE';
  document.getElementById('startBtn').disabled = false;
  document.getElementById('stopBtn').disabled = true;
  toast('Session ended', 'info');
}

// ── Exercise selection ────────────────────────────────
function selectExercise(ex, btn) {
  state.activeExercise = ex;

  document.querySelectorAll('.ex-btn').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');

  document.getElementById('videoBadgeText').textContent =
    EXERCISE_META[ex].name + ' MODE';

  updateGuide(ex);

  if (state.streaming) {
    fetch('/set_exercise', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ exercise: ex }),
    });
  }
  toast(`Switched to ${EXERCISE_META[ex].name}`, 'info');
}

function updateGuide(ex) {
  const g = EXERCISE_META[ex].guide;
  document.getElementById('guideTitle').textContent = g.title;
  const ul = document.getElementById('guideSteps');
  ul.innerHTML = '';
  g.steps.forEach(s => {
    const li = document.createElement('li');
    li.textContent = s;
    ul.appendChild(li);
  });
  const angDiv = document.getElementById('guideAngles');
  angDiv.innerHTML = '';
  g.angles.forEach(a => {
    const span = document.createElement('span');
    span.className = 'angle-tip';
    span.textContent = a;
    angDiv.appendChild(span);
  });
}

// ── Reset ─────────────────────────────────────────────
async function resetCurrent() {
  await fetch('/reset_counter', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ exercise: state.activeExercise }),
  });
  toast(`${EXERCISE_META[state.activeExercise].name} reset`, 'info');
}

async function resetAll() {
  await fetch('/reset_counter', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({}),
  });
  state.repLog = [];
  renderHistory();
  toast('All counters reset', 'info');
}

// ── Stats polling ─────────────────────────────────────
async function pollStats() {
  try {
    const res = await fetch('/stats');
    const data = await res.json();
    updateUI(data);
  } catch (_) {}
}

function updateUI(data) {
  const { reps, stages, feedbacks, angles, fps, active_exercise } = data;
  const ex = active_exercise || state.activeExercise;

  // FPS
  document.getElementById('fpsDisplay').textContent = fps || '--';

  // Big counter (active exercise)
  const bigCount = reps[ex] || 0;
  const bigEl = document.getElementById('bigCount');
  if (parseInt(bigEl.textContent) !== bigCount) {
    bigEl.classList.add('pop');
    setTimeout(() => bigEl.classList.remove('pop'), 150);
  }
  bigEl.textContent = bigCount;

  // Stage
  const stageEl = document.getElementById('stageDisplay');
  const stage = stages[ex] || '---';
  stageEl.textContent = stage;
  stageEl.className = 'meta-value stage-badge' + (stage === 'DOWN' ? ' down' : '');

  // Angle
  document.getElementById('angleDisplay').textContent = (angles[ex] || 0) + '°';

  // Feedback
  const fb = feedbacks[ex] || '';
  document.getElementById('feedbackText').textContent = fb;
  const fbBox = document.getElementById('feedbackBox');
  fbBox.className = 'feedback-box' + (fb.includes('!') || fb.includes('✓') ? ' good' : '');

  // Per-exercise counts
  const GOAL = 12;
  for (const e of ['squat', 'pushup', 'curl', 'lunge']) {
    const count = reps[e] || 0;

    // Side panel count
    const el = document.getElementById('count-' + e);
    if (el && parseInt(el.textContent) !== count) {
      el.textContent = count;
      el.classList.add('bump');
      setTimeout(() => el.classList.remove('bump'), 200);
    }

    // Progress bar (goal = 12)
    const pct = Math.min(100, (count / GOAL) * 100);
    const bar = document.getElementById('prog-' + e);
    if (bar) bar.style.width = pct + '%';
    const pnum = document.getElementById('pnum-' + e);
    if (pnum) pnum.textContent = count;

    // Rep log
    if (count > (state.prevCounts[e] || 0)) {
      const newReps = count - (state.prevCounts[e] || 0);
      for (let i = 0; i < newReps; i++) {
        addRepLog(e, count);
      }
      state.prevCounts[e] = count;
    }
  }

  // Session stats
  const totalReps = Object.values(reps).reduce((a, b) => a + b, 0);
  document.getElementById('totalReps').textContent = totalReps;
  const exercisesDone = Object.values(reps).filter(v => v > 0).length;
  document.getElementById('totalExercises').textContent = exercisesDone;
  // Rough calorie estimate: ~0.5 cal per rep
  document.getElementById('calBurn').textContent = Math.round(totalReps * 0.5);
  // Average angle across exercises
  const avgA = Object.values(angles).reduce((a, b) => a + b, 0) / Object.keys(angles).length;
  document.getElementById('avgAngle').textContent = Math.round(avgA) + '°';
}

// ── Rep log ───────────────────────────────────────────
function addRepLog(exercise, count) {
  const now = new Date();
  const time = now.toTimeString().slice(0, 5);
  state.repLog.unshift({ exercise, count, time });
  if (state.repLog.length > 30) state.repLog.pop();
  renderHistory();
}

function renderHistory() {
  const list = document.getElementById('historyList');
  if (state.repLog.length === 0) {
    list.innerHTML = '<p class="history-empty">No reps yet — start moving!</p>';
    return;
  }
  list.innerHTML = state.repLog.map(entry => `
    <div class="history-entry">
      <span class="history-ex">${EXERCISE_META[entry.exercise]?.name || entry.exercise}</span>
      <span class="history-rep">Rep #${entry.count}</span>
      <span class="history-time">${entry.time}</span>
    </div>
  `).join('');
}

// ── Session timer ─────────────────────────────────────
function updateTimer() {
  const elapsed = Math.floor((Date.now() - state.sessionStart) / 1000);
  const mm = String(Math.floor(elapsed / 60)).padStart(2, '0');
  const ss = String(elapsed % 60).padStart(2, '0');
  document.getElementById('sessionTimer').textContent = `${mm}:${ss}`;
}

// ── Toast ─────────────────────────────────────────────
function toast(msg, type = 'info') {
  const el = document.createElement('div');
  el.className = `toast ${type}`;
  el.textContent = msg;
  document.getElementById('toastStack').appendChild(el);
  setTimeout(() => {
    el.style.animation = 'toastOut 0.3s ease forwards';
    setTimeout(() => el.remove(), 300);
  }, 2800);
}

// ── Init ─────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  updateGuide('squat');

  // Handle video load error gracefully
  const feed = document.getElementById('videoFeed');
  feed.addEventListener('error', () => {
    if (state.streaming) {
      setTimeout(() => { feed.src = '/video_feed?' + Date.now(); }, 1000);
    }
  });

  toast('AI Fitness Trainer ready — click START CAMERA', 'info');
});
