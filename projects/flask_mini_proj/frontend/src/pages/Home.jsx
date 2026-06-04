import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Anchor, Footprints, Moon, Pill, Sparkles } from "lucide-react";
import { fetchTasks } from "../api";
import { Card, CardHeader } from "../components/ui/Card";
import Button from "../components/ui/Button";
import PageHeader from "../components/layout/PageHeader";
import { SkeletonCard } from "../components/ui/Skeleton";
import Badge from "../components/ui/Badge";
import { CATEGORY_LABELS } from "../data/examples";

export default function Home() {
  const [tasks, setTasks] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    fetchTasks().then(setTasks).catch(() => setTasks([]));
  }, []);

  const open = tasks?.filter((t) => t.status === "open") || [];
  const anchors = open.slice(0, 3);
  const meds = open.filter((t) => t.category === "medication");
  const sleep = open.filter((t) => t.category === "sleep");
  const grounding = open.find((t) => t.category === "grounding" && t.title.includes("5-4-3"));

  const today = new Date().toLocaleDateString("he-IL", {
    weekday: "long",
    day: "numeric",
    month: "long",
  });

  if (tasks === null) {
    return (
      <>
        <PageHeader title="שלום, ברוך שובך" subtitle="טוען את לוח היום…" />
        <div className="grid gap-4 md:grid-cols-2">
          <SkeletonCard />
          <SkeletonCard />
        </div>
      </>
    );
  }

  return (
    <>
      <PageHeader
        title="שלום, ברוך שובך"
        subtitle={`${today} — היום נתמקד רק במה שחשוב באמת.`}
      />

      <div className="grid gap-5 lg:grid-cols-3">
        <Card className="lg:col-span-2">
          <CardHeader
            title="שלושת העוגנים להיום"
            subtitle="מקסימום 3 משימות עיקריות — השאר מוקפא."
            action={<Anchor className="h-5 w-5 text-accent-light" />}
          />
          <ul className="space-y-3">
            {anchors.map((t) => (
              <li
                key={t.id}
                className="flex items-center gap-3 rounded-xl border border-glass-border bg-black/20 px-4 py-3"
              >
                <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-accent/20 text-sm font-semibold text-accent-light">
                  {anchors.indexOf(t) + 1}
                </span>
                <div>
                  <p className="font-medium text-white">{t.title}</p>
                  <p className="text-xs text-slate-400">{t.description}</p>
                </div>
              </li>
            ))}
          </ul>
          <Badge category="cognitive_load" className="mt-4">
            {CATEGORY_LABELS.cognitive_load}
          </Badge>
        </Card>

        <Card>
          <CardHeader title="תזכורות" subtitle="לפי המסמכים שהועלו" />
          <div className="space-y-3">
            {meds.map((t) => (
              <ReminderRow key={t.id} icon={Pill} label={t.title} meta={t.time || "לפי מסמך"} />
            ))}
            {sleep.map((t) => (
              <ReminderRow key={t.id} icon={Moon} label={t.title} meta={t.time} />
            ))}
            {open.find((t) => t.id === "task_002") && (
              <ReminderRow icon={Footprints} label="הליכה יומית" meta="17:00" />
            )}
          </div>
        </Card>
      </div>

      <Card className="mt-5 overflow-hidden">
        <div className="relative flex flex-col items-center px-6 py-10 text-center md:py-12">
          <div className="pointer-events-none absolute inset-0 bg-gradient-to-b from-accent/10 to-transparent" />
          <Sparkles className="relative mb-3 h-8 w-8 text-accent-light" />
          <p className="relative mb-2 text-lg font-medium text-white">
            מרגיש לחץ או פלאשבק?
          </p>
          <p className="relative mb-6 max-w-md text-sm text-slate-400">
            {grounding?.description || "התחל מתרגיל קרקוע קצר לפי ההנחיות האישיות שלך."}
          </p>
          <Button
            variant="grounding"
            size="lg"
            onClick={() =>
              navigate("/chat", {
                state: { question: "אני בסטרס עכשיו, מה לעשות לפי ההנחיות שלי?" },
              })
            }
          >
            התחל קרקוע 5-4-3-2-1
          </Button>
          <Link
            to="/chat"
            className="relative mt-4 text-sm text-accent-light transition hover:text-white"
          >
            מעבר לשיחה מלאה ←
          </Link>
        </div>
      </Card>
    </>
  );
}

function ReminderRow({ icon: Icon, label, meta }) {
  return (
    <div className="flex items-center gap-3 rounded-lg bg-black/20 px-3 py-2">
      <Icon className="h-4 w-4 shrink-0 text-accent/80" />
      <span className="flex-1 text-sm text-slate-200">{label}</span>
      {meta && <span className="text-xs text-slate-500">{meta}</span>}
    </div>
  );
}
