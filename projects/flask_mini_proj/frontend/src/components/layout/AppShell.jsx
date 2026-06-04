import { useState } from "react";
import { useLocation } from "react-router-dom";
import { Menu } from "lucide-react";
import { cn } from "../../lib/cn";
import DisclaimerBar from "./DisclaimerBar";
import Sidebar from "./Sidebar";

export default function AppShell({ children }) {
  const [mobileOpen, setMobileOpen] = useState(false);
  const { pathname } = useLocation();
  const isChat = pathname === "/chat";

  return (
    <div className="flex h-full min-h-screen">
      <Sidebar mobileOpen={mobileOpen} onClose={() => setMobileOpen(false)} />

      <div className="flex min-h-0 min-h-screen flex-1 flex-col">
        <header className="flex shrink-0 items-center gap-3 border-b border-white/8 bg-navy-deep/80 px-4 py-3 backdrop-blur-xl lg:hidden">
          <button
            type="button"
            onClick={() => setMobileOpen(true)}
            className="rounded-xl p-2 text-slate-300 transition hover:bg-white/10 focus-ring"
            aria-label="פתח תפריט"
          >
            <Menu className="h-6 w-6" />
          </button>
          <span className="text-sm font-semibold tracking-tight text-gradient-brand">
            PTSD Companion
          </span>
        </header>

        <main
          className={cn(
            "flex min-h-0 flex-1 flex-col",
            isChat
              ? "overflow-hidden px-3 py-2 sm:px-5 sm:py-3 md:px-6 lg:px-8"
              : "overflow-x-hidden px-4 py-5 md:px-8 md:py-7 lg:px-10"
          )}
        >
          <DisclaimerBar compact={isChat} />
          <div
            className={cn(
              "flex min-h-0 flex-1 flex-col",
              isChat && "overflow-hidden"
            )}
          >
            {children}
          </div>
        </main>
      </div>
    </div>
  );
}
