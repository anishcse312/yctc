import React, { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { BrowserRouter, Route, Routes } from "react-router-dom";

const getCookie = (name) => {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(";").shift();
  return null;
};

const setCookie = (name, value, days = 7) => {
  const expires = new Date(Date.now() + days * 86400000).toUTCString();
  document.cookie = `${name}=${encodeURIComponent(value)}; expires=${expires}; path=/`;
};

const useHashView = (defaultView) => {
  const getView = () => (window.location.hash ? window.location.hash.slice(1) : defaultView);
  const [view, setView] = useState(getView);

  useEffect(() => {
    const handler = () => setView(getView());
    window.addEventListener("hashchange", handler);
    return () => window.removeEventListener("hashchange", handler);
  }, []);

  const navigate = (nextView) => {
    if (nextView === view) return;
    window.location.hash = nextView;
  };

  return [view, navigate];
};

const PageShell = ({ children, className = "" }) => (
  <div className={`page ${className}`}>{children}</div>
);

const AuthShell = ({ title, subtitle, children, footer }) => (
  <PageShell>
    <div className="page__content" style={{ maxWidth: "520px" }}>
      <div className="auth-shell card-light fade-up">
        <h2>{title}</h2>
        <p>{subtitle}</p>
        {children}
        {footer ? <div className="auth-links">{footer}</div> : null}
      </div>
    </div>
  </PageShell>
);

const HomePage = () => {
  const hasAuth = Boolean(getCookie("auth_token"));

  return (
    <PageShell className="page--home">
      <div className="page__content">
        <div className="hero">
          <div className="hero__panel glass-card fade-up">
            <p className="sidebar__brand">YCTC.CO.IN</p>
            <h1 className="hero__title">Welcome to the YCTC admin hub.</h1>
            <p className="hero__subtitle">
              Launch the student or admin portals to manage sessions, track records,
              and keep every update flowing across the campus in a single workspace.
            </p>
            <div className="hero__actions">
              <button
                className="btn btn--primary"
                onClick={() => (window.location.href = "/student-portal")}
              >
                Student Portal
              </button>
              <button
                className="btn btn--ghost"
                onClick={() =>
                  (window.location.href = hasAuth ? "/admin/dashboard" : "/admin-login")}
              >
                Admin Portal
              </button>
            </div>
            <div className="stat-grid">
              <div className="stat floating">
                <span>Realtime status</span>
                <strong>Always on</strong>
              </div>
              <div className="stat floating">
                <span>Secure access</span>
                <strong>Token-based</strong>
              </div>
              <div className="stat floating">
                <span>Session tools</span>
                <strong>One dashboard</strong>
              </div>
            </div>
          </div>
          <div className="hero__panel glass-card fade-up delay-2">
            <h2 className="hero__title">Blueprints for busy admins.</h2>
            <p className="hero__subtitle">
              A refreshed layout highlights quick actions, live session controls, and
              an eye-on-time dashboard so the team never loses momentum.
            </p>
            <div className="stat-grid">
              <div className="stat">
                <span>Search range</span>
                <strong>Global</strong>
              </div>
              <div className="stat">
                <span>Branch view</span>
                <strong>Personalized</strong>
              </div>
              <div className="stat">
                <span>Updates</span>
                <strong>Instant</strong>
              </div>
            </div>
          </div>
        </div>
      </div>
    </PageShell>
  );
};

const AdminLoginPage = () => {
  const [form, setForm] = useState({ username: "", password: "" });
  const [status, setStatus] = useState({ loading: false, error: "" });

  const handleSubmit = async (event) => {
    event.preventDefault();
    setStatus({ loading: true, error: "" });
    try {
      const response = await fetch("/admin-login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(form),
        credentials: "include",
      });
      if (response.ok) {
        window.location.href = "/admin/dashboard";
        return;
      }
      const text = await response.text();
      setStatus({ loading: false, error: text || "Login failed." });
    } catch (err) {
      setStatus({ loading: false, error: "Network error. Try again." });
    }
  };

  return (
    <AuthShell
      title="Admin Login"
      subtitle="Secure access for staff. Enter your credentials to continue."
      footer={
        <>
          <a href="/admin-register">Need an account? Register</a>
          <a href="/forgot">Forgot username or password?</a>
        </>
      }
    >
      <form className="form-row" onSubmit={handleSubmit}>
        <label>
          Username
          <input
            className="input"
            type="text"
            value={form.username}
            required
            onChange={(event) => setForm({ ...form, username: event.target.value })}
          />
        </label>
        <label>
          Password
          <input
            className="input"
            type="password"
            value={form.password}
            required
            onChange={(event) => setForm({ ...form, password: event.target.value })}
          />
        </label>
        <button className="btn btn--primary" type="submit" disabled={status.loading}>
          {status.loading ? "Signing in..." : "Login"}
        </button>
        {status.error ? <div className="helper-text">{status.error}</div> : null}
      </form>
    </AuthShell>
  );
};

const AdminRegisterPage = () => {
  const [form, setForm] = useState({
    employee_id: "",
    username: "",
    password: "",
    confirm_password: "",
  });
  const [status, setStatus] = useState({ loading: false, error: "" });

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (!/^\d{6}$/.test(form.employee_id)) {
      setStatus({ loading: false, error: "Employee ID must be 6 digits." });
      return;
    }
    if (form.password !== form.confirm_password) {
      setStatus({ loading: false, error: "Passwords do not match." });
      return;
    }
    setStatus({ loading: true, error: "" });
    try {
      const formData = new FormData();
      Object.entries(form).forEach(([key, value]) => {
        formData.append(key, value);
      });
      const response = await fetch("/admin-register", {
        method: "POST",
        body: formData,
      });
      if (response.ok) {
        alert("Registration successful. Redirecting to login...");
        window.location.href = "/admin-login";
        return;
      }
      const text = await response.text();
      setStatus({ loading: false, error: text || "Registration failed." });
    } catch (err) {
      setStatus({ loading: false, error: "Network error. Try again." });
    }
  };

  return (
    <AuthShell
      title="Create Admin Account"
      subtitle="Register with your employee ID to access the dashboard."
      footer={<a href="/admin-login">Back to login</a>}
    >
      <form className="form-row" onSubmit={handleSubmit}>
        <label>
          Employee ID (6 digits)
          <input
            className="input"
            type="text"
            inputMode="numeric"
            maxLength="6"
            value={form.employee_id}
            required
            onChange={(event) =>
              setForm({
                ...form,
                employee_id: event.target.value.replace(/\D/g, "").slice(0, 6),
              })
            }
          />
        </label>
        <label>
          Username
          <input
            className="input"
            type="text"
            value={form.username}
            required
            onChange={(event) => setForm({ ...form, username: event.target.value })}
          />
        </label>
        <label>
          Password
          <input
            className="input"
            type="password"
            value={form.password}
            required
            onChange={(event) => setForm({ ...form, password: event.target.value })}
          />
        </label>
        <label>
          Confirm Password
          <input
            className="input"
            type="password"
            value={form.confirm_password}
            required
            onChange={(event) =>
              setForm({ ...form, confirm_password: event.target.value })
            }
          />
        </label>
        <button className="btn btn--primary" type="submit" disabled={status.loading}>
          {status.loading ? "Creating account..." : "Register"}
        </button>
        {status.error ? <div className="helper-text">{status.error}</div> : null}
      </form>
    </AuthShell>
  );
};

const ForgotPage = () => {
  const [form, setForm] = useState({ employeeId: "", lastName: "" });
  const [status, setStatus] = useState({ loading: false, error: "" });

  const handleSubmit = async (event) => {
    event.preventDefault();
    setStatus({ loading: true, error: "" });
    try {
      const response = await fetch("/forgot", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(form),
        credentials: "include",
      });
      if (response.ok) {
        window.location.href = "/otp";
        return;
      }
      const data = await response.json();
      setStatus({ loading: false, error: data.message || "Request failed." });
    } catch (err) {
      setStatus({ loading: false, error: "Network error. Try again." });
    }
  };

  return (
    <AuthShell
      title="Recover Access"
      subtitle="Confirm your details and we will verify your OTP."
      footer={<a href="/admin-login">Back to login</a>}
    >
      <form className="form-row" onSubmit={handleSubmit}>
        <label>
          Employee ID
          <input
            className="input"
            type="text"
            value={form.employeeId}
            required
            onChange={(event) => setForm({ ...form, employeeId: event.target.value })}
          />
        </label>
        <label>
          Last Name
          <input
            className="input"
            type="text"
            value={form.lastName}
            required
            onChange={(event) => setForm({ ...form, lastName: event.target.value })}
          />
        </label>
        <button className="btn btn--primary" type="submit" disabled={status.loading}>
          {status.loading ? "Sending..." : "Continue"}
        </button>
        {status.error ? <div className="helper-text">{status.error}</div> : null}
      </form>
    </AuthShell>
  );
};

const OtpPage = () => {
  const inputsRef = useRef([]);
  const [status, setStatus] = useState({ loading: false, error: "" });

  const handleChange = (index, event) => {
    const value = event.target.value.replace(/\D/g, "").slice(0, 1);
    event.target.value = value;
    if (value && inputsRef.current[index + 1]) {
      inputsRef.current[index + 1].focus();
    }
  };

  const handleKeyDown = (index, event) => {
    if (event.key === "Backspace" && !event.target.value && inputsRef.current[index - 1]) {
      inputsRef.current[index - 1].focus();
    }
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    const otp = inputsRef.current.map((input) => input.value).join("");
    if (otp.length !== 6) {
      setStatus({ loading: false, error: "Please enter all 6 digits." });
      return;
    }
    setStatus({ loading: true, error: "" });
    try {
      const response = await fetch("/otp", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ otp }),
        credentials: "include",
      });
      if (response.ok) {
        window.location.href = "/set-new-password";
        return;
      }
      const data = await response.json();
      setStatus({ loading: false, error: data.message || "OTP failed." });
    } catch (err) {
      setStatus({ loading: false, error: "Network error. Try again." });
    }
  };

  return (
    <AuthShell
      title="OTP Verification"
      subtitle="Enter the six-digit code sent to you."
      footer={<a href="/forgot">Back</a>}
    >
      <form className="form-row" onSubmit={handleSubmit}>
        <div className="otp-grid">
          {Array.from({ length: 6 }).map((_, index) => (
            <input
              key={index}
              className="input"
              type="text"
              inputMode="numeric"
              ref={(el) => (inputsRef.current[index] = el)}
              onInput={(event) => handleChange(index, event)}
              onKeyDown={(event) => handleKeyDown(index, event)}
              required
            />
          ))}
        </div>
        <button className="btn btn--primary" type="submit" disabled={status.loading}>
          {status.loading ? "Verifying..." : "Verify"}
        </button>
        {status.error ? <div className="helper-text">{status.error}</div> : null}
      </form>
    </AuthShell>
  );
};

const SetNewPasswordPage = () => {
  const [form, setForm] = useState({ newPassword: "", confirmPassword: "" });
  const [status, setStatus] = useState({ loading: false, error: "" });

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (form.newPassword !== form.confirmPassword) {
      setStatus({ loading: false, error: "Passwords do not match." });
      return;
    }
    setStatus({ loading: true, error: "" });
    try {
      const response = await fetch("/set-new-password", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ newPassword: form.newPassword }),
        credentials: "include",
      });
      if (response.ok) {
        window.location.href = "/admin-login";
        return;
      }
      const data = await response.json();
      setStatus({ loading: false, error: data.message || "Failed to reset password." });
    } catch (err) {
      setStatus({ loading: false, error: "Network error. Try again." });
    }
  };

  return (
    <AuthShell
      title="Set New Password"
      subtitle="Choose a strong password you will remember."
    >
      <form className="form-row" onSubmit={handleSubmit}>
        <label>
          New Password
          <input
            className="input"
            type="password"
            value={form.newPassword}
            required
            onChange={(event) => setForm({ ...form, newPassword: event.target.value })}
          />
        </label>
        <label>
          Confirm Password
          <input
            className="input"
            type="password"
            value={form.confirmPassword}
            required
            onChange={(event) =>
              setForm({ ...form, confirmPassword: event.target.value })
            }
          />
        </label>
        <button className="btn btn--primary" type="submit" disabled={status.loading}>
          {status.loading ? "Updating..." : "Submit"}
        </button>
        {status.error ? <div className="helper-text">{status.error}</div> : null}
      </form>
    </AuthShell>
  );
};

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

const DashboardView = () => {
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
    <div className="main-content">
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

const SearchAllStudentsView = () => {
  const [regNumber, setRegNumber] = useState("");
  const [studentName, setStudentName] = useState("");
  const [message, setMessage] = useState("");
  const [resultsHtml, setResultsHtml] = useState("");

  const runSearch = useCallback(async ({ reg, name }) => {
    let payload = {};
    let endpoint = "";

    if (reg) {
      payload = { registrationNumber: `YS-N24/${reg}` };
      endpoint = "/search/by-reg";
    } else if (name) {
      payload = { name };
      endpoint = "/search/by-name";
    }

    try {
      const response = await fetch(endpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      const html = await response.text();
      if (!response.ok) {
        setMessage("Student not found or error occurred.");
        return;
      }
      setResultsHtml(html);
    } catch (err) {
      setMessage("An error occurred while fetching data.");
    }
  }, []);

  const handleSubmit = async (event) => {
    event.preventDefault();
    setMessage("");
    setResultsHtml("");

    const trimmedReg = regNumber.trim();
    const trimmedName = studentName.trim();

    if ((trimmedReg && trimmedName) || (!trimmedReg && !trimmedName)) {
      setMessage("Please enter either a registration number or a student name, not both.");
      return;
    }

    if (trimmedReg) {
      await runSearch({ reg: trimmedReg });
    } else {
      await runSearch({ name: trimmedName });
    }
  };

  const handleQuickSelect = useCallback(
    async (fullReg) => {
      const reg = fullReg.includes("/") ? fullReg.split("/")[1] : fullReg;
      setRegNumber(reg);
      setStudentName("");
      setMessage("");
      setResultsHtml("");
      await runSearch({ reg });
    },
    [runSearch]
  );

  useEffect(() => {
    window.postRegNo = handleQuickSelect;
    return () => {
      if (window.postRegNo === handleQuickSelect) {
        delete window.postRegNo;
      }
    };
  }, [handleQuickSelect]);

  return (
    <div className="main-content">
      <div className="panel search-card fade-up">
        <h2>Search All Students</h2>
        <form className="form-row" onSubmit={handleSubmit}>
          <label>
            Registration Number
            <div style={{ display: "flex", gap: "8px", alignItems: "center" }}>
              <span>YS-N24/</span>
              <input
                className="input"
                type="text"
                placeholder="Enter Registration Number"
                value={regNumber}
                onChange={(event) => setRegNumber(event.target.value)}
              />
            </div>
          </label>
          <label>
            Or Student Name
            <input
              className="input"
              type="text"
              placeholder="Enter Student Name"
              value={studentName}
              onChange={(event) => setStudentName(event.target.value)}
            />
          </label>
          <button className="btn btn--primary" type="submit">
            Search
          </button>
        </form>
        <div className="search-results">
          {message ? (
            <div>{message}</div>
          ) : resultsHtml ? (
            <div dangerouslySetInnerHTML={{ __html: resultsHtml }} />
          ) : (
            <div>Results appear here.</div>
          )}
        </div>
      </div>
    </div>
  );
};

const SettingsView = () => {
  const [profile, setProfile] = useState({
    username: "",
    email: "",
    employeeId: "",
    profilePicture: "",
  });
  const [passwords, setPasswords] = useState({
    currentPassword: "",
    newPassword: "",
    confirmPassword: "",
  });
  const [status, setStatus] = useState({ loading: false, message: "" });

  useEffect(() => {
    const loadProfile = async () => {
      try {
        const res = await fetch("/api/me", { credentials: "include" });
        const data = await res.json();
        setProfile({
          username: data.username || "",
          email: data.email || "",
          employeeId: data.employeeId || "",
          profilePicture: data.profilePicture || "/static/default-profile.png",
        });
      } catch (err) {
        setStatus({ loading: false, message: "Could not load user data." });
      }
    };
    loadProfile();
  }, []);

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (!passwords.currentPassword) {
      setStatus({ loading: false, message: "Current password is required." });
      return;
    }
    if (passwords.newPassword && passwords.newPassword !== passwords.confirmPassword) {
      setStatus({ loading: false, message: "New password mismatch." });
      return;
    }
    setStatus({ loading: true, message: "" });
    try {
      const payload = {
        username: profile.username,
        currentPassword: passwords.currentPassword,
        newPassword: passwords.newPassword || undefined,
      };
      const response = await fetch("/update-profile", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify(payload),
      });
      const result = await response.json();
      setStatus({ loading: false, message: result.message || "Update complete." });
    } catch (err) {
      setStatus({ loading: false, message: "Update failed." });
    }
  };

  const handleFileChange = async (event) => {
    const file = event.target.files[0];
    if (!file) return;
    const formData = new FormData();
    formData.append("profilePicture", file);
    try {
      const res = await fetch("/update-profile-picture", {
        method: "POST",
        body: formData,
        credentials: "include",
      });
      const result = await res.json();
      setStatus({ loading: false, message: result.message || "Profile picture updated." });
      if (result.newUrl) {
        setProfile((prev) => ({ ...prev, profilePicture: result.newUrl }));
      }
    } catch (err) {
      setStatus({ loading: false, message: "Upload failed." });
    }
  };

  return (
    <div className="main-content">
      <div className="panel profile-card fade-up">
        <div className="profile-header">
          <img className="profile-avatar" src={profile.profilePicture} alt="Profile" />
          <label className="upload-btn">
            Upload photo
            <input type="file" hidden accept="image/*" onChange={handleFileChange} />
          </label>
        </div>
        <form className="form-row" onSubmit={handleSubmit}>
          <label>
            Username
            <input
              className="input"
              type="text"
              value={profile.username}
              onChange={(event) => setProfile({ ...profile, username: event.target.value })}
            />
          </label>
          <label>
            Current Password
            <input
              className="input"
              type="password"
              value={passwords.currentPassword}
              onChange={(event) =>
                setPasswords({ ...passwords, currentPassword: event.target.value })
              }
            />
          </label>
          <label>
            New Password
            <input
              className="input"
              type="password"
              value={passwords.newPassword}
              onChange={(event) =>
                setPasswords({ ...passwords, newPassword: event.target.value })
              }
            />
          </label>
          <label>
            Confirm Password
            <input
              className="input"
              type="password"
              value={passwords.confirmPassword}
              onChange={(event) =>
                setPasswords({ ...passwords, confirmPassword: event.target.value })
              }
            />
          </label>
          <label>
            Email
            <input className="input" type="email" value={profile.email} disabled />
          </label>
          <label>
            Employee ID
            <input className="input" type="text" value={profile.employeeId} disabled />
          </label>
          <button className="btn btn--primary" type="submit" disabled={status.loading}>
            {status.loading ? "Updating..." : "Update Profile"}
          </button>
          {status.message ? <div className="helper-text">{status.message}</div> : null}
        </form>
      </div>
    </div>
  );
};

const StudentLateralAdmissionView = () => (
  <div className="main-content">
    <div className="panel fade-up">
      <h2>Student Lateral Admission</h2>
      <p>This section is ready for your admission workflow.</p>
    </div>
  </div>
);

const DashboardShell = () => {
  const [view, navigate] = useHashView("dashboard");
  const [studentsOpen, setStudentsOpen] = useState(
    view === "searchAllStudents" || view === "studentLateralAdmission"
  );
  const [sessions, setSessions] = useState([]);
  const [sessionValue, setSessionValue] = useState("");
  const [branchOptions, setBranchOptions] = useState([]);
  const [branchValue, setBranchValue] = useState("");
  const [branchLabel, setBranchLabel] = useState("Loading...");

  useEffect(() => {
    setStudentsOpen(view === "searchAllStudents" || view === "studentLateralAdmission");
  }, [view]);

  useEffect(() => {
    const loadSessions = async () => {
      try {
        const res = await fetch("/api/sessions", { credentials: "include" });
        const data = await res.json();
        setSessions(data || []);
        const cookieValue = getCookie("session");
        const initial =
          cookieValue && data.find(([sessionNum]) => String(sessionNum) === cookieValue)
            ? cookieValue
            : data.length
              ? String(data[0][0])
              : "";
        if (initial) {
          setSessionValue(initial);
          setCookie("session", initial);
        }
      } catch (err) {
        setSessions([]);
      }
    };
    loadSessions();
  }, []);

  useEffect(() => {
    const loadBranch = async () => {
      try {
        const res = await fetch("/api/my-branch", { credentials: "include" });
        const data = await res.json();
        if (Array.isArray(data.branch)) {
          setBranchOptions(data.branch);
          const cookieValue = getCookie("branch");
          const initial = data.branch.includes(cookieValue) ? cookieValue : data.branch[0];
          setBranchValue(initial);
          if (initial) setCookie("branch", initial);
        } else {
          setBranchLabel(data.branch || "Unknown");
          if (data.branch) setCookie("branch", data.branch);
        }
      } catch (err) {
        setBranchLabel("Unknown");
      }
    };
    loadBranch();
  }, []);

  const handleLogout = async () => {
    try {
      const res = await fetch("/logout", { method: "POST", credentials: "include" });
      const data = await res.json();
      if (res.status === 200) {
        window.location.href = "/";
      } else {
        alert(data.message || "Logout failed");
      }
    } catch (err) {
      alert("Network error while logging out.");
    }
  };

  const renderView = () => {
    if (view === "searchAllStudents") return <SearchAllStudentsView />;
    if (view === "settings") return <SettingsView />;
    if (view === "studentLateralAdmission") return <StudentLateralAdmissionView />;
    return <DashboardView />;
  };

  return (
    <PageShell className="page--dashboard">
      <div className="dash-shell">
        <aside className="sidebar">
          <div>
            <div className="sidebar__brand">YCTC Admin</div>
            <div style={{ fontSize: "20px", fontWeight: 700, marginTop: "8px" }}>
              Command Center
            </div>
          </div>
          <div className="nav-group">
            <button
              className={`nav-link ${view === "dashboard" ? "active" : ""}`}
              onClick={() => navigate("dashboard")}
            >
              <i className="fa-solid fa-layer-group"></i>
              Dashboard
            </button>
            <button className="nav-button" onClick={() => setStudentsOpen(!studentsOpen)}>
              <i className="fa-solid fa-graduation-cap"></i>
              Students
              <i
                className="fa-solid fa-chevron-right"
                style={{
                  marginLeft: "auto",
                  transform: studentsOpen ? "rotate(90deg)" : "rotate(0deg)",
                  transition: "transform 0.2s ease",
                }}
              ></i>
            </button>
            {studentsOpen ? (
              <div className="nav-sub">
                <button
                  className={`nav-link ${view === "searchAllStudents" ? "active" : ""}`}
                  onClick={() => navigate("searchAllStudents")}
                >
                  Search All Students
                </button>
                <button
                  className={`nav-link ${
                    view === "studentLateralAdmission" ? "active" : ""
                  }`}
                  onClick={() => navigate("studentLateralAdmission")}
                >
                  Student Lateral Admission
                </button>
              </div>
            ) : null}
            <button
              className={`nav-link ${view === "settings" ? "active" : ""}`}
              onClick={() => navigate("settings")}
            >
              <i className="fa-solid fa-gear"></i>
              Settings
            </button>
          </div>
          <div className="nav-group" style={{ marginTop: "auto" }}>
            <button className="nav-link" onClick={handleLogout}>
              <i className="fa-solid fa-right-from-bracket"></i>
              Logout
            </button>
          </div>
        </aside>
        <section className="main-area">
          <div className="topbar">
            <div className="topbar__group">
              Session:
              <select
                className="select"
                value={sessionValue}
                onChange={(event) => {
                  setSessionValue(event.target.value);
                  setCookie("session", event.target.value);
                }}
              >
                {sessions.map(([sessionNum]) => (
                  <option key={sessionNum} value={String(sessionNum)}>
                    Session {sessionNum}
                  </option>
                ))}
              </select>
            </div>
            <div className="topbar__center" onClick={() => (window.location.href = "/")}>
              YCTC
            </div>
            <div className="topbar__group">
              Branch:
              {branchOptions.length ? (
                <select
                  className="select"
                  value={branchValue}
                  onChange={(event) => {
                    setBranchValue(event.target.value);
                    setCookie("branch", event.target.value);
                  }}
                >
                  {branchOptions.map((branch) => (
                    <option key={branch} value={branch}>
                      {branch}
                    </option>
                  ))}
                </select>
              ) : (
                <span>{branchLabel}</span>
              )}
            </div>
          </div>
          {renderView()}
        </section>
      </div>
    </PageShell>
  );
};

const NotFoundPage = () => (
  <PageShell>
    <div className="page__content">
      <div className="glass-card hero__panel fade-up">
        <h1 className="hero__title">Page not found</h1>
        <p className="hero__subtitle">The page you are looking for does not exist.</p>
        <button className="btn btn--primary" onClick={() => (window.location.href = "/")}>
          Return home
        </button>
      </div>
    </div>
  </PageShell>
);

const App = () => (
  <BrowserRouter>
    <Routes>
      <Route path="/" element={<HomePage />} />
      <Route path="/admin-login" element={<AdminLoginPage />} />
      <Route path="/admin-register" element={<AdminRegisterPage />} />
      <Route path="/forgot" element={<ForgotPage />} />
      <Route path="/otp" element={<OtpPage />} />
      <Route path="/set-new-password" element={<SetNewPasswordPage />} />
      <Route path="/admin/dashboard" element={<DashboardShell />} />
      <Route path="*" element={<NotFoundPage />} />
    </Routes>
  </BrowserRouter>
);

export default App;
