'use client';

import { useEffect, useMemo, useState } from 'react';
import Link from 'next/link';
import { FileScan, ImagePlus, LoaderCircle, Radar, ShieldQuestion } from 'lucide-react';

import { fetchHistory, fetchSystemStatus, logout, pollResult, submitFile, submitNews } from '@/lib/api';
import { asConfidencePercent, cn } from '@/lib/utils';
import { useAnalysisStore } from '@/store/use-analysis-store';
import { useAuthStore } from '@/store/use-auth-store';
import type { AnalysisMode, HistoryItem } from '@/types/analysis';
import type { SystemStatus } from '@/types/system';
import { AuthCard } from './auth-card';
import { ResultPanel } from './result-panel';

type VisibleMode = Extract<AnalysisMode, 'image' | 'news'>;

const modeMeta = {
  image: {
    icon: ImagePlus,
    title: 'Image Deepfake Lab',
    intro: 'Upload suspicious images and inspect EXIF tags, noise patterns, and generated patches.',
  },
  news: {
    icon: FileScan,
    title: 'News Credibility Desk',
    intro: 'Paste a URL or body text to score rhetorical manipulation and source trust.',
  },
} satisfies Record<VisibleMode, { icon: typeof ImagePlus; title: string; intro: string }>;

const visibleModes: VisibleMode[] = ['image', 'news'];
const visibleModeSet = new Set<AnalysisMode>(visibleModes);

export function AnalysisConsole({ mode }: { mode: AnalysisMode }) {
  const { latestTask, setLatestTask, setMode } = useAnalysisStore();
  const { email, clearSession, hasHydrated } = useAuthStore();
  const [text, setText] = useState('');
  const [url, setUrl] = useState('');
  const [file, setFile] = useState<File | null>(null);
  const [statusNote, setStatusNote] = useState('');
  const [loading, setLoading] = useState(false);
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [systemStatus, setSystemStatus] = useState<SystemStatus | null>(null);

  useEffect(() => {
    setMode(mode);
  }, [mode, setMode]);

  const meta = modeMeta[mode as VisibleMode];

  async function refreshHistory() {
    try {
      const response = await fetchHistory();
      setHistory(response.results.filter((item) => visibleModeSet.has(item.type)).slice(0, 5));
    } catch {
      setHistory([]);
    }
  }

  useEffect(() => {
    if (!hasHydrated) {
      return;
    }
    if (email) {
      void refreshHistory();
      return;
    }
    setHistory([]);
  }, [email, hasHydrated]);

  useEffect(() => {
    async function run() {
      try {
        const response = await fetchSystemStatus();
        setSystemStatus(response);
      } catch {
        setSystemStatus(null);
      }
    }

    void run();
  }, []);

  async function pollUntilDone(taskId: string, signal: AbortSignal) {
    let done = false;
    let delayMs = 900;
    while (!done) {
      if (signal.aborted) return;
      const current = await pollResult(taskId);
      setLatestTask(current);
      setStatusNote(current.current_step);
      if (current.status === 'completed' || current.status === 'failed') {
        done = true;
        void refreshHistory();
      } else {
        await new Promise((resolve) => window.setTimeout(resolve, delayMs));
        delayMs = Math.min(6000, Math.round(delayMs * 1.25 + Math.random() * 180));
      }
    }
  }

  async function handleSubmit() {
    setLoading(true);
    setStatusNote('Preparing secure intake');
    try {
      if (!email) {
        setStatusNote('Sign in before launching an analysis.');
        return;
      }

      let queued;
      if (mode === 'news') {
        queued = await submitNews({ text: text || undefined, url: url || undefined });
      } else {
        if (!file) {
          setStatusNote('Select a file before starting the case.');
          setLoading(false);
          return;
        }
        queued = await submitFile(mode, file);
      }
      setStatusNote(queued.message);
      const controller = new AbortController();
      await pollUntilDone(queued.task_id, controller.signal);
    } catch (error) {
      setStatusNote('The backend could not be reached. Start the API and retry.');
    } finally {
      setLoading(false);
    }
  }

  async function handleSignOut() {
    try {
      await logout();
    } catch {
      // ignore logout errors; we'll clear local state regardless
    }
    clearSession();
    setLatestTask(null);
    setStatusNote('');
    setHistory([]);
  }

  const canSubmit = useMemo(() => {
    if (mode === 'news') {
      return Boolean(text.trim() || url.trim());
    }
    return Boolean(file);
  }, [file, mode, text, url]);

  const activeModeStatus = useMemo(
    () => systemStatus?.model_status.find((item) => item.mode === mode) ?? null,
    [mode, systemStatus],
  );

  if (!hasHydrated) {
    return (
      <section className="px-6 py-12 lg:px-10 lg:py-16">
        <div className="deepglass mx-auto max-w-4xl rounded-docket p-8 text-sm text-paper/66">
          Restoring your session...
        </div>
      </section>
    );
  }

  if (!email) {
    return (
      <section className="px-6 py-12 lg:px-10 lg:py-16">
        <div className="mx-auto max-w-4xl">
          <AuthCard
            title={`Access the ${meta.title}`}
            copy="Use your own account for verification history, task polling, and rate-limited API access. This replaces the old shared demo login."
          />
        </div>
      </section>
    );
  }

  return (
    <section className="px-6 py-12 lg:px-10 lg:py-16">
      <div className="mx-auto grid max-w-7xl gap-8 lg:grid-cols-[0.95fr_1.05fr]">
        <div className="deepglass space-y-6 rounded-docket p-6 text-paper">
          <div className="flex items-start gap-4">
            <span className="flex h-14 w-14 items-center justify-center rounded-full border border-paper/12 bg-paper/6 text-moss">
              <meta.icon className="h-6 w-6" />
            </span>
            <div>
              <p className="font-mono text-xs uppercase tracking-[0.32em] text-paper/42">Active investigation</p>
              <h1 className="mt-2 font-[family-name:var(--font-display)] text-4xl text-paper">{meta.title}</h1>
              <p className="mt-3 max-w-xl text-base leading-8 text-paper/68">{meta.intro}</p>
              <div className="mt-4 flex flex-wrap items-center gap-3 text-xs uppercase tracking-[0.2em] text-paper/44">
                <span>Signed in as {email}</span>
                <button type="button" onClick={handleSignOut} className="rounded-full border border-paper/12 px-3 py-2 text-paper transition hover:border-moss/35 hover:text-moss">
                  Sign out
                </button>
              </div>
            </div>
          </div>

          <div className="grid gap-3 sm:grid-cols-3">
            {visibleModes.map((item) => (
              <Link
                key={item}
                href={`/analyze/${item}`}
                className={cn(
                  'rounded-[1.1rem] border px-4 py-3 text-sm font-semibold uppercase tracking-[0.18em] transition',
                  item === mode ? 'border-paper/18 bg-paper text-soot' : 'border-paper/10 bg-paper/6 text-paper/72 hover:border-moss/30 hover:text-moss',
                )}
              >
                {item}
              </Link>
            ))}
          </div>

          {activeModeStatus ? (
            <div className="rounded-[1.25rem] border border-paper/10 bg-paper/6 p-5">
              <div className="flex items-start justify-between gap-4">
                <div>
                  <p className="font-mono text-xs uppercase tracking-[0.28em] text-paper/42">Active model status</p>
                  <h2 className="mt-2 font-[family-name:var(--font-display)] text-3xl text-paper">{activeModeStatus.model_id}</h2>
                </div>
                <span className="rounded-full border border-moss/18 bg-moss/10 px-3 py-2 text-[11px] font-semibold uppercase tracking-[0.2em] text-moss">
                  {activeModeStatus.source.replaceAll('_', ' ')}
                </span>
              </div>
              <div className="mt-4 grid gap-3 md:grid-cols-2">
                <div className="rounded-[1rem] border border-paper/10 bg-paper/6 px-4 py-3 text-sm text-paper/68">
                  <p className="font-mono text-[11px] uppercase tracking-[0.22em] text-paper/42">Warm-up</p>
                  <p className="mt-1">{activeModeStatus.warmup_on_startup ? 'Enabled on startup' : 'Not enabled for this mode'}</p>
                </div>
                <Link
                  href="/system"
                  className="inline-flex items-center gap-2 rounded-[1rem] border border-paper/10 bg-paper/6 px-4 py-3 text-sm font-semibold uppercase tracking-[0.16em] text-paper transition hover:border-moss/35 hover:text-moss"
                >
                  <Radar className="h-4 w-4" />
                  Open system desk
                </Link>
              </div>
              <div className="mt-4 space-y-2">
                {activeModeStatus.notes.map((note) => (
                  <p key={note} className="text-sm leading-7 text-paper/64">
                    {note}
                  </p>
                ))}
              </div>
            </div>
          ) : null}

          {mode === 'news' ? (
            <div className="space-y-4">
              <label className="block">
                <span className="mb-2 block font-mono text-xs uppercase tracking-[0.28em] text-paper/44">Source URL</span>
                <input
                  value={url}
                  onChange={(event) => setUrl(event.target.value)}
                  placeholder="https://example.com/story"
                  className="w-full rounded-[1rem] border border-paper/10 bg-paper/6 px-4 py-3 text-paper outline-none transition placeholder:text-paper/28 focus:border-moss/40"
                />
              </label>
              <label className="block">
                <span className="mb-2 block font-mono text-xs uppercase tracking-[0.28em] text-paper/44">Article text</span>
                <textarea
                  value={text}
                  onChange={(event) => setText(event.target.value)}
                  placeholder="Paste the headline, article, or suspicious claim here."
                  rows={10}
                  className="w-full rounded-[1rem] border border-paper/10 bg-paper/6 px-4 py-3 text-paper outline-none transition placeholder:text-paper/28 focus:border-moss/40"
                />
              </label>
            </div>
          ) : (
            <label className="flex min-h-56 cursor-pointer flex-col items-center justify-center rounded-[1.4rem] border border-dashed border-paper/18 bg-paper/5 p-6 text-center transition hover:border-moss/35 hover:bg-paper/8">
              <ShieldQuestion className="h-10 w-10 text-moss" />
              <p className="mt-4 font-[family-name:var(--font-display)] text-3xl text-paper">Drop the suspect file here</p>
              <p className="mt-3 max-w-md text-sm leading-7 text-paper/60">Add an evidence sample and route it through the backend analysis contract.</p>
              <input
                type="file"
                className="mt-6 block w-full text-sm text-paper/60 file:mr-4 file:rounded-full file:border-0 file:bg-paper file:px-4 file:py-3 file:font-semibold file:text-soot"
                onChange={(event) => setFile(event.target.files?.[0] ?? null)}
              />
              {file ? <p className="mt-4 font-mono text-xs uppercase tracking-[0.24em] text-moss">Loaded: {file.name}</p> : null}
            </label>
          )}

          <div className="rounded-[1.25rem] border border-paper/10 bg-paper/6 px-5 py-4 text-paper">
            <div className="flex items-center justify-between gap-4">
              <div>
                <p className="font-mono text-xs uppercase tracking-[0.3em] text-paper/45">Case status</p>
                <p className="mt-2 text-sm text-paper/72">{statusNote || 'Awaiting new evidence.'}</p>
              </div>
              {loading ? <LoaderCircle className="h-5 w-5 animate-spin text-paper" /> : null}
            </div>
            {latestTask ? (
              <div className="mt-4">
                <div className="mb-2 flex items-center justify-between text-xs uppercase tracking-[0.22em] text-paper/45">
                  <span>{latestTask.status}</span>
                  <span>{latestTask.progress}%</span>
                </div>
                <div className="h-2 rounded-full bg-paper/10">
                  <div className="h-2 rounded-full bg-moss transition-all" style={{ width: `${latestTask.progress}%` }} />
                </div>
              </div>
            ) : null}
          </div>

          <button
            type="button"
            disabled={!canSubmit || loading}
            onClick={handleSubmit}
            className="inline-flex w-full items-center justify-center rounded-full bg-paper px-6 py-4 text-sm font-semibold uppercase tracking-[0.24em] text-soot transition hover:bg-moss disabled:cursor-not-allowed disabled:bg-paper/25"
          >
            Launch analysis
          </button>
        </div>

        <div className="space-y-6">
          {latestTask?.result ? (
            <ResultPanel result={latestTask.result} />
          ) : (
            <div className="deepglass-soft rounded-docket p-8 text-paper">
              <p className="font-mono text-xs uppercase tracking-[0.3em] text-paper/42">No result yet</p>
              <h2 className="mt-4 font-[family-name:var(--font-display)] text-4xl text-paper">Run a case to populate the forensic board.</h2>
              <p className="mt-4 max-w-2xl text-base leading-8 text-paper/66">
                The UI is wired to the backend queue contract. Once a verification finishes, you will see the verdict, confidence, breakdown signals, and evidence notes here.
              </p>
            </div>
          )}

          <div className="deepglass-soft rounded-docket p-6 text-paper">
            <div className="flex items-center justify-between gap-4">
              <div>
                <p className="font-mono text-xs uppercase tracking-[0.3em] text-paper/42">Recent case log</p>
                <h2 className="mt-2 font-[family-name:var(--font-display)] text-3xl text-paper">Last five investigations</h2>
              </div>
              <Link href="/history" className="text-sm font-semibold uppercase tracking-[0.2em] text-moss">
                Open full log
              </Link>
            </div>
            <div className="mt-5 space-y-3">
              {history.length ? (
                history.map((item) => (
                  <article key={item.request_id} className="flex flex-wrap items-center justify-between gap-3 rounded-[1rem] border border-paper/10 bg-paper/6 px-4 py-3 text-sm text-paper/68">
                    <div>
                      <p className="font-semibold uppercase tracking-[0.16em] text-paper">{item.type}</p>
                      <p className="font-mono text-xs uppercase tracking-[0.18em] text-paper/42">{new Date(item.created_at).toLocaleString()}</p>
                    </div>
                    <div className="text-right">
                      <p className="font-semibold capitalize text-paper">{item.verdict ?? item.status}</p>
                      <p className="font-mono text-xs uppercase tracking-[0.18em] text-paper/42">{item.confidence != null ? `${asConfidencePercent(item.confidence)} model confidence` : item.status}</p>
                    </div>
                  </article>
                ))
              ) : (
                <p className="rounded-[1rem] border border-dashed border-paper/14 bg-paper/4 px-4 py-6 text-sm leading-7 text-paper/58">Once you authenticate and run a case, the latest request history will appear here.</p>
              )}
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
