import { useEffect, useRef, useState } from "react";
import { api } from "../api/client";
import ShareButton from "../components/ShareButton";
import Skeleton from "../components/Skeleton";

const STATUS_CONFIG = {
  todo: { label: "To do", color: "#888", bg: "#f5f5f5" },
  in_progress: { label: "In progress", color: "#854F0B", bg: "#FAEEDA" },
  done: { label: "Done", color: "#0F6E56", bg: "#E1F5EE" },
};

const TYPE_CONFIG = {
  note: { label: "Note", icon: "ti-file-text", bg: "#E6F1FB", color: "#185FA5" },
  code: { label: "Code", icon: "ti-code", bg: "#EEEDFE", color: "#534AB7" },
  image: { label: "Image", icon: "ti-photo", bg: "#FAEEDA", color: "#854F0B" },
  html: { label: "HTML", icon: "ti-brand-html5", bg: "#EAF3DE", color: "#3B6D11" },
  file: { label: "File", icon: "ti-file", bg: "#f5f5f5", color: "#444" },
};

function escapeHtml(value) {
  return value.replace(/[&<>"']/g, char => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    "\"": "&quot;",
    "'": "&#39;",
  }[char]));
}

function highlightCode(value = "") {
  const escaped = escapeHtml(value);
  return escaped
    .replace(/\b(const|let|var|function|return|async|await|if|else|for|while|class|import|from|export|def|try|except|with)\b/g, "<span class=\"tok-keyword\">$1</span>")
    .replace(/(&quot;.*?&quot;|'.*?')/g, "<span class=\"tok-string\">$1</span>")
    .replace(/\b(\d+)\b/g, "<span class=\"tok-number\">$1</span>");
}

export default function Dashboard({ course, onBack }) {
  const [topics, setTopics] = useState([]);
  const [activeTopic, setActiveTopic] = useState(null);
  const [materials, setMaterials] = useState([]);
  const [loadingTopics, setLoadingTopics] = useState(true);
  const [loadingMats, setLoadingMats] = useState(false);
  const [newTopicTitle, setNewTopicTitle] = useState("");
  const [showAddTopic, setShowAddTopic] = useState(false);
  const [search, setSearch] = useState("");
  const [preview, setPreview] = useState(null);
  const [editMat, setEditMat] = useState(null);
  const [showEditor, setShowEditor] = useState(false);
  const [noteForm, setNoteForm] = useState({ title: "", content: "" });
  const [savingNote, setSavingNote] = useState(false);
  const fileInputRef = useRef();

  useEffect(() => { loadTopics(); }, [course.id]);
  useEffect(() => { if (activeTopic) loadMaterials(activeTopic.id); }, [activeTopic?.id]);

  async function loadTopics() {
    setLoadingTopics(true);
    try {
      const nextTopics = await api.getTopics(course.id);
      setTopics(nextTopics);
      setActiveTopic(nextTopics[0] || null);
    } finally {
      setLoadingTopics(false);
    }
  }

  async function loadMaterials(topicId) {
    setLoadingMats(true);
    try { setMaterials(await api.getMaterials(topicId)); }
    finally { setLoadingMats(false); }
  }

  async function addTopic() {
    if (!newTopicTitle.trim()) return;
    const topic = await api.createTopic(course.id, { title: newTopicTitle, position: topics.length, status: "todo" });
    setTopics(prev => [...prev, { ...topic, material_count: 0 }]);
    setNewTopicTitle("");
    setShowAddTopic(false);
    setActiveTopic(topic);
  }

  async function changeTopicStatus(topic, status) {
    const updated = await api.updateTopic(course.id, topic.id, { status });
    setTopics(prev => prev.map(item => item.id === topic.id ? updated : item));
    if (activeTopic?.id === topic.id) setActiveTopic(updated);
  }

  async function deleteTopic(topicId) {
    if (!confirm("Delete this topic and all materials?")) return;
    await api.deleteTopic(course.id, topicId);
    const remaining = topics.filter(topic => topic.id !== topicId);
    setTopics(remaining);
    if (activeTopic?.id === topicId) {
      setActiveTopic(remaining[0] || null);
      setMaterials([]);
    }
  }

  async function saveNote(e) {
    e.preventDefault();
    if (!activeTopic || !noteForm.title.trim()) return;
    setSavingNote(true);
    try {
      if (editMat) {
        const material = await api.updateMaterial(activeTopic.id, editMat.id, {
          title: noteForm.title,
          content: noteForm.content,
          material_type: "note",
        });
        setMaterials(prev => prev.map(item => item.id === material.id ? material : item));
      } else {
        const material = await api.createMaterial(activeTopic.id, {
          title: noteForm.title,
          material_type: "note",
          content: noteForm.content,
        });
        setMaterials(prev => [...prev, material]);
        bumpMaterialCount(1);
      }
      closeEditor();
    } finally {
      setSavingNote(false);
    }
  }

  async function handleUpload(e) {
    const file = e.target.files?.[0];
    if (!file || !activeTopic) return;
    const ext = file.name.split(".").pop().toLowerCase();
    const typeMap = { py: "code", js: "code", ts: "code", html: "html", htm: "html", png: "image", jpg: "image", jpeg: "image", gif: "image", webp: "image" };
    const materialType = typeMap[ext] || "file";
    try {
      const material = await api.uploadFile(activeTopic.id, file.name, materialType, file);
      setMaterials(prev => [...prev, material]);
      bumpMaterialCount(1);
    } catch (err) {
      alert("Upload failed: " + err.message);
    }
    e.target.value = "";
  }

  async function deleteMaterial(material) {
    if (!confirm("Delete this material?")) return;
    await api.deleteMaterial(activeTopic.id, material.id);
    setMaterials(prev => prev.filter(item => item.id !== material.id));
    bumpMaterialCount(-1);
  }

  function bumpMaterialCount(delta) {
    setTopics(prev => prev.map(topic => topic.id === activeTopic.id ? { ...topic, material_count: Math.max(0, (topic.material_count || 0) + delta) } : topic));
  }

  function openEdit(material) {
    setEditMat(material);
    setNoteForm({ title: material.title, content: material.content || "" });
    setShowEditor(true);
  }

  function closeEditor() {
    setShowEditor(false);
    setNoteForm({ title: "", content: "" });
    setEditMat(null);
  }

  const filtered = materials.filter(material =>
    !search || material.title.toLowerCase().includes(search.toLowerCase()) || (material.content || "").toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="dashboard">
      <aside className="dash-sidebar">
        <div className="dash-sidebar-header">
          <button className="back-btn" onClick={onBack}><i className="ti ti-arrow-left"></i></button>
          <div>
            <div className="dash-course-name">{course.title}</div>
            <div className="dash-course-sub">{topics.length} topics</div>
          </div>
        </div>
        <div className="topic-list">
          {loadingTopics ? <Skeleton rows={5} /> : topics.map(topic => {
            const sc = STATUS_CONFIG[topic.status] || STATUS_CONFIG.todo;
            return (
              <div key={topic.id} className={`topic-row ${activeTopic?.id === topic.id ? "active" : ""}`} onClick={() => setActiveTopic(topic)}>
                <span className="topic-dot" style={{ background: sc.color }}></span>
                <span className="topic-row-name">{topic.title}</span>
                <span className="topic-count">{topic.material_count}</span>
                <div className="topic-row-actions">
                  <select value={topic.status} onChange={e => { e.stopPropagation(); changeTopicStatus(topic, e.target.value); }} onClick={e => e.stopPropagation()} className="status-select">
                    {Object.entries(STATUS_CONFIG).map(([key, value]) => <option key={key} value={key}>{value.label}</option>)}
                  </select>
                  <button className="icon-btn-sm danger" onClick={e => { e.stopPropagation(); deleteTopic(topic.id); }}><i className="ti ti-trash"></i></button>
                </div>
              </div>
            );
          })}
        </div>
        {showAddTopic ? (
          <div className="add-topic-form">
            <input autoFocus value={newTopicTitle} onChange={e => setNewTopicTitle(e.target.value)} placeholder="Topic name..." onKeyDown={e => { if (e.key === "Enter") addTopic(); if (e.key === "Escape") setShowAddTopic(false); }} />
            <div className="inline-actions">
              <button className="btn-solid sm" onClick={addTopic}>Add</button>
              <button className="btn-ghost sm" onClick={() => setShowAddTopic(false)}>Cancel</button>
            </div>
          </div>
        ) : (
          <button className="add-topic-btn" onClick={() => setShowAddTopic(true)}><i className="ti ti-plus"></i> Add topic</button>
        )}
      </aside>

      <main className="dash-main">
        {activeTopic ? (
          <>
            <div className="dash-topbar">
              <div className="dash-topbar-left">
                <span className="dash-topic-title">{activeTopic.title}</span>
                <span className="status-badge" style={{ background: STATUS_CONFIG[activeTopic.status]?.bg, color: STATUS_CONFIG[activeTopic.status]?.color }}>
                  {STATUS_CONFIG[activeTopic.status]?.label}
                </span>
              </div>
              <div className="dash-topbar-right">
                <div className="search-wrap"><i className="ti ti-search"></i><input value={search} onChange={e => setSearch(e.target.value)} placeholder="Search materials..." /></div>
                <ShareButton courseId={course.id} />
                <button className="btn-outline" onClick={() => fileInputRef.current.click()}><i className="ti ti-upload"></i> Upload</button>
                <button className="btn-solid" onClick={() => { setShowEditor(true); setEditMat(null); setNoteForm({ title: "", content: "" }); }}><i className="ti ti-plus"></i> New note</button>
                <input ref={fileInputRef} type="file" hidden onChange={handleUpload} />
              </div>
            </div>

            <div className="dash-content">
              {loadingMats ? (
                <Skeleton rows={4} />
              ) : filtered.length === 0 ? (
                <div className="empty-state small">
                  <i className="ti ti-file-off" style={{ fontSize: 36, opacity: 0.2 }}></i>
                  <p>{search ? "No results found" : "No materials yet. Add a note or upload a file."}</p>
                </div>
              ) : (
                <div className="materials-grid">
                  {filtered.map(material => {
                    const tc = TYPE_CONFIG[material.material_type] || TYPE_CONFIG.file;
                    return (
                      <div key={material.id} className="mat-card" onClick={() => setPreview(material)}>
                        <div className="mat-card-actions">
                          {material.material_type === "note" && <button className="icon-btn-sm" onClick={e => { e.stopPropagation(); openEdit(material); }}><i className="ti ti-edit"></i></button>}
                          <button className="icon-btn-sm danger" onClick={e => { e.stopPropagation(); deleteMaterial(material); }}><i className="ti ti-trash"></i></button>
                        </div>
                        <div className="mat-badge" style={{ background: tc.bg, color: tc.color }}>
                          <i className={`ti ${tc.icon}`}></i> {tc.label}
                        </div>
                        <div className="mat-title">{material.title}</div>
                        {material.content && <div className="mat-preview">{material.content.slice(0, 80)}{material.content.length > 80 ? "..." : ""}</div>}
                        <div className="mat-date">{new Date(material.created_at).toLocaleDateString()}</div>
                      </div>
                    );
                  })}
                </div>
              )}

              {showEditor && (
                <div className="editor-panel">
                  <div className="editor-panel-header">
                    <span>{editMat ? "Edit note" : "New note"}</span>
                    <button className="icon-btn" onClick={closeEditor}><i className="ti ti-x"></i></button>
                  </div>
                  <form onSubmit={saveNote}>
                    <input className="editor-title-input" value={noteForm.title} onChange={e => setNoteForm(form => ({ ...form, title: e.target.value }))} placeholder="Note title..." required />
                    <textarea className="editor-body-input" value={noteForm.content} onChange={e => setNoteForm(form => ({ ...form, content: e.target.value }))} placeholder="Write your notes here..." rows={10} />
                    <div className="modal-actions">
                      <button type="button" className="btn-ghost" onClick={closeEditor}>Cancel</button>
                      <button type="submit" className="btn-solid" disabled={savingNote}>{savingNote ? "Saving..." : editMat ? "Update" : "Save note"}</button>
                    </div>
                  </form>
                </div>
              )}
            </div>
          </>
        ) : (
          <div className="empty-state"><i className="ti ti-layout-sidebar" style={{ fontSize: 48, opacity: 0.15 }}></i><p>Select or create a topic to get started.</p></div>
        )}
      </main>

      {preview && (
        <div className="modal-overlay" onClick={() => setPreview(null)}>
          <div className="preview-modal" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <h2>{preview.title}</h2>
              <button className="icon-btn" onClick={() => setPreview(null)}><i className="ti ti-x"></i></button>
            </div>
            <div className="preview-body">
              {preview.material_type === "image" && preview.file_path && <img src={api.uploadUrl(preview.file_path)} alt={preview.title} style={{ maxWidth: "100%", borderRadius: 8 }} />}
              {preview.material_type === "html" && preview.file_path && <iframe src={api.uploadUrl(preview.file_path)} style={{ width: "100%", height: 400, border: "none", borderRadius: 8 }} title={preview.title} />}
              {preview.material_type === "code" && (
                <pre className="preview-code" dangerouslySetInnerHTML={{ __html: highlightCode(preview.content || preview.file_name || "") }} />
              )}
              {(preview.material_type === "note" || preview.material_type === "file") && (
                <pre className="preview-code">{preview.content || preview.file_name || "(No content)"}</pre>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
