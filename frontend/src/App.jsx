import { useState } from "react";
import Home from "./pages/Home";
import Dashboard from "./pages/Dashboard";
import "./index.css";

export default function App() {
  const [activeCourse, setActiveCourse] = useState(null);

  return activeCourse
    ? <Dashboard course={activeCourse} onBack={() => setActiveCourse(null)} />
    : <Home onOpen={setActiveCourse} />;
}
