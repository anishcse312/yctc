import React, { useRef, useState } from "react";
import AuthShell from "../components/AuthShell";

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

export default OtpPage;
