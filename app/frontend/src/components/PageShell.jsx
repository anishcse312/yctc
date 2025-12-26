import React from "react";

const PageShell = ({ children, className = "" }) => (
  <div className={`page ${className}`}>{children}</div>
);

export default PageShell;
