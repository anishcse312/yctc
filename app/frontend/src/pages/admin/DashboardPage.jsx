import React, { useEffect, useMemo, useRef, useState } from "react";

const AnalogClock = ({ now }) => {
  const canvasRef = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    const radius = canvas.height / 2;

    const drawHand = (pos, length, width) => {
      ctx.save();
      ctx.beginPath();
      ctx.lineWidth = width;
      ctx.lineCap = "round";
      ctx.rotate(pos);
      ctx.moveTo(0, 0);
      ctx.lineTo(0, -length);
      ctx.stroke();
      ctx.restore();
    };

    ctx.setTransform(1, 0, 0, 1, 0, 0);
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.translate(radius, radius);

    ctx.beginPath();
    ctx.arc(0, 0, radius - 2, 0, 2 * Math.PI);
    ctx.fillStyle = "#ffffff";
    ctx.fill();
    ctx.strokeStyle = "#0c2040";
    ctx.lineWidth = 2;
    ctx.stroke();

    ctx.font = `${radius * 0.15}px Space Grotesk`;
    ctx.textBaseline = "middle";
    ctx.textAlign = "center";
    ctx.fillStyle = "#0c2040";

    for (let num = 1; num <= 12; num += 1) {
      const ang = (num * Math.PI) / 6;
      ctx.rotate(ang);
      ctx.translate(0, -radius * 0.82);
      ctx.rotate(-ang);
      ctx.fillText(num.toString(), 0, 0);
      ctx.rotate(ang);
      ctx.translate(0, radius * 0.82);
      ctx.rotate(-ang);
    }

    const hour = now.getHours() % 12;
    const minute = now.getMinutes();
    const second = now.getSeconds();

    const hourPos = (hour * Math.PI) / 6 + (minute * Math.PI) / (6 * 60);
    drawHand(hourPos, radius * 0.5, radius * 0.07);

    const minutePos = (minute * Math.PI) / 30 + (second * Math.PI) / (30 * 60);
    drawHand(minutePos, radius * 0.78, radius * 0.05);

    const secondPos = (second * Math.PI) / 30;
    ctx.strokeStyle = "#1f7ed6";
    drawHand(secondPos, radius * 0.85, radius * 0.02);
  }, [now]);

  return <canvas ref={canvasRef} width="200" height="200"></canvas>;
};

const DashboardPage = () => {
  const [greeting, setGreeting] = useState("Loading user...");
  const [now, setNow] = useState(new Date());

  useEffect(() => {
    const timer = setInterval(() => setNow(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  useEffect(() => {
    const fetchUser = async () => {
      try {
        const res = await fetch("/api/me", { credentials: "include" });
        const data = await res.json();
        setGreeting(`Welcome ${data.firstName} (${data.username})`);
      } catch (err) {
        setGreeting("Welcome!");
      }
    };
    fetchUser();
  }, []);

  const timeString = useMemo(
    () =>
      now.toLocaleTimeString("en-US", {
        hour: "numeric",
        minute: "2-digit",
        hour12: true,
      }),
    [now]
  );

  const dateParts = useMemo(
    () =>
      now
        .toLocaleDateString("en-US", {
          month: "long",
          day: "numeric",
          year: "numeric",
        })
        .replace(",", "")
        .split(" "),
    [now]
  );

  return (
    <div className="main-content main-content--search">
      <div className="panel panel--dark fade-up">
        <h2 style={{ margin: 0 }}>{greeting}</h2>
      </div>
      <div className="dashboard-grid">
        <div className="panel clock-card fade-up delay-1">
          <AnalogClock now={now} />
          <div className="clock-readout">
            <div>{timeString}</div>
            <div style={{ whiteSpace: "pre-line" }}>
              {dateParts[0].toUpperCase()} {dateParts[1]}
              <br />
              {dateParts[2]}
            </div>
          </div>
        </div>
        <div className="panel fade-up delay-2">
          <iframe
            className="calendar-frame"
            src="https://calendar.google.com/calendar/embed?src=yctc.gipl%40gmail.com&ctz=Asia%2FKolkata"
            title="YCTC Calendar"
          ></iframe>
        </div>
      </div>
    </div>
  );
};

export default DashboardPage;
