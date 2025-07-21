document
  .getElementById("searchForm")
  .addEventListener("submit", async (e) => {
    e.preventDefault();

    const regInput = document.getElementById("regNumber");
    const nameInput = document.getElementById("studentName");
    const studentDetails = document.getElementById("studentDetails");

    const regNumber = regInput.value.trim();
    const studentName = nameInput.value.trim();

    studentDetails.innerHTML = "";

    if ((regNumber && studentName) || (!regNumber && !studentName)) {
      studentDetails.textContent =
        "Please enter either a registration number or a student name, not both.";
      return;
    }

    let payload = {};
    let endpoint = "";

    if (regNumber) {
      payload = { registrationNumber: `YS-N24/${regNumber}` };
      endpoint = "/search/by-reg";
    } else if (studentName) {
      payload = { name: studentName };
      endpoint = "/search/by-name";
    }

    try {
      const response = await fetch(endpoint, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      });

      const html = await response.text();

      if (!response.ok) {
        studentDetails.textContent = "Student not found or error occurred.";
        return;
      }

      studentDetails.innerHTML = html; // expects rows with onclick="postRegNo(...)"
    } catch (error) {
      console.error(error);
      studentDetails.textContent = "An error occurred while fetching data.";
    }
  });
