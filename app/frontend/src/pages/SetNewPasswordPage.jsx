import React, { useState } from "react";
import AuthShell from "../components/AuthShell";

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

export default SetNewPasswordPage;
