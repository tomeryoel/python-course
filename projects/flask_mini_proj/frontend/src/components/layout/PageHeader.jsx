export default function PageHeader({ title, subtitle, action }) {
  return (
    <header className="mb-6 md:mb-8">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight text-white md:text-3xl">
            {title}
          </h1>
          {subtitle && (
            <p className="mt-2 max-w-2xl text-sm leading-relaxed text-slate-400 md:text-base">
              {subtitle}
            </p>
          )}
        </div>
        {action}
      </div>
    </header>
  );
}
