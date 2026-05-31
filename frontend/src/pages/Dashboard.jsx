import { useState, useEffect, useRef } from "react";
import { api } from "../api/client";

const STATUS_CONFIG = {
  todo:        { label: "To do",      color: "#888", bg: "#f5f5f5" },
  in_progress: { label: "In progress", color: "#854F0B", bg: "#FAEEDA" },
  done:        { label: "Done",        color: "#0F6E56", bg: "#E1F5EE" },
};

const TYPE_CONFIG = {
  note:  { label: "Note",  icon: "ti-file-text",   bg: "#E6F1FB", color: "#185FA5" },
  code:  { label: "Code",  icon: "ti-code",         bg: "#EEEDFE", color: "#534AB7" },
  image: { label: "Image", icon: "ti-photo",        bg: "#FAEEDA", color: "#854F0B" },
  html:  { label: "HTML",  icon: "ti-brand-html5",  bg: "#EAF3DE", color: "#3B6D11" },
  file:  { label: "File",  icon: "ti-file",         bg: "#f5f5f5", color: "#444" },
};

export default function Dashboard({ course, onBack }) {
  const [topics, setTopics] = useState([]);
  const [activeTopic, setActiveTopic] = useState(null);
  const [materials, setMaterials] = useState([]);
  const [loadingTopics, setLoadingTopics] = useState(true);
  const [loadingMats, setLoadingMats] = useState(false);
  const [newTopicName, setNewTopicName] = useState("");
  const [addingTopic, setAddingTopic] = useState(false);
  const [showAddTopic, setShowAddTopic] = useState(false);
  const [search, setSearch] = useState("");
  const [preview, setPreview] = useState(null);
  const [editMat, setEditMat] = useState(null);
  const [showEditor, setShowEditor] = useState(false);
  const [noteForm, setNoteForm] = useState({ title: "", content: "" });
  const [savingNote, setSavingNote] = useState(false);
  const fileInputRef = useRef();

  useEffect(() => { loadTopics(); }, [course.id]);
  useEffect(() => { if (activeTopic) loadMaterials(activeTopic.id); }, [activeTopic]);

  async function loadTopics() {
    setLoadingTopics(true);
    try {
      const t = await api.getTopics(course.id);
      setTopics(t);
      if (t.length > 0) setActiveTopic(t[0]);
    } finally { setLoadingTopics(false); }
  }

  async function loadMaterials(topicId) {
    setLoadingMats(true);
    try { setMaterials(await api.getMaterials(topicId)); }
    finally { setLoadingMats(false); }
  }

  async function addTopic() {
    if (!newTopicName.trim()) return;
    setAddingTopic(true);
    try {
      const t = await api.createTopic(course.id, { name: newTopicName, order: topics.length });
      setTopics(prev => [...prev, { ...t, material_count: 0 }]);
      setNewTopicName("");
      setShowAddTopic(false);
      setActiveTopic(t);
    } finally { setAddingTopic(false); }
  }

  async function changeTopicStatus(topic, status) {
    const updated = await api.updateTopic(course.id, topic.id, { status });
    setTopics(prev => prev.map(t => t.id === topic.id ? { ...t, status } : t));
    if (activeTopic?.id === topic.id) setActiveTopic(prev => ({ ...prev, status }));
  }

  async function deleteTopic(topicId) {
    if (!confirm("Delete this topic and all materials?")) return;
    await api.deleteTopic(course.id, topicId);
    const remaining = topics.filter(t => t.id !== topicId);
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
        const m = await api.updateMaterial(activeTopic.id, editMat.id, { title: noteForm.title, content: noteForm.content });
        setMaterials(prev => prev.map(x => x.id === m.id ? m : x));
      } else {
        const m = await api.createMaterial(activeTopic.id, { title: noteForm.title, type: "note", content: noteForm.content });
        setMaterials(prev => [...prev, m]);
        setTopics(prev => prev.map(t => t.id === activeTopic.id ? { ...t, material_count: (t.material_count || 0) + 1 } : t));
      }
      setShowEditor(false);
      setNoteForm({ title: "", content: "" });
      setEditMat(null);
    } finally { setSavingNote(false); }
  }

  async function handleUpload(e) {
    const file = e.target.files[0];
    if (!file || !activeTopic) return;
    const ext = file.name.split(".").pop().toLowerCase();
    const typeMap = { py: "code", js: "code", ts: "code", html: "html", htm: "html", png: "image", jpg: "image", jpeg: "image", gif: "image", webp: "image" };
    const type = typeMap[ext] || "file";
    try {
      const m = await api.uploadFile(activeTopic.id, file.name, type, file);
      setMaterials(prev => [...prev, m]);
      setTopics(prev => prev.map(t => t.id === activeTopic.id ? { ...t, material_count: (t.material_count || 0) + 1 } : t));
    } catch(err) { alert("Upload failed: " + err.message); }
    e.target.value = "";
  }

  async function deleteMaterial(mat) {
    if (!confirm("Delete this material?")) return;
    await api.deleteMaterial(activeTopic.id, mat.id);
    setMaterials(prev => prev.filter(m => m.id !== mat.id));
    setTopics(prev => prev.map(t => t.id === activeTopic.id ? { ...t, material_count: Math.max(0, (t.material_count || 1) - 1) } : t));
  }

  function openEdit(mat) {
    setEditMat(mat);
    setNoteForm({ title: mat.title, content: mat.content || "" });
    setShowEditor(true);
  }

  function openPreview(mat) { setPreview(mat); }

  const filtered = materials.filter(m =>
    !search || m.title.toLowerCase().includes(search.toLowerCase()) || (m.content || "").toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="dashboard">
      <div className="dash-sidebar">
        <div className="dash-sidebar-header">
          <button className="back-btn" onClick={onBack}><i className="ti ti-arrow-left"></i></button>
          <div>
            <div className="dash-course-name">{course.name}</div>
            <div className="dash-course-sub">{topics.length} topics</div>
          </div>
        </div>
        <div className="topic-list">
          {loadingTopics ? <div className="list-loading"><i className="ti ti-loader-2 spin"></i></div> :
            topics.map(t => {
              const sc = STATUS_CONFIG[t.status] || STATUS_CONFIG.todo;
              return (
                <div key={t.id} className={`topic-row ${activeTopic?.id === t.id ? "active" : ""}`} onClick={() => setActiveTopic(t)}>
                  <span className="topic-dot" style={{ background: sc.color }}></span>
                  <span className="topic-row-name">{t.name}</span>
                  <span className="topic-count">{t.material_count}</span>
                  <div className="topic-row-actions">
                    <select value={t.status} onChange={e => { e.stopPropagation(); changeTopicStatus(t, e.target.value); }} onClick={e => e.stopPropagation()} className="status-select">
                      {Object.entries(STATUS_CONFIG).map(([k, v]) => <option key={k} value={k}>{v.label}</option>)}
                    </select>
                    <button className="icon-btn-sm danger" onClick={e => { e.stopPropagation(); deleteTopic(t.id); }}><i className="ti ti-trash"></i></button>
                  </div>
                </div>
              );
            })
          }
        </div>
        {showAddTopic ? (
          <div className="add-topic-form">
            <input autoFocus value={newTopicName} onChange={e => setNewTopicName(e.target.value)} placeholder="Topic name..." onKeyDown={e => { if (e.key === "Enter") addTopic(); if (e.key === "Escape") setShowAddTopic(false); }} />
            <div style={{ display: "flex", gap: 6, marginTop: 6 }}>
              <button className="btn-solid sm" onClick={addTopic} disabled={addingTopic}>{addingTopic ? "..." : "Add"}</button>
              <button className="btn-ghost sm" onClick={() => setShowAddTopic(false)}>Cancel</button>
            </div>
          </div>
        ) : (
          <button className="add-topic-btn" onClick={() => setShowAddTopic(true)}><i className="ti ti-plus"></i> Add topic</button>
        )}
      </div>

      <div className="dash-main">
        {activeTopic ? (
          <>
            <div className="dash-topbar">
              <div className="dash-topbar-left">
                <span className="dash-topic-title">{activeTopic.name}</span>
                <span className="status-badge" style={{ background: STATUS_CONFIG[activeTopic.status]?.bg, color: STATUS_CONFIG[activeTopic.status]?.color }}>
                  {STATUS_CONFIG[activeTopic.status]?.label}
                </span>
              </div>
              <div className="dash-topbar-right">
                <div className="search-wrap"><i className="ti ti-search"></i><input value={search} onChange={e => setSearch(e.target.value)} placeholder="Search materials..." /></div>
                <button className="btn-outline" onClick={() => fileInputRef.current.click()}><i className="ti ti-upload"></i> Upload</button>
                <button className="btn-solid" onClick={() => { setShowEditor(true); setEditMat(null); setNoteForm({ title: "", content: "" }); }}><i className="ti ti-plus"></i> New note</button>
                <input ref={fileInputRef} type="file" style={{ display: "none" }} onChange={handleUpload} />
              </div>
            </div>

            <div className="dash-content">
              {loadingMats ? (
                <div className="loading-state"><i className="ti ti-loader-2 spin"></i></div>
              ) : filtered.length === 0 ? (
                <div className="empty-state small">
                  <i className="ti ti-file-off" style={{ fontSize: 36, opacity: 0.2 }}></i>
                  <p>{search ? "No results found" : "No materials yet. Add a note or upload a file."}</p>
                </div>
              ) : (
                <div className="materials-grid">
                  {filtered.map(m => {
                    const tc = TYPE_CONFIG[m.type] || TYPE_CONFIG.file;
                    return (
                      <div key={m.id} className="mat-card" onClick={() => openPreview(m)}>
                        <div className="mat-card-actions">
                          {m.type === "note" && <button className="icon-btn-sm" onClick={e => { e.stopPropagation(); openEdit(m); }}><i className="ti ti-edit"></i></button>}
                          <button className="icon-btn-sm danger" onClick={e => { e.stopPropagation(); deleteMaterial(m); }}><i className="ti ti-trash"></i></button>
                        </div>
                        <div className="mat-badge" style={{ background: tc.bg, color: tc.color }}>
                          <i className={`ti ${tc.icon}`}></i> {tc.label}
                        </div>
                        <div className="mat-title">{m.title}</div>
                        {m.content && <div className="mat-preview">{m.content.slice(0, 80)}{m.content.length > 80 ? "..." : ""}</div>}
                        <div className="mat-date">{new Date(m.created_at).toLocaleDateString()}</div>
                      </div>
                    );
                  })}
                </div>
              )}

              {showEditor && (
                <div className="editor-panel">
                  <div className="editor-panel-header">
                    <span>{editMat ? "Edit note" : "New note"}</span>
                    <button className="icon-btn" onClick={() => { setShowEditor(false); setEditMat(null); }}><i className="ti ti-x"></i></button>
                  </div>
                  <form onSubmit={saveNote}>
                    <input className="editor-title-input" value={noteForm.title} onChange={e => setNoteForm(f => ({...f, title: e.target.value}))} placeholder="Note title..." required />
                    <textarea className="editor-body-input" value={noteForm.content} onChange={e => setNoteForm(f => ({...f, content: e.target.value}))} placeholder="Write your notes here..." rows={10} />
                    <div style={{ display: "flex", justifyContent: "flex-end", gap: 8, marginTop: 12 }}>
                      <button type="button" className="btn-ghost" onClick={() => { setShowEditor(false); setEditMat(null); }}>Cancel</button>
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
      </div>

      {preview && (
        <div className="modal-overlay" onClick={() => setPreview(null)}>
          <div className="preview-modal" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <h2>{preview.title}</h2>
              <div style={{ display: "flex", gap: 8 }}>
                {preview.file_path && (
                  <a href={api.fileUrl(activeTopic.id, preview.id)} target="_blank" rel="noreferrer" className="btn-outline sm"><i className="ti ti-download"></i> Download</a>
                )}
                <button className="icon-btn" onClick={() => setPreview(null)}><i className="ti ti-x"></i></button>
              </div>
            </div>
            <div className="preview-body">
              {preview.type === "image" && <img src={api.fileUrl(activeTopic.id, preview.id)} alt={preview.title} style={{ maxWidth: "100%", borderRadius: 8 }} />}
              {preview.type === "html" && <iframe src={api.fileUrl(activeTopic.id, preview.id)} style={{ width: "100%", height: 400, border: "none", borderRadius: 8 }} title={preview.title} />}
              {(preview.type === "note" || preview.type === "code" || preview.type === "file") && (
                <pre className="preview-code">{preview.content || "(No content)"}</pre>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
