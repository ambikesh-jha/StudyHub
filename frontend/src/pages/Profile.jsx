import { useEffect, useRef, useState } from "react";
import { api } from "../api/client";
import Skeleton from "../components/Skeleton";
import { useAuth } from "../hooks/useAuth";

export default function Profile() {
  const { user, setUser, signOut } = useAuth();
  const [profile, setProfile] = useState(user);
  const [stats, setStats] = useState(null);
  const [preferences, setPreferences] = useState(null);
  const [saving, setSaving] = useState(false);
  const [password, setPassword] = useState({ current_password: "", new_password: "", confirm_password: "" });
  const [message, setMessage] = useState("");
  const fileRef = useRef();

  useEffect(() => {
    let alive = true;
    async function load() {
      const [freshProfile, freshStats, freshPreferences] = await Promise.all([api.me(), api.stats(), api.preferences()]);
      if (!alive) return;
      setProfile(freshProfile);
      setUser(freshProfile);
      setStats(freshStats);
      setPreferences(freshPreferences);
    }
    load().catch(error => setMessage(error.message));
    return () => { alive = false; };
  }, []);

  async function saveProfile(e) {
    e.preventDefault();
    setSaving(true);
    setMessage("");
    try {
      const updated = await api.updateMe({
        display_name: profile.display_name,
        email: profile.email,
        bio: profile.bio,
      });
      setProfile(updated);
      setUser(updated);
      setMessage("Profile saved");
    } catch (error) {
      setMessage(error.message);
    } finally {
      setSaving(false);
    }
  }

  async function uploadAvatar(e) {
    const file = e.target.files?.[0];
    if (!file) return;
    const result = await api.uploadAvatar(file);
    setProfile(prev => ({ ...prev, avatar_url: result.avatar_url }));
  }

  async function saveTheme(theme_mode) {
    const updated = await api.updatePreferences({ ...preferences, theme_mode });
    setPreferences(updated);
    setUser(prev => prev ? { ...prev, preferences: updated } : prev);
  }

  async function changePassword(e) {
    e.preventDefault();
    setMessage("");
    try {
      await api.changePassword(password);
      setPassword({ current_password: "", new_password: "", confirm_password: "" });
      setMessage("Password changed");
    } catch (error) {
      setMessage(error.message);
    }
  }

  if (!profile) {
    return <main className="profile-page"><Skeleton rows={4} /></main>;
  }

  return (
    <main className="profile-page">
      <header className="profile-header">
        <div className="avatar" style={profile.avatar_url ? { backgroundImage: `url(${api.uploadUrl(profile.avatar_url)})` } : null}>
          {!profile.avatar_url && <i className="ti ti-user"></i>}
        </div>
        <div>
          <h1>{profile.display_name}</h1>
          <p>{profile.email}</p>
        </div>
        <button className="btn-ghost" onClick={signOut}><i className="ti ti-logout"></i> Logout</button>
      </header>

      <section className="profile-grid">
        <form className="settings-panel" onSubmit={saveProfile}>
          <h2>Profile</h2>
          <label>Name<input value={profile.display_name || ""} onChange={e => setProfile(p => ({ ...p, display_name: e.target.value }))} /></label>
          <label>Email<input type="email" value={profile.email || ""} onChange={e => setProfile(p => ({ ...p, email: e.target.value }))} /></label>
          <label>Bio<textarea rows={4} value={profile.bio || ""} onChange={e => setProfile(p => ({ ...p, bio: e.target.value }))} /></label>
          <div className="profile-actions">
            <button type="button" className="btn-outline" onClick={() => fileRef.current.click()}><i className="ti ti-photo-up"></i> Avatar</button>
            <button className="btn-solid" disabled={saving}>{saving ? "Saving..." : "Save"}</button>
          </div>
          <input ref={fileRef} hidden type="file" accept="image/*" onChange={uploadAvatar} />
        </form>

        <div className="settings-panel">
          <h2>Account</h2>
          <div className="stats-grid">
            <span><strong>{stats?.owned_courses ?? 0}</strong> Courses</span>
            <span><strong>{stats?.owned_topics ?? 0}</strong> Topics</span>
            <span><strong>{stats?.owned_materials ?? 0}</strong> Materials</span>
          </div>
          <div className="stats-grid secondary">
            <span><strong>{stats?.courses_enrolled ?? 0}</strong> Enrolled</span>
            <span><strong>{stats?.courses_completed ?? 0}</strong> Done</span>
            <span><strong>{stats?.streak_days ?? 0}</strong> Streak</span>
          </div>
          <div className="theme-toggle">
            {["system", "light", "dark"].map(theme => (
              <button key={theme} className={preferences?.theme_mode === theme ? "active" : ""} onClick={() => saveTheme(theme)}>
                {theme}
              </button>
            ))}
          </div>
          <form onSubmit={changePassword} className="password-form">
            <input type="password" placeholder="Current password" value={password.current_password} onChange={e => setPassword(p => ({ ...p, current_password: e.target.value }))} />
            <input type="password" placeholder="New password" value={password.new_password} onChange={e => setPassword(p => ({ ...p, new_password: e.target.value }))} />
            <input type="password" placeholder="Confirm password" value={password.confirm_password} onChange={e => setPassword(p => ({ ...p, confirm_password: e.target.value }))} />
            <button className="btn-outline">Change password</button>
          </form>
          {message && <div className="profile-message">{message}</div>}
        </div>
      </section>
    </main>
  );
}
