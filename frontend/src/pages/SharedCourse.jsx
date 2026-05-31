import { useEffect, useState } from "react";
import { api } from "../api/client";
import Skeleton from "../components/Skeleton";
import { useAuth } from "../hooks/useAuth";

export default function SharedCourse({ token, onOpenCourse }) {
  const { isAuthenticated } = useAuth();
  const [preview, setPreview] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [enrolling, setEnrolling] = useState(false);

  useEffect(() => {
    let alive = true;
    async function load() {
      setLoading(true);
      setError("");
      try {
        const result = await api.previewSharedCourse(token);
        if (alive) setPreview(result);
      } catch (err) {
        if (alive) setError(err.message || "This share link could not be opened");
      } finally {
        if (alive) setLoading(false);
      }
    }
    load();
    return () => { alive = false; };
  }, [token]);

  async function enroll() {
    if (!preview?.course?.id) return;
    setEnrolling(true);
    setError("");
    try {
      await api.enrollCourse(preview.course.id);
      const refreshed = await api.previewSharedCourse(token);
      setPreview(refreshed);
    } catch (err) {
      setError(err.message || "Could not enroll in this course");
    } finally {
      setEnrolling(false);
    }
  }

  if (loading) {
    return <main className="shared-page"><Skeleton rows={5} /></main>;
  }

  if (error || !preview) {
    return (
      <main className="shared-page">
        <div className="empty-state">
          <i className="ti ti-link-off" style={{ fontSize: 48, opacity: 0.2 }}></i>
          <p>{error || "This share link is unavailable."}</p>
        </div>
      </main>
    );
  }

  const course = preview.course;

  return (
    <main className="shared-page">
      <header className="shared-header">
        <div>
          <div className="shared-kicker"><i className="ti ti-link"></i> Shared course</div>
          <h1>{course.title}</h1>
          {course.description && <p>{course.description}</p>}
        </div>
        <div className="shared-actions">
          {preview.can_enroll && (
            <button className="btn-solid" onClick={enroll} disabled={enrolling}>
              <i className="ti ti-user-plus"></i>
              {enrolling ? "Joining..." : "Enroll"}
            </button>
          )}
          {(preview.is_enrolled || course.is_enrolled) && (
            <button className="btn-outline" onClick={() => onOpenCourse(course)}>
              <i className="ti ti-arrow-right"></i>
              Open
            </button>
          )}
          {!isAuthenticated && <span className="share-status">Log in to enroll and save progress.</span>}
        </div>
      </header>

      <section className="shared-topic-list">
        {preview.topics.length === 0 ? (
          <div className="empty-state small">No topics have been added yet.</div>
        ) : preview.topics.map(topic => (
          <article className="shared-topic" key={topic.id}>
            <span>{topic.position + 1}</span>
            <div>
              <h2>{topic.title}</h2>
              <p>{topic.material_count} materials</p>
            </div>
          </article>
        ))}
      </section>
    </main>
  );
}
