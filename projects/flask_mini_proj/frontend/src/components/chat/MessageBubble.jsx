import { cn } from "../../lib/cn";
import SourcesAccordion from "./SourcesAccordion";

export default function MessageBubble({ role, text, sources }) {
  const isUser = role === "user";

  return (
    <div
      className={cn(
        "animate-fade-in max-w-[92%] md:max-w-[78%]",
        isUser ? "self-end" : "self-start"
      )}
    >
      <div
        className={cn(
          "rounded-2xl px-4 py-3 text-sm leading-relaxed md:text-[0.95rem]",
          isUser
            ? "rounded-br-md bg-gradient-to-l from-accent to-accent-muted text-white shadow-md"
            : "rounded-bl-md border border-glass-border bg-glass-strong text-slate-100"
        )}
      >
        <p className="whitespace-pre-wrap">{text}</p>
      </div>
      {!isUser && sources?.length > 0 && <SourcesAccordion sources={sources} />}
    </div>
  );
}
