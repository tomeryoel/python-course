import { useEffect, useState } from "react";
import { ClipboardList } from "lucide-react";
import {
  createTask,
  extractTasks,
  fetchTasks,
  patchTask,
  removeTask,
} from "../api";
import TaskCard from "../components/tasks/TaskCard";
import TaskProgress from "../components/tasks/TaskProgress";
import PageHeader from "../components/layout/PageHeader";
import { Card, CardHeader } from "../components/ui/Card";
import Button from "../components/ui/Button";
import EmptyState from "../components/ui/EmptyState";
import ErrorAlert from "../components/ui/ErrorAlert";
import { SkeletonCard } from "../components/ui/Skeleton";
import { CATEGORY_LABELS } from "../data/examples";
import { toUserMessage } from "../lib/errors";
import { useLocale } from "../context/LocaleContext";
import { cn } from "../lib/cn";

const inputClass = cn(
  "w-full rounded-xl border border-glass-border bg-black/25 px-3 py-2 text-sm text-slate-100",
  "placeholder:text-slate-500 focus-ring"
);

const emptyForm = {
  title: "",
  description: "",
  category: "routine",
  time: "",
  source: "הוספה ידנית",
};

export default function Tasks() {
  const { t } = useLocale();
  const [tasks, setTasks] = useState(null);
  const [error, setError] = useState("");
  const [form, setForm] = useState(emptyForm);
  const [extractText, setExtractText] = useState("");
  const [extractSource, setExtractSource] = useState("סיכום חדש");
  const [loading, setLoading] = useState(false);

  const load = () =>
    fetchTasks()
      .then(setTasks)
      .catch((e) => setError(toUserMessage(e, t)));

  useEffect(() => {
    load();
  }, []);

  const open = tasks?.filter((x) => x.status === "open") || [];
  const done = tasks?.filter((x) => x.status === "done") || [];

  const grouped = open.reduce((acc, task) => {
    const c = task.category || "routine";
    if (!acc[c]) acc[c] = [];
    acc[c].push(task);
    return acc;
  }, {});

  async function toggle(task) {
    await patchTask(task.id, { status: task.status === "done" ? "open" : "done" });
    load();
  }

  async function handleAdd(e) {
    e.preventDefault();
    try {
      await createTask(form);
      setForm(emptyForm);
      load();
    } catch (err) {
      setError(toUserMessage(err, t));
    }
  }

  async function handleDelete(id) {
    if (!confirm("למחוק משימה?")) return;
    await removeTask(id);
    load();
  }

  async function handleExtract(e) {
    e.preventDefault();
    setLoading(true);
    setError("");
    try {
      await extractTasks(extractText, extractSource);
      setExtractText("");
      load();
    } catch (err) {
      setError(toUserMessage(err, t));
    } finally {
      setLoading(false);
    }
  }

  if (tasks === null) {
    return (
      <>
        <PageHeader title="לוח משימות" subtitle="טוען…" />
        <SkeletonCard />
      </>
    );
  }

  return (
    <>
      <PageHeader
        title="לוח משימות"
        subtitle="משימות תפקותיות מהמסמכים — המוח התפקודי שלך"
      />

      <TaskProgress done={done.length} total={tasks.length} />

      {error && <ErrorAlert message={error} className="mb-4" />}

      {tasks.length === 0 ? (
        <EmptyState icon={ClipboardList} title={t("noTasks")} />
      ) : (
        Object.entries(grouped).map(([cat, list]) => (
          <Card key={cat} className="mb-4">
            <CardHeader title={CATEGORY_LABELS[cat] || cat} />
            <div className="space-y-2">
              {list.map((task) => (
                <TaskCard
                  key={task.id}
                  task={task}
                  onToggle={toggle}
                  onDelete={handleDelete}
                />
              ))}
            </div>
          </Card>
        ))
      )}

      <div className="mt-6 grid gap-5 lg:grid-cols-2">
        <Card>
          <CardHeader title="הוסף משימה" />
          <form onSubmit={handleAdd} className="space-y-3">
            <FormField label="כותרת">
              <input
                required
                value={form.title}
                onChange={(e) => setForm({ ...form, title: e.target.value })}
                className={inputClass}
              />
            </FormField>
            <FormField label="תיאור">
              <textarea
                value={form.description}
                onChange={(e) => setForm({ ...form, description: e.target.value })}
                className={cn(inputClass, "min-h-[80px]")}
              />
            </FormField>
            <FormField label="קטגוריה">
              <select
                value={form.category}
                onChange={(e) => setForm({ ...form, category: e.target.value })}
                className={inputClass}
              >
                {Object.entries(CATEGORY_LABELS).map(([k, v]) => (
                  <option key={k} value={k}>
                    {v}
                  </option>
                ))}
              </select>
            </FormField>
            <Button type="submit">הוסף</Button>
          </form>
        </Card>

        <Card>
          <CardHeader title="חילוץ משימות מסיכום" subtitle="Bedrock" />
          <form onSubmit={handleExtract} className="space-y-3">
            <FormField label="שם מקור">
              <input
                value={extractSource}
                onChange={(e) => setExtractSource(e.target.value)}
                className={inputClass}
              />
            </FormField>
            <FormField label="הדבק טקסט סיכום">
              <textarea
                required
                rows={5}
                value={extractText}
                onChange={(e) => setExtractText(e.target.value)}
                className={inputClass}
              />
            </FormField>
            <Button type="submit" disabled={loading}>
              {loading ? "מחלץ…" : "חלץ משימות"}
            </Button>
          </form>
        </Card>
      </div>

    </>
  );
}

function FormField({ label, children }) {
  return (
    <div>
      <label className="mb-1 block text-xs text-slate-500">{label}</label>
      {children}
    </div>
  );
}
