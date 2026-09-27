import { useState } from "react";
import { createKitten, uploadPhoto } from "../api";

// Form for posting a new kitten listing, with photo upload from the device.
export default function KittenForm({ onCreated }) {
  const [name, setName] = useState("");
  const [age, setAge] = useState("");
  const [location, setLocation] = useState("");
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState("");
  const [notes, setNotes] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  function handleFileChange(e) {
    const f = e.target.files[0];
    setFile(f || null);
    setPreview(f ? URL.createObjectURL(f) : ""); // local preview before upload
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    setBusy(true);
    try {
      // 1. if a photo was chosen, upload it first and get back a URL
      let photoUrl = null;
      if (file) {
        photoUrl = await uploadPhoto(file);
      }
      // 2. create the listing with that photo URL
      await createKitten({
        name,
        age: age ? Number(age) : null,
        location,
        photo: photoUrl,
        notes: notes || null,
      });
      // reset
      setName("");
      setAge("");
      setLocation("");
      setFile(null);
      setPreview("");
      setNotes("");
      e.target.reset();
      onCreated();
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="card">
      <h3>Post a kitten for adoption</h3>
      <form onSubmit={handleSubmit} className="kitten-form">
        <input placeholder="Name *" value={name} onChange={(e) => setName(e.target.value)} required />
        <input placeholder="Age (years)" type="number" min="0" value={age} onChange={(e) => setAge(e.target.value)} />
        <input placeholder="Location *" value={location} onChange={(e) => setLocation(e.target.value)} required />

        <label className="file-label">
          {file ? "Change photo" : "📷 Upload a cat photo"}
          <input type="file" accept="image/*" onChange={handleFileChange} hidden />
        </label>
        {preview && <img className="preview" src={preview} alt="preview" />}

        <textarea placeholder="Notes (optional)" value={notes} onChange={(e) => setNotes(e.target.value)} />
        {error && <p className="error">{error}</p>}
        <button type="submit" disabled={busy}>{busy ? "Posting..." : "Post listing"}</button>
      </form>
    </div>
  );
}
