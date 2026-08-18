import { useEffect, useState } from "react";
import client from "../api/client";
import JobFormModal from "./JobFormModal";

export default function JobsManager() {
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [editingJob, setEditingJob] = useState(null); // null = closed, {} = create, {...} = edit
  const [error, setError] = useState("");

  async function loadJobs() {
    setLoading(true);
    try {
      const res = await client.get("/admin/jobs");
      setJobs(res.data);
    } catch (err) {
      setError(err.response?.data?.error || "Failed to load jobs");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadJobs();
  }, []);

  async function handleSave(form) {
    if (editingJob?.id) {
      await client.put(`/admin/jobs/${editingJob.id}`, form);
    } else {
      await client.post("/admin/jobs", form);
    }
    setEditingJob(null);
    await loadJobs();
  }

  async function handleDelete(job) {
    if (!confirm(`Delete "${job.title}"? Existing applications for it are kept.`)) return;
    await client.delete(`/admin/jobs/${job.id}`);
    await loadJobs();
  }

  if (loading) return <p className="muted">Loading jobs...</p>;

  return (
    <div>
      <div className="panel-header">
        <h2>Jobs ({jobs.length})</h2>
        <button className="btn btn-primary" onClick={() => setEditingJob({})}>
          + New Job
        </button>
      </div>

      {error && <p className="error-text">{error}</p>}

      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Title</th>
              <th>Department</th>
              <th>Location</th>
              <th>Type</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {jobs.map((job) => (
              <tr key={job.id}>
                <td>{job.title}</td>
                <td>{job.department || "—"}</td>
                <td>{job.location || "—"}</td>
                <td>{job.job_type}</td>
                <td className="row-actions">
                  <button className="link-btn" onClick={() => setEditingJob(job)}>
                    Edit
                  </button>
                  <button className="link-btn danger" onClick={() => handleDelete(job)}>
                    Delete
                  </button>
                </td>
              </tr>
            ))}
            {jobs.length === 0 && (
              <tr>
                <td colSpan={5} className="muted">
                  No jobs yet. Create one to get started.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {editingJob !== null && (
        <JobFormModal
          initialJob={editingJob.id ? editingJob : null}
          onSave={handleSave}
          onClose={() => setEditingJob(null)}
        />
      )}
    </div>
  );
}
