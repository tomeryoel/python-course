import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Activity, Anchor, BarChart3, Footprints, Moon, Phone, Pill, Sparkles } from "lucide-react";
import { fetchStressCheckIn, fetchTasks, fetchWeeklySnapshot, triggerEmergencyCall } from "../api";
import EmergencyContactModal from "../components/tools/EmergencyContactModal";
import { Card, CardHeader } from "../components/ui/Card";
import Button from "../components/ui/Button";
import PageHeader from "../components/layout/PageHeader";
import { SkeletonCard } from "../components/ui/Skeleton";
import Badge from "../components/ui/Badge";
import ErrorAlert from "../components/ui/ErrorAlert";
import { CATEGORY_LABELS } from "../data/examples";

export default function Home() {
  const [tasks, setTasks] = useState(null);
  const [snapshot, setSnapshot] = useState(null);
  const [snapshotLoading, setSnapshotLoading] = useState(false);
  const [snapshotError, setSnapshotError] = useState("");
  const [stressResult, setStressResult] = useState(null);
  const [stressLoading, setStressLoading] = useState(false);
  const [stressError, setStressError] = useState("");
  const [emergencyOpen, setEmergencyOpen] = useState(false);
  const [emergencyLoading, setEmergencyLoading] = useState(false);
  const [emergencyResult, setEmergencyResult] = useState(null);
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

      <div className="mt-5 grid gap-5 md:grid-cols-2 lg:grid-cols-3">
        <Card premium>
          <CardHeader
            title="בדיקת עומס / סטרס"
            subtitle="Lambda tool — Stress Check-in Classifier (demo)"
            action={<Activity className="h-5 w-5 text-teal-300" />}
          />
          {stressError && <ErrorAlert message={stressError} className="mb-3" />}
          {stressResult ? (
            <div className="space-y-2 text-sm text-slate-300">
              <Badge category={stressResult.classification === "crisis" ? "safety" : "grounding"}>
                {stressResult.classification}
              </Badge>
              <p>{stressResult.user_facing_summary}</p>
              <p className="text-2xs text-slate-500">{stressResult.safety_disclaimer}</p>
            </div>
          ) : (
            <p className="text-sm text-slate-400">
              מסווג עומס קוגניטיבי ומחזיר הנחיות ניתוב בטוחות ל-Agent.
            </p>
          )}
          <Button
            variant="secondary"
            size="sm"
            className="mt-4"
            disabled={stressLoading}
            onClick={async () => {
              setStressLoading(true);
              setStressError("");
              try {
                setStressResult(
                  await fetchStressCheckIn({
                    user_message: "אני ממש מוצף ולא מצליח לזכור מה לעשות",
                    self_reported_stress_level: 8,
                    confusion_level: 7,
                    preferred_language: "he",
                  })
                );
              } catch (e) {
                setStressError(e.message);
              } finally {
                setStressLoading(false);
              }
            }}
          >
            {stressLoading ? "מסווג…" : "Stress Check-in (demo)"}
          </Button>
        </Card>

        <Card premium>
          <CardHeader
            title="סיכום שבועי"
            subtitle="Lambda tool — Weekly Wellness Snapshot"
            action={<BarChart3 className="h-5 w-5 text-accent-light" />}
          />
          {snapshotError && <ErrorAlert message={snapshotError} className="mb-3" />}
          {snapshot ? (
            <div className="space-y-2 text-sm text-slate-300">
              <p>{snapshot.week_summary}</p>
              <p className="text-teal-200">{snapshot.encouragement}</p>
              <p className="text-slate-400">
                <strong className="text-slate-200">מיקוד הבא:</strong> {snapshot.next_focus}
              </p>
              <p className="text-2xs text-slate-500">{snapshot.disclaimer}</p>
            </div>
          ) : (
            <p className="text-sm text-slate-400">לחץ ליצירת סיכום מהמשימות שלך.</p>
          )}
          <Button
            variant="secondary"
            size="sm"
            className="mt-4"
            disabled={snapshotLoading}
            onClick={async () => {
              setSnapshotLoading(true);
              setSnapshotError("");
              try {
                setSnapshot(await fetchWeeklySnapshot("he"));
              } catch (e) {
                setSnapshotError(e.message);
              } finally {
                setSnapshotLoading(false);
              }
            }}
          >
            {snapshotLoading ? "מייצר…" : "Generate Weekly Snapshot"}
          </Button>
        </Card>

        <Card className="opacity-90">
          <CardHeader
            title="תמיכה — איש קשר חירום"
            subtitle="אופציונלי / עתידי — Amazon Connect (לא נדרש)"
            action={<Phone className="h-5 w-5 text-amber-300" />}
          />
          <p className="text-sm leading-relaxed text-slate-400">
            הרחבה עתידית בלבד — שיחת תמיכה אוטומטית. לא נדרש להגשה.{" "}
            <strong className="text-amber-200/90">לא שירות חירום רפואי.</strong>
          </p>
          <Button
            variant="danger"
            size="sm"
            className="mt-4"
            onClick={() => {
              setEmergencyResult(null);
              setEmergencyOpen(true);
            }}
          >
            Contact Emergency Support
          </Button>
        </Card>
      </div>

      <EmergencyContactModal
        open={emergencyOpen}
        onClose={() => setEmergencyOpen(false)}
        loading={emergencyLoading}
        result={emergencyResult}
        onConfirm={async () => {
          setEmergencyLoading(true);
          try {
            const res = await triggerEmergencyCall(true, {
              user_display_name: "User",
              trigger_reason: "User confirmed from dashboard",
              language: "he",
            });
            setEmergencyResult(res);
          } catch (e) {
            setEmergencyResult({ result: { error: e.message } });
          } finally {
            setEmergencyLoading(false);
          }
        }}
      />

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
