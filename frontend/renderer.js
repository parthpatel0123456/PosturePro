let ws = new WebSocket("ws://127.0.0.1:8000/score/ws");

ws.onmessage = (event) => {
  const score = JSON.parse(event.data);

  updateScore("score", score.score, getScoreClass(score.score));
  updateScore("tilt", score.tilt_score, getFieldScoreClass(score.tilt_score));
  updateScore("forward", score.forward_slouch_score, getFieldScoreClass(score.forward_slouch_score));
  updateScore("shoulder", score.shoulder_tilt, getFieldScoreClass(score.shoulder_tilt));
};

function updateScore(id, value, scoreClass) {
  const el = document.getElementById(id);
  el.textContent = value;

  el.classList.remove("glow-good", "glow-mid", "glow-bad");
  el.classList.add(scoreClass);

  el.animate([{ transform: "scale(1.05)" }, { transform: "scale(1)" }], {
    duration: 300,
    easing: "ease-out",
  });
}

function getScoreClass(score) {
  if (score >= 80) return "glow-good";
  if (score >= 50) return "glow-mid";
  return "glow-bad";
}

function getFieldScoreClass(score) {
  if (score >= 0.8) return "glow-good";
  if (score >= 0.5) return "glow-mid";
  return "glow-bad";
}
