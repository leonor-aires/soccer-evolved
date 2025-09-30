import { useState } from "react";

const API = "http://localhost:8000"; // your FastAPI URL

export default function App() {
  const [gesture, setGesture] = useState("shooting"); // "shooting" | "passing"
  const [file, setFile] = useState(null);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  // response of /upload
  const [result, setResult] = useState(null);

  // list from /videos
  const [recent, setRecent] = useState([]);
  const [top, setTop] = useState([]);

  const handleUpload = async (e) => {
    e.preventDefault();
    if (!file) return;

    setLoading(true);
    setError("");
    setResult(null);

    try {
      const form = new FormData();
      form.append("file", file);

      const res = await fetch(`${API}/upload?gesture=${encodeURIComponent(gesture)}`, {
        method: "POST",
        body: form,
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);

      const data = await res.json();
      setResult(data);

      // refresh lists after a successful upload
      await refreshLists();
    } catch (err) {
      setError(String(err));
    } finally {
      setLoading(false);
    }
  };

  const refreshLists = async () => {
    try {
      setError("");
      const [topRes, allRes] = await Promise.all([
        fetch(`${API}/videos?gesture=${gesture}&type=top`),
        fetch(`${API}/videos?gesture=${gesture}&type=all`),
      ]);
      if (!topRes.ok || !allRes.ok) throw new Error("HTTP error while loading lists");

      setTop(await topRes.json());
      setRecent(await allRes.json());
    } catch (err) {
      setError(String(err));
    }
  };

  return (
    <div style={{ maxWidth: 900, margin: "32px auto", fontFamily: "system-ui, Arial" }}>
      <h1 style={{ marginTop: 0 }}>Soccer Evolved – MVP</h1>

      {/* Gesture selector */}
      <label>
        Gesto:&nbsp;
        <select value={gesture} onChange={(e) => setGesture(e.target.value)}>
          <option value="shooting">Remate (Shooting)</option>
          <option value="passing">Passe (Passing)</option>
        </select>
      </label>

      {/* Upload form */}
      <form onSubmit={handleUpload} style={{ display: "flex", gap: 12, alignItems: "center", marginTop: 12 }}>
        <input
          type="file"
          accept="video/*,image/*"
          onChange={(e) => setFile(e.target.files?.[0] || null)}
        />
        <button type="submit" disabled={loading || !file}>
          {loading ? "A analisar..." : "Upload"}
        </button>
        <button type="button" onClick={refreshLists} disabled={loading} title="Atualizar listas">
          Atualizar lista
        </button>
      </form>

      {/* Upload result */}
      {result && (
        <div style={{ marginTop: 16, padding: 12, border: "1px solid #ddd", borderRadius: 8 }}>
          <h3 style={{ marginTop: 0 }}>
            Resultado — {gesture === "shooting" ? "Remate" : "Passe"}
          </h3>
          <p>
            Competência:{" "}
            <b>{Math.round((result.competence || 0) * 100)}%</b>
          </p>

          {Array.isArray(result.errors) && result.errors.length > 0 && (
            <>
              <p><b>Erros detetados:</b></p>
              <ul>{result.errors.map((e, i) => <li key={i}>{String(e)}</li>)}</ul>
            </>
          )}

          {Array.isArray(result.tips) && result.tips.length > 0 && (
            <>
              <p><b>Dicas:</b></p>
              <ul>{result.tips.map((t, i) => <li key={i}>{String(t)}</li>)}</ul>
            </>
          )}
        </div>
      )}

      {error && <p style={{ color: "red", marginTop: 12 }}>Erro: {error}</p>}

      {/* Lists */}
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 24, marginTop: 24 }}>
        <section>
          <h3>Top 5 analisados — {gesture === "shooting" ? "Remate" : "Passe"}</h3>
          <ul>
            {top.length === 0 && <li>Sem vídeos ainda.</li>}
            {top.map((v) => (
              <li key={v.video_id}>
                {v.created_at} — {v.filename} — {Math.round((v.competence || 0) * 100)}%
              </li>
            ))}
          </ul>
        </section>

        <section>
          <h3>Uploads recentes — {gesture === "shooting" ? "Remate" : "Passe"}</h3>
          <ul>
            {recent.length === 0 && <li>Sem vídeos ainda.</li>}
            {recent.map((v) => (
              <li key={v.video_id}>
                {v.created_at} — {v.filename} — {Math.round((v.competence || 0) * 100)}%
              </li>
            ))}
          </ul>
        </section>
      </div>

      <hr style={{ margin: "24px 0" }} />
      <small style={{ color: "#666" }}>
        MVP: o score é de exemplo (0.75). Quando tivermos os vídeos, ligamos o AI real no backend.
      </small>
    </div>
  );
}
