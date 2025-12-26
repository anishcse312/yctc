import React, { useEffect, useState } from "react";

const SettingsPage = () => {
  const [profile, setProfile] = useState({
    username: "",
    email: "",
    employeeId: "",
    profilePicture: "",
  });
  const [passwords, setPasswords] = useState({
    currentPassword: "",
    newPassword: "",
    confirmPassword: "",
  });
  const [status, setStatus] = useState({ loading: false, message: "" });

  useEffect(() => {
    const loadProfile = async () => {
      try {
        const res = await fetch("/api/me", { credentials: "include" });
        const data = await res.json();
        setProfile({
          username: data.username || "",
          email: data.email || "",
          employeeId: data.employeeId || "",
          profilePicture: data.profilePicture || "/static/default-profile.png",
        });
      } catch (err) {
        setStatus({ loading: false, message: "Could not load user data." });
      }
    };
    loadProfile();
  }, []);

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (!passwords.currentPassword) {
      setStatus({ loading: false, message: "Current password is required." });
      return;
    }
    if (passwords.newPassword && passwords.newPassword !== passwords.confirmPassword) {
      setStatus({ loading: false, message: "New password mismatch." });
      return;
    }
    setStatus({ loading: true, message: "" });
    try {
      const payload = {
        username: profile.username,
        currentPassword: passwords.currentPassword,
        newPassword: passwords.newPassword || undefined,
      };
      const response = await fetch("/update-profile", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify(payload),
      });
      const result = await response.json();
      setStatus({ loading: false, message: result.message || "Update complete." });
    } catch (err) {
      setStatus({ loading: false, message: "Update failed." });
    }
  };

  const handleFileChange = async (event) => {
    const file = event.target.files[0];
    if (!file) return;
    const formData = new FormData();
    formData.append("profilePicture", file);
    try {
      const res = await fetch("/update-profile-picture", {
        method: "POST",
        body: formData,
        credentials: "include",
      });
      const result = await res.json();
      setStatus({ loading: false, message: result.message || "Profile picture updated." });
      if (result.newUrl) {
        setProfile((prev) => ({ ...prev, profilePicture: result.newUrl }));
      }
    } catch (err) {
      setStatus({ loading: false, message: "Upload failed." });
    }
  };

  return (
    <div className="main-content">
      <div className="panel profile-card fade-up">
        <div className="profile-header">
          <img className="profile-avatar" src={profile.profilePicture} alt="Profile" />
          <label className="upload-btn">
            Upload photo
            <input type="file" hidden accept="image/*" onChange={handleFileChange} />
          </label>
        </div>
        <form className="form-row" onSubmit={handleSubmit}>
          <label>
            Username
            <input
              className="input"
              type="text"
              value={profile.username}
              onChange={(event) => setProfile({ ...profile, username: event.target.value })}
            />
          </label>
          <label>
            Current Password
            <input
              className="input"
              type="password"
              value={passwords.currentPassword}
              onChange={(event) =>
                setPasswords({ ...passwords, currentPassword: event.target.value })
              }
            />
          </label>
          <label>
            New Password
            <input
              className="input"
              type="password"
              value={passwords.newPassword}
              onChange={(event) =>
                setPasswords({ ...passwords, newPassword: event.target.value })
              }
            />
          </label>
          <label>
            Confirm Password
            <input
              className="input"
              type="password"
              value={passwords.confirmPassword}
              onChange={(event) =>
                setPasswords({ ...passwords, confirmPassword: event.target.value })
              }
            />
          </label>
          <label>
            Email
            <input className="input" type="email" value={profile.email} disabled />
          </label>
          <label>
            Employee ID
            <input className="input" type="text" value={profile.employeeId} disabled />
          </label>
          <button className="btn btn--primary" type="submit" disabled={status.loading}>
            {status.loading ? "Updating..." : "Update Profile"}
          </button>
          {status.message ? <div className="helper-text">{status.message}</div> : null}
        </form>
      </div>
    </div>
  );
};

export default SettingsPage;
