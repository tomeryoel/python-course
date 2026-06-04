import { cn } from "../../lib/cn";
import SourcesAccordion from "./SourcesAccordion";

export default function MessageBubble({ role, text, sources }) {
  const isUser = role === "user";

  return (
    <div
      className={cn(
        "animate-fade-in w-full",
        isUser ? "flex justify-end" : "flex justify-start"
      )}
    >
      <div className={cn("max-w-[92%] md:max-w-[85%]", !isUser && "min-w-0")}>
        <div
          className={cn(
            "rounded-2xl px-4 py-3.5 text-sm leading-relaxed md:text-[0.9375rem]",
            isUser
              ? "rounded-br-md bg-gradient-to-l from-accent to-accent-dim text-white shadow-lg shadow-accent/20"
              : "rounded-bl-md border border-white/10 bg-gradient-to-b from-white/[0.1] to-white/[0.04] text-slate-100 shadow-inner-soft"
          )}
        >
          <p className="whitespace-pre-wrap">{text}</p>
        </div>
        {!isUser && sources?.length > 0 && <SourcesAccordion sources={sources} />}
      </div>
    </div>
  );
}
