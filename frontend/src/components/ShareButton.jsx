import { useState } from "react";
import { api } from "../api/client";

export default function ShareButton({ courseId }) {
  const [status, setStatus] = useState("");
  const [busy, setBusy] = useState(false);
  const [analytics, setAnalytics] = useState(null);
  const [open, setOpen] = useState(false);

  async function share() {
    if (!courseId) return;
    setBusy(true);
    setStatus("");
    try {
      const link = await api.shareCourse(courseId);
      const shareUrl = `${window.location.origin}/shared/course/${encodeURIComponent(link.token)}`;
      await navigator.clipboard.writeText(shareUrl);
      setStatus(`Copied. Expires ${new Date(link.expires_at).toLocaleDateString()}`);
      setAnalytics(await api.shareLinks(courseId));
    } catch (error) {
      setStatus(error.message || "Could not create share link");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="share-wrap">
      <button className="btn-outline" onClick={share} disabled={busy}>
        <i className="ti ti-link"></i>
        {busy ? "Sharing..." : "Share"}
      </button>
      <button className="icon-btn" onClick={async () => {
        const nextOpen = !open;
        setOpen(nextOpen);
        if (nextOpen) setAnalytics(await api.shareLinks(courseId));
      }} title="Share analytics">
        <i className="ti ti-chart-bar"></i>
      </button>
      {status && <span className="share-status">{status}</span>}
      {open && analytics && (
        <div className="share-popover">
          <strong>{analytics.total_access_count}</strong>
          <span>Total visits</span>
          <small>{analytics.items.length} active links</small>
        </div>
      )}
    </div>
  );
}
