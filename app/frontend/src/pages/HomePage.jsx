import React from "react";
import PageShell from "../components/PageShell";
import { getCookie } from "../utils/cookies";

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

export default HomePage;
