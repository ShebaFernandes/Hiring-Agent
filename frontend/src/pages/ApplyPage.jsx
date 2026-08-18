import { useEffect, useState } from "react";
import client from "../api/client";

const EMPTY_FORM = { name: "", phone: "", email: "", job_id: "", note: "" };

export default function ApplyPage() {
  const [jobs, setJobs] = useState([]);
  const [form, setForm] = useState(EMPTY_FORM);
  const [resume, setResume] = useState(null);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState(false);

  useEffect(() => {
    client.get("/jobs").then((res) => setJobs(res.data));
  }, []);

  function handleChange(e) {
    setForm({ ...form, [e.target.name]: e.target.value });
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");

    if (!resume) {
      setError("Please attach your resume (PDF or Word doc)");
      return;
    }

    // A plain object can't hold a File, so the request body is built as
    // multipart/form-data - axios sets the right Content-Type automatically
    // once it sees a FormData instance.
    const payload = new FormData();
    Object.entries(form).forEach(([key, value]) => payload.append(key, value));
    payload.append("resume", resume);

    setSubmitting(true);
    try {
      await client.post("/apply", payload);
      setSuccess(true);
      setForm(EMPTY_FORM);
      setResume(null);
    } catch (err) {
      setError(err.response?.data?.error || "Something went wrong. Please try again.");
    } finally {
      setSubmitting(false);
    }
  }

  if (success) {
    return (
      <div className="page-center">
        <div className="card">
          <h1>Application received</h1>
          <p className="muted">Thanks for applying — we'll be in touch.</p>
          <button className="btn btn-primary" onClick={() => setSuccess(false)}>
            Submit another application
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="page-center">
      <div className="card card-wide">
        <h1>Apply for a job</h1>
        <p className="muted">Fill in your details below to apply.</p>

        <form onSubmit={handleSubmit} className="form">
          <label>
            Full Name *
            <input name="name" value={form.name} onChange={handleChange} required />
          </label>
          <label>
            Phone *
            <input name="phone" value={form.phone} onChange={handleChange} required />
          </label>
          <label>
            Email *
            <input type="email" name="email" value={form.email} onChange={handleChange} required />
          </label>
          <label>
            Job *
            <select name="job_id" value={form.job_id} onChange={handleChange} required>
              <option value="" disabled>
                Select a job
              </option>
              {jobs.map((job) => (
                <option key={job.id} value={job.id}>
                  {job.title}
                  {job.location ? ` — ${job.location}` : ""}
                </option>
              ))}
            </select>
          </label>
          <label>
            Resume (PDF or Word) *
            <input
              type="file"
              accept=".pdf,.doc,.docx"
              onChange={(e) => setResume(e.target.files[0])}
            />
          </label>
          <label>
            Brief note
            <textarea
              name="note"
              value={form.note}
              onChange={handleChange}
              rows={3}
              placeholder="Anything you'd like us to know"
            />
          </label>

          {error && <p className="error-text">{error}</p>}

          <button type="submit" className="btn btn-primary btn-block" disabled={submitting}>
            {submitting ? "Submitting..." : "Submit Application"}
          </button>
        </form>
      </div>
    </div>
  );
}
