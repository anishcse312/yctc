import React, { useState } from "react";
import AuthShell from "../components/AuthShell";

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

export default ForgotPage;
