export default function BottomNav({ view, onView }) {
  return (
    <nav className="bottom-nav">
      <button className={view === "home" ? "active" : ""} onClick={() => onView("home")} title="Courses">
        <i className="ti ti-books"></i>
        <span>Courses</span>
      </button>
      <button className={view === "profile" ? "active" : ""} onClick={() => onView("profile")} title="Profile">
        <i className="ti ti-user-circle"></i>
        <span>Profile</span>
      </button>
    </nav>
  );
}
