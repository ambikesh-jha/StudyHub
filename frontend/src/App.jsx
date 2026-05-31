import { useState } from "react";
import BottomNav from "./components/BottomNav";
import { AuthProvider, useAuth } from "./hooks/useAuth";
import { useOffline } from "./hooks/useOffline";
import Dashboard from "./pages/Dashboard";
import Home from "./pages/Home";
import Login from "./pages/Login";
import Profile from "./pages/Profile";
import SharedCourse from "./pages/SharedCourse";
import "./index.css";

function StudyHubApp() {
  const { booting, isAuthenticated } = useAuth();
  const [activeCourse, setActiveCourse] = useState(null);
  const [view, setView] = useState("home");
  const offline = useOffline();
  const sharedMatch = window.location.pathname.match(/^\/shared\/course\/(.+)$/);

  if (booting) {
    return <div className="boot-screen"><i className="ti ti-loader-2 spin"></i></div>;
  }

  if (sharedMatch) {
    return (
      <>
        {activeCourse ? (
          <Dashboard course={activeCourse} onBack={() => setActiveCourse(null)} />
        ) : (
          <SharedCourse token={decodeURIComponent(sharedMatch[1])} onOpenCourse={setActiveCourse} />
        )}
        {offline && <div className="offline-toast"><i className="ti ti-wifi-off"></i> Offline</div>}
      </>
    );
  }

  if (!isAuthenticated) return <Login />;

  function changeView(next) {
    setActiveCourse(null);
    setView(next);
  }

  return (
    <>
      {activeCourse ? (
        <Dashboard course={activeCourse} onBack={() => setActiveCourse(null)} />
      ) : view === "profile" ? (
        <Profile />
      ) : (
        <Home onOpen={setActiveCourse} onProfile={() => setView("profile")} />
      )}
      <BottomNav view={activeCourse ? "home" : view} onView={changeView} />
      {offline && <div className="offline-toast"><i className="ti ti-wifi-off"></i> Offline</div>}
    </>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <StudyHubApp />
    </AuthProvider>
  );
}
