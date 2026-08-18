import { useEffect, useState } from "react";
import client from "../api/client";
import CandidatesPanel from "../components/CandidatesPanel";
import JobsManager from "../components/JobsManager";
import { useAuth } from "../context/AuthContext";

export default function AdminDashboard() {
  const [tab, setTab] = useState("candidates");
  const [jobs, setJobs] = useState([]);
  const { email, logout } = useAuth();

  // Jobs are loaded here (not just inside JobsManager) because
  // CandidatesPanel also needs the list to populate its job filter dropdown.
  useEffect(() => {
    client.get("/admin/jobs").then((res) => setJobs(res.data));
  }, [tab]);

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <h1>Hiring Dashboard</h1>
        <div className="dashboard-header-right">
          <span className="muted">{email}</span>
          <button className="btn btn-secondary" onClick={logout}>
            Log Out
          </button>
        </div>
      </header>

      <nav className="tabs">
        <button
          className={tab === "candidates" ? "tab active" : "tab"}
          onClick={() => setTab("candidates")}
        >
          Candidates
        </button>
        <button
          className={tab === "jobs" ? "tab active" : "tab"}
          onClick={() => setTab("jobs")}
        >
          Jobs
        </button>
      </nav>

      <main className="dashboard-content">
        {tab === "candidates" ? <CandidatesPanel jobs={jobs} /> : <JobsManager />}
      </main>
    </div>
  );
}
