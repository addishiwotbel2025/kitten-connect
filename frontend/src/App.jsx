import { useEffect, useState, useCallback } from "react";
import { getMe, listKittens, getToken, clearToken } from "./api";
import AuthForm from "./components/AuthForm";
import KittenForm from "./components/KittenForm";
import KittenCard from "./components/KittenCard";
import BackgroundRotator from "./components/BackgroundRotator";
import { CatFaceIcon, PawIcon } from "./components/icons";
import "./App.css";

export default function App() {
  const [user, setUser] = useState(null);       // current logged-in user, or null
  const [kittens, setKittens] = useState([]);
  const [loading, setLoading] = useState(true);

  // Load the logged-in user (if a token exists) and the kitten list.
  const refresh = useCallback(async () => {
    setLoading(true);
    try {
      if (getToken()) {
        try {
          setUser(await getMe());
        } catch {
          clearToken();       // token expired/invalid
          setUser(null);
        }
      }
      setKittens(await listKittens());
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  function handleLogout() {
    clearToken();
    setUser(null);
  }

  return (
    <div className="app">
      <BackgroundRotator />

      <header className="topbar">
        <h1 className="brand">
          <CatFaceIcon size={30} /> KittenConnect
        </h1>
        {user && (
          <div className="userbox">
            <span>Hi, {user.name}</span>
            <button className="secondary" onClick={handleLogout}>Log out</button>
          </div>
        )}
      </header>

      <main className="layout">
        <section className="sidebar">
          {user ? (
            <KittenForm onCreated={refresh} />
          ) : (
            <AuthForm onAuthed={refresh} />
          )}
        </section>

        <section className="feed">
          <h2 className="feed-title"><PawIcon size={20} /> Available kittens</h2>
          {loading ? (
            <p className="muted">Loading...</p>
          ) : kittens.length === 0 ? (
            <p className="muted">No kittens listed yet. Be the first to post one!</p>
          ) : (
            <div className="grid">
              {kittens.map((k) => (
                <KittenCard
                  key={k.id}
                  kitten={k}
                  isOwner={user && k.owner_id === user.id}
                  onChanged={refresh}
                />
              ))}
            </div>
          )}
        </section>
      </main>
    </div>
  );
}
