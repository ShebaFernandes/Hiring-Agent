import { useEffect, useState } from "react";
import client from "../api/client";
import { STAGES } from "../constants";
import StageBadge from "./StageBadge";

export default function CandidatesPanel({ jobs }) {
  const [candidates, setCandidates] = useState([]);
  const [loading, setLoading] = useState(true);
  const [jobFilter, setJobFilter] = useState("");
  const [stageFilter, setStageFilter] = useState("");
  const [error, setError] = useState("");

  async function loadCandidates() {
    setLoading(true);
    setError("");
    try {
      const params = {};
      if (jobFilter) params.job_id = jobFilter;
      if (stageFilter) params.stage = stageFilter;
      const res = await client.get("/admin/candidates", { params });
      setCandidates(res.data);
    } catch (err) {
      setError(err.response?.data?.error || "Failed to load candidates");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadCandidates();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [jobFilter, stageFilter]);

  async function handleStageChange(candidate, newStage) {
    // Optimistic update so the dropdown feels instant; loadCandidates() call
    // at the end reconciles with the server response.
    setCandidates((prev) =>
      prev.map((c) => (c.id === candidate.id ? { ...c, stage: newStage } : c))
    );
    try {
      await client.patch(`/admin/candidates/${candidate.id}/stage`, { stage: newStage });
    } catch (err) {
      setError(err.response?.data?.error || "Failed to update stage");
      await loadCandidates(); // revert to server truth on failure
    }
  }

  async function handleDownload(candidate) {
    const res = await client.get(`/admin/candidates/${candidate.id}/resume`, {
      responseType: "blob",
    });
    const url = window.URL.createObjectURL(new Blob([res.data]));
    const link = document.createElement("a");
    link.href = url;
    link.download = candidate.resume_original_name || "resume";
    link.click();
    window.URL.revokeObjectURL(url);
  }

  return (
    <div>
      <div className="panel-header">
        <h2>Candidates ({candidates.length})</h2>
        <div className="filters">
          <select value={jobFilter} onChange={(e) => setJobFilter(e.target.value)}>
            <option value="">All Jobs</option>
            {jobs.map((job) => (
              <option key={job.id} value={job.id}>
                {job.title}
              </option>
            ))}
          </select>
          <select value={stageFilter} onChange={(e) => setStageFilter(e.target.value)}>
            <option value="">All Stages</option>
            {STAGES.map((stage) => (
              <option key={stage} value={stage}>
                {stage}
              </option>
            ))}
          </select>
        </div>
      </div>

      {error && <p className="error-text">{error}</p>}
      {loading ? (
        <p className="muted">Loading candidates...</p>
      ) : (
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Name</th>
                <th>Contact</th>
                <th>Job</th>
                <th>Note</th>
                <th>Resume</th>
                <th>Stage</th>
              </tr>
            </thead>
            <tbody>
              {candidates.map((c) => (
                <tr key={c.id}>
                  <td>{c.name}</td>
                  <td>
                    <div>{c.email}</div>
                    <div className="muted">{c.phone}</div>
                  </td>
                  <td>{c.job_title}</td>
                  <td className="note-cell" title={c.note}>
                    {c.note || "—"}
                  </td>
                  <td>
                    <button className="link-btn" onClick={() => handleDownload(c)}>
                      Download
                    </button>
                  </td>
                  <td>
                    <div className="stage-cell">
                      <StageBadge stage={c.stage} />
                      <select
                        value={c.stage}
                        onChange={(e) => handleStageChange(c, e.target.value)}
                      >
                        {STAGES.map((stage) => (
                          <option key={stage} value={stage}>
                            {stage}
                          </option>
                        ))}
                      </select>
                    </div>
                  </td>
                </tr>
              ))}
              {candidates.length === 0 && (
                <tr>
                  <td colSpan={6} className="muted">
                    No candidates match these filters.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
