import { useState } from "react";
import { updateKitten, deleteKitten } from "../api";

// A single kitten listing. Owners get edit/delete controls; everyone else
// just sees the details (mirrors the backend's ownership rules).
export default function KittenCard({ kitten, isOwner, onChanged }) {
  const [editing, setEditing] = useState(false);
  const [status, setStatus] = useState(kitten.status);
  const [notes, setNotes] = useState(kitten.notes || "");
  const [error, setError] = useState("");

  async function handleSave() {
    setError("");
    try {
      await updateKitten(kitten.id, { status, notes: notes || null });
      setEditing(false);
      onChanged();
    } catch (err) {
      setError(err.message);
    }
  }

  async function handleDelete() {
    setError("");
    try {
      await deleteKitten(kitten.id);
      onChanged();
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <div className="card kitten-card">
      {kitten.photo ? (
        <img className="kitten-photo" src={kitten.photo} alt={kitten.name} />
      ) : (
        <div className="kitten-photo placeholder">🐱</div>
      )}

      <div className="kitten-body">
        <div className="kitten-head">
          <h4>{kitten.name}</h4>
          <span className={`badge ${kitten.status === "adopted" ? "adopted" : "available"}`}>
            {kitten.status}
          </span>
        </div>
        <p className="muted">
          {kitten.age != null ? `${kitten.age} yr` : "age unknown"} · {kitten.location}
        </p>

        {editing ? (
          <div className="edit-area">
            <label>
              Status:
              <select value={status} onChange={(e) => setStatus(e.target.value)}>
                <option value="available">available</option>
                <option value="adopted">adopted</option>
              </select>
            </label>
            <textarea value={notes} onChange={(e) => setNotes(e.target.value)} placeholder="Notes" />
            <div className="row">
              <button onClick={handleSave}>Save</button>
              <button className="secondary" onClick={() => setEditing(false)}>Cancel</button>
            </div>
          </div>
        ) : (
          <p>{kitten.notes || <span className="muted">No notes</span>}</p>
        )}

        {error && <p className="error">{error}</p>}

        {isOwner && !editing && (
          <div className="row">
            <button className="secondary" onClick={() => setEditing(true)}>Edit</button>
            <button className="danger" onClick={handleDelete}>Delete</button>
          </div>
        )}
      </div>
    </div>
  );
}
