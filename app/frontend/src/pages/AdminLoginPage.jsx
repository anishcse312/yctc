import React, { useState } from "react";
import AuthShell from "../components/AuthShell";

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

export default AdminLoginPage;
