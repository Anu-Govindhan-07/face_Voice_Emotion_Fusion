const player = document.getElementById('player');
const overlay = document.getElementById('overlay');
const faceCount = document.getElementById('faceCount');
const speakerCount = document.getElementById('speakerCount');
const summaryList = document.getElementById('summaryList');
const identityList = document.getElementById('identityList');
const statusLabel = document.getElementById('status');

let frameTracks = [];

function applyUiData(ui) {
  faceCount.textContent = `Face Tracks: ${ui.summary?.face_tracks || 0}`;
  speakerCount.textContent = `Speaker Segments: ${ui.summary?.speaker_segments || 0}`;
  renderSummary(ui.summary || {});
  renderIdentities(ui.tracks || []);

  frameTracks = (ui.face_tracks || []).map((ft) => {
    const detail = (ui.tracks || []).find((t) => t.track_id === ft.track_id);
    return { ...ft, label: `${detail?.resolved_name || "Unknown"} • ${detail?.current_emotion?.emotion || ""}` };
  });

  statusLabel.textContent = "Loaded ui.json successfully.";
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
      const sample = (track.bboxes || []).find((f) => Math.abs(f.ts - currentTime) <= 0.25);
      return sample ? { track_id: track.track_id, bbox: sample.bbox, label: track.label || track.track_id } : null;
    })
    .filter(Boolean);
}

function drawBoxes() {
  const boxes = currentBoxes(player.currentTime);
  overlay.innerHTML = '';
  const vw = player.clientWidth;
  const vh = player.clientHeight;
  boxes.forEach(({ bbox, label }) => {
    const [x1, y1, x2, y2] = bbox;
    const div = document.createElement('div');
    div.className = 'box';
    div.style.left = `${(x1 / 1280) * vw}px`;
    div.style.top = `${(y1 / 720) * vh}px`;
    div.style.width = `${((x2 - x1) / 1280) * vw}px`;
    div.style.height = `${((y2 - y1) / 720) * vh}px`;
    div.textContent = label;
    overlay.appendChild(div);
  });
}

player.addEventListener('timeupdate', drawBoxes);
window.addEventListener('resize', drawBoxes);

async function loadUiJson(file) {
  const text = await file.text();
  const ui = JSON.parse(text);
  applyUiData(ui);
}

document.getElementById('analyzeBtn').addEventListener('click', async () => {
  const fileInput = document.createElement('input');
  fileInput.type = 'file';
  fileInput.accept = '.json';
  fileInput.onchange = async () => {
    if (!fileInput.files?.[0]) return;
    await loadUiJson(fileInput.files[0]);
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
  const uiUrl = params.get("ui");
  if (!uiUrl) return;
  try {
    const res = await fetch(uiUrl);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    applyUiData(data);
  } catch (e) {
    statusLabel.textContent = `Failed to load ${uiUrl}: ${e}`;
  }
})();
