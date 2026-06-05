import { NavLink } from "react-router-dom";
import {
  Brain,
  ClipboardList,
  FileText,
  Home,
  Info,
  MessageCircle,
  X,
} from "lucide-react";
import { cn } from "../../lib/cn";

const links = [
  { to: "/", label: "לוח בקרה", icon: Home, end: true },
  { to: "/chat", label: "שיחה", icon: MessageCircle },
  { to: "/tasks", label: "משימות", icon: ClipboardList },
  { to: "/documents", label: "מסמכים", icon: FileText },
  { to: "/about", label: "אודות", icon: Info },
];

export default function Sidebar({ mobileOpen, onClose }) {
  const nav = (
    <nav className="flex flex-col gap-1.5 p-3" aria-label="ניווט ראשי">
      {links.map(({ to, label, icon: Icon, end }) => (
        <NavLink
          key={to}
          to={to}
          end={end}
          onClick={onClose}
          className={({ isActive }) =>
            cn(
              "group relative flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition-all duration-200",
              "focus-ring",
              isActive
                ? "border border-accent/25 bg-gradient-to-l from-accent/25 to-accent/5 text-white shadow-[inset_0_1px_0_rgba(255,255,255,0.08)]"
                : "border border-transparent text-slate-400 hover:bg-white/[0.06] hover:text-slate-100"
            )
          }
        >
          {({ isActive }) => (
            <>
              {/* active accent bar (RTL → right edge) */}
              <span
                className={cn(
                  "absolute right-0 top-1/2 h-5 w-1 -translate-y-1/2 rounded-l-full bg-accent-light transition-opacity",
                  isActive ? "opacity-100" : "opacity-0"
                )}
                aria-hidden
              />
              <Icon
                className={cn(
                  "h-5 w-5 shrink-0 transition-colors",
                  isActive ? "text-accent-light" : "text-slate-500 group-hover:text-slate-300"
                )}
                strokeWidth={1.75}
              />
              {label}
            </>
          )}
        </NavLink>
      ))}
    </nav>
  );

  return (
    <>
      {/* Desktop sidebar */}
      <aside className="sticky top-0 hidden h-screen lg:flex lg:w-64 lg:flex-col lg:border-l lg:border-white/8 lg:bg-navy-deep/70 lg:backdrop-blur-2xl">
        <div className="flex h-full flex-col px-2 py-5">
          <div className="px-3">
            <Brand />
          </div>
          {nav}
          <footer className="mt-auto px-4 pt-6 text-xs text-slate-500">
            <Brain className="mb-1.5 h-4 w-4 text-accent/60" />
            זיכרון טיפולי מבוסס מסמכים מקומיים
          </footer>
        </div>
      </aside>

      {/* Mobile drawer */}
      <div
        className={cn(
          "fixed inset-0 z-50 lg:hidden",
          mobileOpen ? "pointer-events-auto" : "pointer-events-none"
        )}
        aria-hidden={!mobileOpen}
      >
        <div
          className={cn(
            "absolute inset-0 bg-black/50 backdrop-blur-sm transition-opacity",
            mobileOpen ? "opacity-100" : "opacity-0"
          )}
          onClick={onClose}
        />
        <aside
          className={cn(
            "absolute right-0 top-0 flex h-full w-[min(280px,85vw)] flex-col border-l border-glass-border bg-navy-soft shadow-2xl transition-transform duration-300",
            mobileOpen ? "translate-x-0" : "translate-x-full"
          )}
        >
          <div className="flex items-center justify-between p-4">
            <Brand compact />
            <button
              type="button"
              onClick={onClose}
              className="rounded-lg p-2 text-slate-400 hover:bg-white/10 focus-ring"
              aria-label="סגור תפריט"
            >
              <X className="h-5 w-5" />
            </button>
          </div>
          {nav}
        </aside>
      </div>
    </>
  );
}

function Brand({ compact }) {
  return (
    <div className={cn("mb-6", compact && "mb-0")}>
      <h2 className="text-lg font-bold text-gradient-brand">PTSD Companion</h2>
      {!compact && (
        <p className="mt-1 text-xs text-slate-500">המוח החיצוני שלך</p>
      )}
    </div>
  );
}
