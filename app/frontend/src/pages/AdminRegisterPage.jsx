import React, { useState } from "react";
import AuthShell from "../components/AuthShell";

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

export default AdminRegisterPage;
