let ws = new WebSocket("ws://127.0.0.1:8000/score/ws");

ws.onmessage = (event) => {
  const score = JSON.parse(event.data);
  console.log(score);

  document.getElementById("score").textContent = score.score;
  document.getElementById("tilt").textContent = score.tilt_score;
  document.getElementById("forward").textContent = score.forward_slouch_score;
  document.getElementById("shoulder").textContent = score.shoulder_tilt;
};
