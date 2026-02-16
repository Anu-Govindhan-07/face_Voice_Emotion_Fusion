const player = document.getElementById('player');
const overlay = document.getElementById('overlay');
const faceCount = document.getElementById('faceCount');
const speakerCount = document.getElementById('speakerCount');
const summaryList = document.getElementById('summaryList');
const identityList = document.getElementById('identityList');
const statusLabel = document.getElementById('status');
const jobIdInput = document.getElementById('jobIdInput');

let frameTracks = [];
let emotionSamplesByTrack = {};

function findNearestSample(samples = [], currentTime, maxGap = 1.0) {
  if (!samples.length) return null;
  let nearest = null;
  let bestDelta = Number.POSITIVE_INFINITY;
  for (const item of samples) {
    const delta = Math.abs((item.ts ?? 0) - currentTime);
    if (delta < bestDelta) {
      bestDelta = delta;
      nearest = item;
    }
  }
  if (bestDelta > maxGap) return null;
  return nearest;
}

function trackInfoMap(ui) {
  const map = {};
  for (const t of ui.tracks || []) map[t.track_id] = t;
  return map;
}

function applyUiData(ui) {
  faceCount.textContent = `Face Tracks: ${ui.summary?.face_tracks || 0}`;
  speakerCount.textContent = `Speaker Segments: ${ui.summary?.speaker_segments || 0}`;
  renderSummary(ui.summary || {});
  renderIdentities(ui.tracks || []);

  const detailMap = trackInfoMap(ui);
  emotionSamplesByTrack = ui.emotion_samples || {};

  frameTracks = (ui.face_tracks || []).map((ft) => {
    const detail = detailMap[ft.track_id] || {};
    return {
      ...ft,
      resolved_name: detail.resolved_name || 'Unknown',
      fallback_emotion: detail.current_emotion || { emotion: 'neutral', confidence: 0 },
    };
  });

  statusLabel.textContent = 'Analysis loaded successfully.';
  drawBoxes();
}

function renderSummary(summary) {
  summaryList.innerHTML = '';
  const items = [
    ['Face tracks', summary.face_tracks || 0],
    ['Speaker segments', summary.speaker_segments || 0],
    ['Identities matched', summary.identities_matched || 0],
    ['Emotion tracks', summary.emotion_tracks || 0],
    ['Associations', summary.associations || 0],
  ];
  for (const [label, val] of items) {
    const li = document.createElement('li');
    li.className = 'metric';
    li.innerHTML = `<span>${label}</span><b>${val}</b>`;
    summaryList.appendChild(li);
  }
}

function renderIdentities(tracks = []) {
  identityList.innerHTML = '';
  tracks.forEach((t) => {
    const li = document.createElement('li');
    li.textContent = `${t.track_id} • ${t.resolved_name || 'Unknown'} • ${t.current_emotion?.emotion || 'neutral'} (${Math.round((t.current_emotion?.confidence || 0) * 100)}%)`;
    identityList.appendChild(li);
  });
}

function currentBoxes(currentTime) {
  return frameTracks
    .map((track) => {
      const nearestBox = findNearestSample(track.bboxes || [], currentTime, 1.0);
      if (!nearestBox) return null;

      const emotionTimeline = emotionSamplesByTrack[track.track_id] || [];
      const emotionAtTime = findNearestSample(emotionTimeline, currentTime, 1.0) || track.fallback_emotion;
      const emotion = emotionAtTime?.emotion || 'neutral';
      const confidence = Math.round((emotionAtTime?.confidence || 0) * 100);
      const label = `${track.resolved_name} ${emotion} (${confidence}%)`;
      return { bbox: nearestBox.bbox, label };
    })
    .filter(Boolean);
}

function drawBoxes() {
  const boxes = currentBoxes(player.currentTime || 0);
  overlay.innerHTML = '';
  const vw = player.clientWidth || 1;
  const vh = player.clientHeight || 1;
  const sourceW = player.videoWidth || 1280;
  const sourceH = player.videoHeight || 720;

  boxes.forEach(({ bbox, label }) => {
    const [x1, y1, x2, y2] = bbox;
    const div = document.createElement('div');
    div.className = 'box';
    div.style.left = `${(x1 / sourceW) * vw}px`;
    div.style.top = `${(y1 / sourceH) * vh}px`;
    div.style.width = `${((x2 - x1) / sourceW) * vw}px`;
    div.style.height = `${((y2 - y1) / sourceH) * vh}px`;
    div.textContent = label;
    overlay.appendChild(div);
  });
}

async function fetchUiByJobId(jobId) {
  const url = `/data/jobs/${encodeURIComponent(jobId)}/outputs/ui.json`;
  const res = await fetch(url);
  if (!res.ok) throw new Error(`Could not load ${url} (HTTP ${res.status})`);
  return res.json();
}

async function loadUiJsonFile(file) {
  const text = await file.text();
  applyUiData(JSON.parse(text));
}

player.addEventListener('timeupdate', drawBoxes);
player.addEventListener('loadedmetadata', drawBoxes);
window.addEventListener('resize', drawBoxes);

document.getElementById('analyzeBtn').addEventListener('click', async () => {
  const jobId = jobIdInput.value.trim();
  if (!jobId) {
    statusLabel.textContent = 'Enter a job_id first (example: job_001).';
    return;
  }
  statusLabel.textContent = `Analyzing using job_id=${jobId} ...`;
  try {
    const ui = await fetchUiByJobId(jobId);
    applyUiData(ui);
  } catch (err) {
    statusLabel.textContent = `${err}. Run: python -m src.main --video <path> --job_id ${jobId}`;
  }
});

document.getElementById('loadJsonBtn').addEventListener('click', () => {
  const fileInput = document.createElement('input');
  fileInput.type = 'file';
  fileInput.accept = '.json';
  fileInput.onchange = async () => {
    if (!fileInput.files?.[0]) return;
    await loadUiJsonFile(fileInput.files[0]);
  };
  fileInput.click();
});

document.getElementById('videoFile').addEventListener('change', (e) => {
  const file = e.target.files?.[0];
  if (!file) return;
  player.src = URL.createObjectURL(file);
  statusLabel.textContent = `Video loaded: ${file.name}`;
});

(async function bootstrapFromQuery() {
  const params = new URLSearchParams(window.location.search);
  const uiUrl = params.get('ui');
  const jobId = params.get('job_id');
  if (jobId && !jobIdInput.value) jobIdInput.value = jobId;

  try {
    if (uiUrl) {
      const res = await fetch(uiUrl);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      applyUiData(await res.json());
    } else if (jobId) {
      applyUiData(await fetchUiByJobId(jobId));
    }
  } catch (e) {
    statusLabel.textContent = `Auto-load failed: ${e}`;
  }
})();
