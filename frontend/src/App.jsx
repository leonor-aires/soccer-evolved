import { useState } from "react";

function App() {
  const API = import.meta.env.VITE_API_BASE || "http://127.0.0.1:8000";
  const [file, setFile] = useState(null);
  const [score, setScore] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleUpload = async (e) => {
    e.preventDefault();
    if (!file) return;

    setLoading(true);
    setError("");
    setScore(null);

    try {
      const form = new FormData();
      form.append("file", file);

      const res = await fetch(`${API}/upload`, {
        method: "POST",
        body: form,
      });

      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      setScore(Math.round((data.competence || 0) * 100)); // 0.75 -> 75
    } catch (err) {
      setError(String(err));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: 520, margin: "40px auto", fontFamily: "system-ui, Arial" }}>
      <h1>Soccer Evolved – Demo</h1>
      <form onSubmit={handleUpload} style={{ display: "flex", gap: 12 }}>
        <input
          type="file"
          accept="video/*,image/*"
          onChange={(e) => setFile(e.target.files?.[0] || null)}
        />
        <button type="submit" disabled={loading || !file}>
          {loading ? "Analyzing..." : "Upload"}
        </button>
      </form>

      {score !== null && (
        <p style={{ marginTop: 16 }}>
          Competence score (fake): <b>{score}%</b>
        </p>
      )}
      {error && <p style={{ color: "red" }}>Error: {error}</p>}

      <hr style={{ margin: "24px 0" }} />
      <small style={{ color: "#666" }}>
        MVP demo: sends a file to the backend and shows a fake score.
        Real AI will replace this soon.
      </small>
    </div>
  );
}

export default App;
