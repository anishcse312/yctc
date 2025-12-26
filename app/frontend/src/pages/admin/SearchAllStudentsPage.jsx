import React, { useCallback, useEffect, useState } from "react";

const SearchAllStudentsPage = () => {
  const [regNumber, setRegNumber] = useState("");
  const [studentName, setStudentName] = useState("");
  const [message, setMessage] = useState("");
  const [resultsHtml, setResultsHtml] = useState("");

  const runSearch = useCallback(async ({ reg, name }) => {
    let payload = {};
    let endpoint = "";

    if (reg) {
      payload = { registrationNumber: reg };
      endpoint = "/search/by-reg";
    } else if (name) {
      payload = { name };
      endpoint = "/search/by-name";
    }

    try {
      const response = await fetch(endpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      const html = await response.text();
      if (response.status === 403) {
        setMessage("You do not have permission to view this.");
        return;
      }
      if (!response.ok) {
        setMessage("Student not found or error occurred.");
        return;
      }
      setResultsHtml(html);
    } catch (err) {
      setMessage("An error occurred while fetching data.");
    }
  }, []);

  const handleSubmit = async (event) => {
    event.preventDefault();
    setMessage("");
    setResultsHtml("");

    const trimmedReg = regNumber.trim();
    const trimmedName = studentName.trim();

    if ((trimmedReg && trimmedName) || (!trimmedReg && !trimmedName)) {
      setMessage("Please enter either a registration number or a student name, not both.");
      return;
    }

    if (trimmedReg) {
      await runSearch({ reg: trimmedReg });
    } else {
      await runSearch({ name: trimmedName });
    }
  };

  const handleQuickSelect = useCallback(
    async (fullReg) => {
      setRegNumber(fullReg);
      setStudentName("");
      setMessage("");
      setResultsHtml("");
      await runSearch({ reg: fullReg });
    },
    [runSearch]
  );

  useEffect(() => {
    window.postRegNo = handleQuickSelect;
    return () => {
      if (window.postRegNo === handleQuickSelect) {
        delete window.postRegNo;
      }
    };
  }, [handleQuickSelect]);

  return (
    <div className="main-content">
      <div className="panel search-card fade-up">
        <h2>Search All Students</h2>
        <form className="form-row" onSubmit={handleSubmit}>
          <label>
            Registration Number
            <input
              className="input"
              type="text"
              placeholder="YS-N24/6900155/2022"
              value={regNumber}
              onChange={(event) => setRegNumber(event.target.value)}
            />
          </label>
          <label>
            Or Student Name
            <input
              className="input"
              type="text"
              placeholder="Enter Student Name"
              value={studentName}
              onChange={(event) => setStudentName(event.target.value)}
            />
          </label>
          <button className="btn btn--primary" type="submit">
            Search
          </button>
        </form>
        <div className="search-results">
          {message ? (
            <div>{message}</div>
          ) : resultsHtml ? (
            <div dangerouslySetInnerHTML={{ __html: resultsHtml }} />
          ) : (
            <div>Results appear here.</div>
          )}
        </div>
      </div>
    </div>
  );
};

export default SearchAllStudentsPage;
