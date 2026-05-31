import { useState, useEffect } from "react";
import { api } from "../api/client";

const COLOR_MAP = {
  purple: { bg: "#EEEDFE", border: "#AFA9EC", text: "#3C3489", dot: "#534AB7" },
  teal:   { bg: "#E1F5EE", border: "#5DCAA5", text: "#085041", dot: "#1D9E75" },
  coral:  { bg: "#FAECE7", border: "#F0997B", text: "#4A1B0C", dot: "#D85A30" },
  blue:   { bg: "#E6F1FB", border: "#85B7EB", text: "#042C53", dot: "#378ADD" },
  amber:  { bg: "#FAEEDA", border: "#EF9F27", text: "#412402", dot: "#BA7517" },
  pink:   { bg: "#FBEAF0", border: "#ED93B1", text: "#4B1528", dot: "#D4537E" },
};

const ICONS = ["ti-book-2", "ti-brain", "ti-robot", "ti-code", "ti-database", "ti-chart-dots", "ti-atom", "ti-infinity"];
const COLORS = Object.keys(COLOR_MAP);

export default function Home({ onOpen }) {
  const [courses, setCourses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [form, setForm] = useState({ name: "", description: "", icon: "ti-book-2", color: "purple" });
  const [saving, setSaving] = useState(false);
  const [deleteId, setDeleteId] = useState(null);

  useEffect(() => { load(); }, []);

  async function load() {
    try { setCourses(await api.getCourses()); }
    catch(e) { console.error(e); }
    finally { setLoading(false); }
  }

  async function handleCreate(e) {
    e.preventDefault();
    if (!form.name.trim()) return;
    setSaving(true);
    try {
      const c = await api.createCourse(form);
      setCourses(prev => [...prev, c]);
      setShowModal(false);
      setForm({ name: "", description: "", icon: "ti-book-2", color: "purple" });
    } catch(e) { alert("Error: " + e.message); }
    finally { setSaving(false); }
  }

  async function handleDelete(e, id) {
    e.stopPropagation();
    if (!confirm("Delete this course and all its content?")) return;
    await api.deleteCourse(id);
    setCourses(prev => prev.filter(c => c.id !== id));
  }

  return (
    <div className="home-page">
      <header className="home-header">
        <div className="header-inner">
          <div className="logo"><i className="ti ti-stack-2"></i> StudyHub</div>
          <button className="btn-new" onClick={() => setShowModal(true)}>
            <i className="ti ti-plus"></i> New Course
          </button>
        </div>
      </header>

      <main className="home-main">
        <div className="home-hero">
          <h1>My Learning Space</h1>
          <p>All your courses, notes, and materials — one place.</p>
        </div>

        {loading ? (
          <div className="loading-state"><i className="ti ti-loader-2 spin"></i> Loading courses...</div>
        ) : courses.length === 0 ? (
          <div className="empty-state">
            <i className="ti ti-books" style={{ fontSize: 48, opacity: 0.2 }}></i>
            <p>No courses yet. Start by adding one!</p>
            <button className="btn-new" onClick={() => setShowModal(true)}>
              <i className="ti ti-plus"></i> Add your first course
            </button>
          </div>
        ) : (
          <div className="courses-grid">
            {courses.map(c => {
              const col = COLOR_MAP[c.color] || COLOR_MAP.purple;
              return (
                <div key={c.id} className="course-card" onClick={() => onOpen(c)}
                  style={{ "--card-bg": col.bg, "--card-border": col.border, "--card-text": col.text, "--card-dot": col.dot }}>
                  <div className="card-top">
                    <div className="course-icon-wrap" style={{ background: col.dot }}>
                      <i className={`ti ${c.icon}`} style={{ color: "#fff", fontSize: 22 }}></i>
                    </div>
                    <button className="card-del-btn" onClick={(e) => handleDelete(e, c.id)} title="Delete">
                      <i className="ti ti-trash"></i>
                    </button>
                  </div>
                  <div className="course-name">{c.name}</div>
                  {c.description && <div className="course-desc">{c.description}</div>}
                  <div className="course-stats">
                    <span><i className="ti ti-layers-subtract"></i> {c.topic_count} topics</span>
                    <span><i className="ti ti-files"></i> {c.material_count} materials</span>
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
              <input value={form.name} onChange={e => setForm(f => ({...f, name: e.target.value}))} placeholder="e.g. LangChain, LangGraph..." required />
              <label>Description</label>
              <input value={form.description} onChange={e => setForm(f => ({...f, description: e.target.value}))} placeholder="What will you learn?" />
              <label>Icon</label>
              <div className="icon-grid">
                {ICONS.map(ic => (
                  <div key={ic} className={`icon-choice ${form.icon === ic ? "selected" : ""}`} onClick={() => setForm(f => ({...f, icon: ic}))}>
                    <i className={`ti ${ic}`}></i>
                  </div>
                ))}
              </div>
              <label>Color</label>
              <div className="color-grid">
                {COLORS.map(cl => (
                  <div key={cl} className={`color-choice ${form.color === cl ? "selected" : ""}`}
                    style={{ background: COLOR_MAP[cl].dot }}
                    onClick={() => setForm(f => ({...f, color: cl}))} />
                ))}
              </div>
              <div className="modal-actions">
                <button type="button" className="btn-ghost" onClick={() => setShowModal(false)}>Cancel</button>
                <button type="submit" className="btn-solid" disabled={saving}>
                  {saving ? "Creating..." : "Create Course"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
