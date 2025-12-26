import React from "react";
import PageShell from "./PageShell";

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

export default AuthShell;
