export function initDashboard() {
  fetchUserGreeting();
  drawAnalogClock();
}

async function fetchUserGreeting() {
  try {
    const res = await fetch('/api/me');
    const data = await res.json();

    const greeting = `Welcome ${data.firstName} (${data.username})`;
    document.getElementById("userGreeting").textContent = greeting;
  } catch (err) {
    console.error("Failed to fetch user info:", err);
    document.getElementById("userGreeting").textContent = "Welcome!";
  }
}

function drawAnalogClock() {
  const canvas = document.getElementById("analogClock");
  const ctx = canvas.getContext("2d");
  const radius = canvas.height / 2;
  ctx.translate(radius, radius);

  function drawClock() {
    ctx.clearRect(-radius, -radius, canvas.width, canvas.height);
    drawFace(ctx, radius);
    drawTime(ctx, radius);
    updateDigitalDisplay();
  }

  function drawFace(ctx, radius) {
    ctx.beginPath();
    ctx.arc(0, 0, radius - 2, 0, 2 * Math.PI);
    ctx.fillStyle = "#fff";
    ctx.fill();
    ctx.strokeStyle = "#000";
    ctx.lineWidth = 2;
    ctx.stroke();
    ctx.font = radius * 0.15 + "px sans-serif";
    ctx.textBaseline = "middle";
    ctx.textAlign = "center";
    for (let num = 1; num <= 12; num++) {
      let ang = num * Math.PI / 6;
      ctx.rotate(ang);
      ctx.translate(0, -radius * 0.85);
      ctx.rotate(-ang);
      ctx.fillText(num.toString(), 0, 0);
      ctx.rotate(ang);
      ctx.translate(0, radius * 0.85);
      ctx.rotate(-ang);
    }
  }

  function drawTime(ctx, radius) {
    const now = new Date();
    let hour = now.getHours();
    let minute = now.getMinutes();
    let second = now.getSeconds();

    hour %= 12;
    hour = (hour * Math.PI / 6) + (minute * Math.PI / (6 * 60));
    drawHand(ctx, hour, radius * 0.5, radius * 0.07);

    minute = (minute * Math.PI / 30) + (second * Math.PI / (30 * 60));
    drawHand(ctx, minute, radius * 0.8, radius * 0.07);

    second = (second * Math.PI / 30);
    drawHand(ctx, second, radius * 0.9, radius * 0.02);
  }

  function drawHand(ctx, pos, length, width) {
    ctx.beginPath();
    ctx.lineWidth = width;
    ctx.lineCap = "round";
    ctx.moveTo(0, 0);
    ctx.rotate(pos);
    ctx.lineTo(0, -length);
    ctx.stroke();
    ctx.rotate(-pos);
  }

  function updateDigitalDisplay() {
    const now = new Date();
    const options = { hour: 'numeric', minute: '2-digit', hour12: true };
    document.getElementById("digitalTime").textContent = now.toLocaleTimeString('en-US', options);

    const dateOptions = { year: 'numeric', month: 'long', day: 'numeric' };
    const formatted = now.toLocaleDateString('en-US', dateOptions).split(' ');
    document.getElementById("currentDate").innerText = `${formatted[0].toUpperCase()} ${formatted[1]}\n${formatted[2]}`;
  }

  drawClock();
  setInterval(drawClock, 100);
}
