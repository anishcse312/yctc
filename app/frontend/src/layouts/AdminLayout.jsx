import React, { useEffect, useState } from "react";
import { Outlet, useLocation, useNavigate } from "react-router-dom";
import PageShell from "../components/PageShell";
import { getCookie, setCookie } from "../utils/cookies";

const AdminLayout = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const [studentsOpen, setStudentsOpen] = useState(
    location.pathname.startsWith("/admin/students")
  );
  const [sessions, setSessions] = useState([]);
  const [sessionValue, setSessionValue] = useState("");
  const [branchOptions, setBranchOptions] = useState([]);
  const [branchValue, setBranchValue] = useState("");
  const [branchLabel, setBranchLabel] = useState("Loading...");

  useEffect(() => {
    if (location.pathname.startsWith("/admin/students")) {
      setStudentsOpen(true);
    } else {
      setStudentsOpen(false);
    }
  }, [location.pathname]);

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

  const isActive = (path) => location.pathname === path;

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
              className={`nav-link ${isActive("/admin/dashboard") ? "active" : ""}`}
              onClick={() => navigate("/admin/dashboard")}
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
                  className={`nav-link ${
                    isActive("/admin/students/search") ? "active" : ""
                  }`}
                  onClick={() => navigate("/admin/students/search")}
                >
                  Search All Students
                </button>
                <button
                  className={`nav-link ${
                    isActive("/admin/students/lateralAdmissions") ? "active" : ""
                  }`}
                  onClick={() => navigate("/admin/students/lateralAdmissions")}
                >
                  Student Lateral Admission
                </button>
              </div>
            ) : null}
            <button
              className={`nav-link ${isActive("/admin/settings") ? "active" : ""}`}
              onClick={() => navigate("/admin/settings")}
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
            <div
              className="topbar__center"
              onClick={() => (window.location.href = "/")}
            >
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
          <Outlet />
        </section>
      </div>
    </PageShell>
  );
};

export default AdminLayout;
