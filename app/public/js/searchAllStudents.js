export function initSearchAllStudents() {
  const sessionMap = {};

  async function loadSessions() {
  try {
    const res = await fetch("/api/sessions");
    const sessions = await res.json();

    const sessionSelect = document.getElementById("sessionSelect");
    const yearSpan = document.getElementById("sessionYear");
    sessionSelect.innerHTML = "";

    sessions.forEach(([sessionNum, year]) => {
      const option = document.createElement("option");
      option.value = String(sessionNum);
      option.textContent = `Session ${sessionNum}`;
      sessionSelect.appendChild(option);
      sessionMap[sessionNum] = year;
    });

    if (sessions.length > 0) {
      const defaultSession = sessions[0][0];
      sessionSelect.value = defaultSession;
      yearSpan.textContent = sessionMap[defaultSession];
    }

    sessionSelect.addEventListener("change", () => {
      const selected = sessionSelect.value;
      yearSpan.textContent = sessionMap[selected] || "----";
    });
  } catch (err) {
    console.error("Failed to load sessions", err);
  }
}


  document.getElementById("searchForm").addEventListener("submit", async function (e) {
    e.preventDefault();
    const regPrefix = "YS-N24";
    const session = document.getElementById("sessionSelect").value;
    const regNum = document.getElementById("regNumber").value.trim();
    const year = sessionMap[session];
    const display = document.getElementById("studentDetails");

    if (!regNum || !year) return;

    const fullReg = `${regPrefix}/${session}-${regNum}/${year}`;
    display.textContent = "Loading...";

    try {
      const res = await fetch("/searchStudent", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ regNo: fullReg })
      });

      const data = await res.json();
      if (res.status !== 200) {
        display.textContent = data.message || "Student not found.";
        return;
      }

      display.textContent = renderStudent(data);
    } catch (err) {
      display.textContent = "Failed to fetch data.";
      console.error(err);
    }
  });

  function renderStudent(d) {
    const clean = (v) => (v === null || v === "nan" || typeof v === "undefined" ? "-" : v);

    let out = `\u{1F4CC} Registration No: ${clean(d.reg_no)}\n\n`;
    out += `\u{1F464} General Info:\n`;
    out += `Name       : ${clean(d.name)}\n`;
    out += `Father's   : ${clean(d.f_name)}\n`;
    out += `DOB        : ${clean(d.dob)}\n`;
    out += `Sex        : ${clean(d.sex)}     Caste : ${clean(d.caste)}\n`;
    out += `Phone      : ${clean(d.phone)}\n`;
    out += `Address    : ${clean(d.add_1)}\n             ${clean(d.po)}, ${clean(d.district)} - ${clean(d.pin)}\n\n`;

    out += `\u{1F393} Qualification (General):\n`;
    ["GQ1", "GQ2", "GQ3", "GQ4"].forEach((key) => {
      if (d[key]) {
        const [exam, year, board, marks] = d[key].split("#");
        out += `${exam.padEnd(6)} - ${year} - ${board} - Marks: ${marks}\n`;
      }
    });

    out += `\n\u{1F4D8} Course Details:\n`;
    out += `Course     : ${clean(d.course_id)}\n`;
    out += `Batch      : ${clean(d.batch)}\n`;
    out += `Session    : ${clean(d.session)} (${clean(d.ses_half)})\n`;
    out += `Semester   : ${clean(d.semister)}\n`;
    out += `Form No    : ${clean(d.form_no)}\n`;
    out += `Final Roll : ${clean(d.final_roll)}\n`;
    out += `Scholar    : ${clean(d.scholar)}\n`;
    out += `Lateral    : ${clean(d.lateral)}\n`;
    out += `Remarks    : ${clean(d.Remarks)}\n\n`;

    out += `\u{1F4C4} Previous Reg: ${clean(d.pre_reg)}\n`;
    out += `\u{1F4C4} Next Reg    : ${clean(d.n_reg_no_1)}\n\n`;

    out += `\u{1F4B5} Admission & Fees:\n`;
    out += `Admission Date : ${clean(d.admission)} | Receipt #: ${clean(d.admn_recpt)} | Amount: ${clean(d.amount)}\n`;
    for (let i = 1; i <= 5; i++) {
      out += `Instalment ${i}   : ${clean(d[`inst_${i}_dt`])} | Receipt #: ${clean(d[`i_${i}_recpt`])}\n`;
    }
    if (d.fine_amt) {
      out += `Fine Amount    : ₹${clean(d.fine_amt)} (${clean(d.fine_days)} days late)\n`;
    }

    out += `\n\u{1F4BE} Payment Mode: ${clean(d.pay_mode)} | Centre: ${clean(d.centre)}\n`;
    out += `\u{1F4DD} Attended By: ${clean(d.Attend_By)} | Prospectus Issued: ${clean(d.ProspectusIssued)}\n`;

    return out;
  }

  loadSessions();
}