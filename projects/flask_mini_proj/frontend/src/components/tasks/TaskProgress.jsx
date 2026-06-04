export default function TaskProgress({ done, total }) {
  const pct = total ? Math.round((done / total) * 100) : 0;

  return (
    <div className="glass-panel p-5">
      <div className="mb-2 flex justify-between text-sm">
        <span className="text-slate-300">התקדמות יומית</span>
        <span className="font-medium text-accent-light">
          {done}/{total}
        </span>
      </div>
      <div className="h-2 overflow-hidden rounded-full bg-white/10">
        <div
          className="h-full rounded-full bg-gradient-to-l from-accent to-teal-500 transition-all duration-500"
          style={{ width: `${pct}%` }}
          role="progressbar"
          aria-valuenow={pct}
          aria-valuemin={0}
          aria-valuemax={100}
        />
      </div>
    </div>
  );
}
