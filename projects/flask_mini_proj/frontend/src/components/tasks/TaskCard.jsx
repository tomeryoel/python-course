import { Check, Clock, Trash2 } from "lucide-react";
import { CATEGORY_LABELS } from "../../data/examples";
import Badge from "../ui/Badge";
import Button from "../ui/Button";
import { cn } from "../../lib/cn";

export default function TaskCard({ task, onToggle, onDelete }) {
  const done = task.status === "done";

  return (
    <article
      className={cn(
        "group flex gap-3 rounded-xl border p-4 transition-all duration-200",
        done
          ? "border-white/5 bg-black/15 opacity-60"
          : "border-glass-border bg-black/20 hover:border-accent/25 hover:bg-black/30"
      )}
    >
      <button
        type="button"
        onClick={() => onToggle(task)}
        aria-label={done ? "סמן כפתוח" : "סמן כהושלם"}
        className={cn(
          "mt-0.5 flex h-6 w-6 shrink-0 items-center justify-center rounded-lg border transition-colors focus-ring",
          done
            ? "border-accent/50 bg-accent/30 text-white"
            : "border-slate-500 hover:border-accent"
        )}
      >
        {done && <Check className="h-4 w-4" />}
      </button>

      <div className="min-w-0 flex-1">
        <div className="flex flex-wrap items-center gap-2">
          <h4 className={cn("font-medium text-white", done && "line-through")}>
            {task.title}
          </h4>
          <Badge category={task.category}>
            {CATEGORY_LABELS[task.category] || task.category}
          </Badge>
        </div>
        <p className="mt-1 text-sm leading-relaxed text-slate-400">{task.description}</p>
        <div className="mt-2 flex flex-wrap gap-2 text-xs text-slate-500">
          {task.time && (
            <span className="inline-flex items-center gap-1">
              <Clock className="h-3 w-3" />
              {task.time}
            </span>
          )}
          <span>{task.source}</span>
        </div>
        {task.safety_note && (
          <p className="mt-2 text-xs text-amber-200/90">{task.safety_note}</p>
        )}
      </div>

      <Button
        variant="ghost"
        size="sm"
        onClick={() => onDelete(task.id)}
        className="opacity-0 transition-opacity group-hover:opacity-100 md:opacity-100"
        aria-label="מחק משימה"
      >
        <Trash2 className="h-4 w-4" />
      </Button>
    </article>
  );
}
