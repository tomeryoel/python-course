import { useState } from "react";
import { Menu } from "lucide-react";
import DisclaimerBar from "./DisclaimerBar";
import Sidebar from "./Sidebar";

export default function AppShell({ children }) {
  const [mobileOpen, setMobileOpen] = useState(false);

  return (
    <div className="flex min-h-screen">
      <Sidebar mobileOpen={mobileOpen} onClose={() => setMobileOpen(false)} />

      <div className="flex min-h-screen flex-1 flex-col">
        <header className="flex items-center gap-3 border-b border-glass-border bg-navy/50 px-4 py-3 backdrop-blur-md lg:hidden">
          <button
            type="button"
            onClick={() => setMobileOpen(true)}
            className="rounded-xl p-2 text-slate-300 hover:bg-white/10 focus-ring"
            aria-label="פתח תפריט"
          >
            <Menu className="h-6 w-6" />
          </button>
          <span className="text-sm font-semibold text-gradient-brand">PTSD Companion</span>
        </header>

        <main className="flex-1 overflow-x-hidden px-4 py-5 md:px-8 md:py-7 lg:px-10">
          <DisclaimerBar />
          {children}
        </main>
      </div>
    </div>
  );
}
