async function initSettings() {
    try {
      const res = await fetch('/api/me');
      const data = await res.json();

      document.getElementById('profilePicture').src = data.profilePicture || '/static/default-profile.png';
      document.getElementById('username').value = data.username;
      document.getElementById('email').value = data.email;
      document.getElementById('employeeId').value = data.employeeId;

      document.getElementById('profileForm').addEventListener('submit', async (e) => {
        e.preventDefault();

        const username = document.getElementById('username').value;
        const currentPassword = document.getElementById('currentPassword').value;
        const newPassword = document.getElementById('newPassword').value;
        const confirmPassword = document.getElementById('confirmPassword').value;

        if (!currentPassword) {
          alert("Current password is required to update profile.");
          return;
        }

        if (newPassword && newPassword !== confirmPassword) {
          alert("New password and confirm password do not match.");
          return;
        }

        const payload = {
          username,
          currentPassword,
          newPassword: newPassword || undefined
        };

        const response = await fetch('/update-profile', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          credentials: 'include',
          body: JSON.stringify(payload)
        });

        const result = await response.json();
        alert(result.message || "Update complete.");
      });

      document.getElementById('profileUpload').addEventListener('change', async (event) => {
        const file = event.target.files[0];
        if (!file) return;

        const formData = new FormData();
        formData.append("profilePicture", file);

        const res = await fetch('/update-profile-picture', {
          method: 'POST',
          body: formData,
          credentials: 'include'
        });

        const result = await res.json();
        alert(result.message || "Profile picture updated");

        if (result.newUrl) {
          document.getElementById('profilePicture').src = result.newUrl;
        }
      });

    } catch (err) {
      console.error("Failed to load settings:", err);
      alert("Could not load user data.");
    }
  }

  initSettings();