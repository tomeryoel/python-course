import { NavLink } from "react-router-dom";
import { DISCLAIMER } from "../data/examples";

const links = [
  { to: "/", label: "לוח בקרה" },
  { to: "/chat", label: "שיחה" },
  { to: "/tasks", label: "משימות" },
  { to: "/documents", label: "מסמכים" },
  { to: "/about", label: "אודות" },
];

export default function Layout({ children }) {
  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="logo">PTSD Companion</div>
        <div className="tagline">המוח החיצוני שלך</div>
        <nav>
          {links.map((l) => (
            <NavLink
              key={l.to}
              to={l.to}
              className={({ isActive }) =>
                `nav-link${isActive ? " active" : ""}`
              }
              end={l.to === "/"}
            >
              {l.label}
            </NavLink>
          ))}
        </nav>
      </aside>
      <main className="main-content">
        <div className="disclaimer-bar">{DISCLAIMER}</div>
        {children}
      </main>
    </div>
  );
}
