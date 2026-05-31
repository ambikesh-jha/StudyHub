import { useState } from "react";
import { useAuth } from "../hooks/useAuth";

export default function Login() {
  const { signIn, register } = useAuth();
  const [mode, setMode] = useState("login");
  const [form, setForm] = useState({ email: "", password: "", display_name: "" });
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  async function submit(e) {
    e.preventDefault();
    setBusy(true);
    setError("");
    try {
      if (mode === "login") {
        await signIn(form.email, form.password);
      } else {
        await register({
          email: form.email,
          password: form.password,
          display_name: form.display_name || form.email.split("@")[0],
        });
      }
    } catch (err) {
      setError(err.message || "Authentication failed");
    } finally {
      setBusy(false);
    }
  }

  return (
    <main className="auth-page">
      <section className="auth-panel">
        <div className="auth-brand">
          <i className="ti ti-stack-2"></i>
          <span>StudyHub</span>
        </div>
        <div className="auth-tabs">
          <button className={mode === "login" ? "active" : ""} onClick={() => setMode("login")}>Login</button>
          <button className={mode === "register" ? "active" : ""} onClick={() => setMode("register")}>Register</button>
        </div>
        <form onSubmit={submit} className="auth-form">
          {mode === "register" && (
            <label>
              <span>Name</span>
              <input value={form.display_name} onChange={e => setForm(f => ({ ...f, display_name: e.target.value }))} placeholder="Ambikesh" />
            </label>
          )}
          <label>
            <span>Email</span>
            <input type="email" value={form.email} onChange={e => setForm(f => ({ ...f, email: e.target.value }))} placeholder="you@example.com" required />
          </label>
          <label>
            <span>Password</span>
            <input type="password" value={form.password} onChange={e => setForm(f => ({ ...f, password: e.target.value }))} placeholder="At least 8 characters" minLength={8} required />
          </label>
          {error && <div className="form-error">{error}</div>}
          <button className="btn-solid auth-submit" disabled={busy}>
            {busy ? "Please wait..." : mode === "login" ? "Login" : "Create account"}
          </button>
        </form>
      </section>
    </main>
  );
}
