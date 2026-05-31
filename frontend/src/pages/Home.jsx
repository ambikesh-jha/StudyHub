import { useEffect, useState } from "react";
import { api } from "../api/client";
import Skeleton from "../components/Skeleton";
import { useAuth } from "../hooks/useAuth";

const COLOR_MAP = {
  purple: { bg: "#EEEDFE", border: "#AFA9EC", text: "#3C3489", dot: "#534AB7" },
  teal: { bg: "#E1F5EE", border: "#5DCAA5", text: "#085041", dot: "#1D9E75" },
  coral: { bg: "#FAECE7", border: "#F0997B", text: "#4A1B0C", dot: "#D85A30" },
  blue: { bg: "#E6F1FB", border: "#85B7EB", text: "#042C53", dot: "#378ADD" },
  amber: { bg: "#FAEEDA", border: "#EF9F27", text: "#412402", dot: "#BA7517" },
  pink: { bg: "#FBEAF0", border: "#ED93B1", text: "#4B1528", dot: "#D4537E" },
};

const ICONS = ["ti-book-2", "ti-brain", "ti-robot", "ti-code", "ti-database", "ti-chart-dots", "ti-atom", "ti-infinity"];
const COLORS = Object.keys(COLOR_MAP);

function iconClass(icon) {
  return icon?.startsWith("ti-") ? icon : `ti-${icon || "book-2"}`;
}

export default function Home({ onOpen, onProfile }) {
  const { user } = useAuth();
  const [courses, setCourses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [form, setForm] = useState({ title: "", description: "", icon: "ti-book-2", color: "purple", is_published: false });
  const [saving, setSaving] = useState(false);

  useEffect(() => { load(); }, []);

  async function load() {
    setLoading(true);
    try { setCourses(await api.getCourses()); }
    catch (e) { console.error(e); }
    finally { setLoading(false); }
  }

  async function handleCreate(e) {
    e.preventDefault();
    if (!form.title.trim()) return;
    setSaving(true);
    try {
      const course = await api.createCourse(form);
      setCourses(prev => [...prev, course]);
      setShowModal(false);
      setForm({ title: "", description: "", icon: "ti-book-2", color: "purple", is_published: false });
    } catch (e) {
      alert("Error: " + e.message);
    } finally {
      setSaving(false);
    }
  }

  async function handleDelete(e, id) {
    e.stopPropagation();
    if (!confirm("Delete this course and all its content?")) return;
    await api.deleteCourse(id);
    setCourses(prev => prev.filter(course => course.id !== id));
  }

  return (
    <div className="home-page">
      <header className="home-header">
        <div className="header-inner">
          <div className="logo"><i className="ti ti-stack-2"></i> StudyHub</div>
          <div className="header-actions">
            <button className="profile-chip" onClick={onProfile}>
              <i className="ti ti-user-circle"></i>
              <span>{user?.display_name || "Profile"}</span>
            </button>
            <button className="btn-new" onClick={() => setShowModal(true)}>
              <i className="ti ti-plus"></i> New Course
            </button>
          </div>
        </div>
      </header>

      <main className="home-main">
        <div className="home-hero">
          <h1>My Learning Space</h1>
          <p>All your courses, notes, and materials in one place.</p>
        </div>

        {loading ? (
          <Skeleton rows={4} />
        ) : courses.length === 0 ? (
          <div className="empty-state">
            <i className="ti ti-books" style={{ fontSize: 48, opacity: 0.2 }}></i>
            <p>No courses yet. Start by adding one.</p>
            <button className="btn-new" onClick={() => setShowModal(true)}>
              <i className="ti ti-plus"></i> Add your first course
            </button>
          </div>
        ) : (
          <div className="courses-grid">
            {courses.map(course => {
              const col = COLOR_MAP[course.color] || COLOR_MAP.purple;
              return (
                <div
                  key={course.id}
                  className="course-card"
                  onClick={() => onOpen(course)}
                  style={{ "--card-bg": col.bg, "--card-border": col.border, "--card-text": col.text, "--card-dot": col.dot }}
                >
                  <div className="card-top">
                    <div className="course-icon-wrap" style={{ background: col.dot }}>
                      <i className={`ti ${iconClass(course.icon)}`} style={{ color: "#fff", fontSize: 22 }}></i>
                    </div>
                    <button className="card-del-btn" onClick={(e) => handleDelete(e, course.id)} title="Delete">
                      <i className="ti ti-trash"></i>
                    </button>
                  </div>
                  <div className="course-name">{course.title}</div>
                  {course.description && <div className="course-desc">{course.description}</div>}
                  <div className="course-stats">
                    <span><i className="ti ti-layers-subtract"></i> {course.topic_count} topics</span>
                    <span><i className="ti ti-files"></i> {course.material_count} materials</span>
                  </div>
                  <div className="card-open">Open <i className="ti ti-arrow-right"></i></div>
                </div>
              );
            })}
            <div className="course-card add-card" onClick={() => setShowModal(true)}>
              <i className="ti ti-plus" style={{ fontSize: 28, opacity: 0.3 }}></i>
              <span>New Course</span>
            </div>
          </div>
        )}
      </main>

      {showModal && (
        <div className="modal-overlay" onClick={() => setShowModal(false)}>
          <div className="modal" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <h2>New Course</h2>
              <button className="icon-btn" onClick={() => setShowModal(false)}><i className="ti ti-x"></i></button>
            </div>
            <form onSubmit={handleCreate}>
              <label>Name *</label>
              <input value={form.title} onChange={e => setForm(f => ({ ...f, title: e.target.value }))} placeholder="e.g. LangChain, LangGraph..." required />
              <label>Description</label>
              <input value={form.description} onChange={e => setForm(f => ({ ...f, description: e.target.value }))} placeholder="What will you learn?" />
              <label className="check-row">
                <input type="checkbox" checked={form.is_published} onChange={e => setForm(f => ({ ...f, is_published: e.target.checked }))} />
                <span>Visible to enrolled learners</span>
              </label>
              <label>Icon</label>
              <div className="icon-grid">
                {ICONS.map(icon => (
                  <div key={icon} className={`icon-choice ${form.icon === icon ? "selected" : ""}`} onClick={() => setForm(f => ({ ...f, icon }))}>
                    <i className={`ti ${icon}`}></i>
                  </div>
                ))}
              </div>
              <label>Color</label>
              <div className="color-grid">
                {COLORS.map(color => (
                  <div
                    key={color}
                    className={`color-choice ${form.color === color ? "selected" : ""}`}
                    style={{ background: COLOR_MAP[color].dot }}
                    onClick={() => setForm(f => ({ ...f, color }))}
                  />
                ))}
              </div>
              <div className="modal-actions">
                <button type="button" className="btn-ghost" onClick={() => setShowModal(false)}>Cancel</button>
                <button type="submit" className="btn-solid" disabled={saving}>{saving ? "Creating..." : "Create Course"}</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
