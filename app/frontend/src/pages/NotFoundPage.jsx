import React from "react";
import PageShell from "../components/PageShell";

const NotFoundPage = () => (
  <PageShell>
    <div className="page__content">
      <div className="glass-card hero__panel fade-up">
        <h1 className="hero__title">Page not found</h1>
        <p className="hero__subtitle">The page you are looking for does not exist.</p>
        <button
          className="btn btn--primary"
          onClick={() => (window.location.href = "/")}
        >
          Return home
        </button>
      </div>
    </div>
  </PageShell>
);

export default NotFoundPage;
