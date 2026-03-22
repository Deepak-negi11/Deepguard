'use client';

import { useEffect, useMemo, useState } from 'react';
import Link from 'next/link';
import { FileAudio2, FileScan, ImagePlus, LoaderCircle, ShieldQuestion } from 'lucide-react';

import { fetchHistory, logout, pollResult, submitFile, submitNews } from '@/lib/api';
import { cn } from '@/lib/utils';
import { useAnalysisStore } from '@/store/use-analysis-store';
import { useAuthStore } from '@/store/use-auth-store';
import type { AnalysisMode, HistoryItem } from '@/types/analysis';
import { AuthCard } from './auth-card';
import { ResultPanel } from './result-panel';

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
  audio: {
    icon: FileAudio2,
    title: 'Audio Clone Trace',
    intro: 'Run a synthetic voice trace against spectral, cadence, and consistency signals.',
  },
} satisfies Record<AnalysisMode, { icon: typeof ImagePlus; title: string; intro: string }>;

export function AnalysisConsole({ mode }: { mode: AnalysisMode }) {
  const { latestTask, setLatestTask, setMode } = useAnalysisStore();
  const { email, clearSession, hasHydrated } = useAuthStore();
  const [text, setText] = useState('');
  const [url, setUrl] = useState('');
  const [file, setFile] = useState<File | null>(null);
  const [statusNote, setStatusNote] = useState('');
  const [loading, setLoading] = useState(false);
  const [history, setHistory] = useState<HistoryItem[]>([]);

  useEffect(() => {
    setMode(mode);
  }, [mode, setMode]);

  const meta = modeMeta[mode];

  async function refreshHistory() {
    try {
      const response = await fetchHistory();
      setHistory(response.results.slice(0, 5));
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

  if (!hasHydrated) {
    return (
      <section className="px-6 py-12 lg:px-10 lg:py-16">
        <div className="mx-auto max-w-4xl rounded-docket border border-soot/12 bg-white/75 p-8 text-sm text-soot/65 shadow-docket">
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
        <div className="space-y-6 rounded-docket border border-soot/12 bg-white/75 p-6 shadow-docket backdrop-blur">
          <div className="flex items-start gap-4">
            <span className="flex h-14 w-14 items-center justify-center rounded-full border border-ember/20 bg-ember/10 text-ember">
              <meta.icon className="h-6 w-6" />
            </span>
            <div>
              <p className="font-mono text-xs uppercase tracking-[0.32em] text-soot/45">Active investigation</p>
              <h1 className="mt-2 font-[family-name:var(--font-display)] text-4xl text-soot">{meta.title}</h1>
              <p className="mt-3 max-w-xl text-base leading-8 text-soot/70">{meta.intro}</p>
              <div className="mt-4 flex flex-wrap items-center gap-3 text-xs uppercase tracking-[0.2em] text-soot/45">
                <span>Signed in as {email}</span>
                <button type="button" onClick={handleSignOut} className="rounded-full border border-soot/15 px-3 py-2 text-soot transition hover:border-ember/35 hover:text-ember">
                  Sign out
                </button>
              </div>
            </div>
          </div>

          <div className="grid gap-3 sm:grid-cols-3">
            {(['image', 'news', 'audio'] as AnalysisMode[]).map((item) => (
              <Link
                key={item}
                href={`/analyze/${item}`}
                className={cn(
                  'rounded-[1.1rem] border px-4 py-3 text-sm font-semibold uppercase tracking-[0.18em] transition',
                  item === mode ? 'border-soot bg-soot text-paper' : 'border-soot/10 bg-paper/70 text-soot/70 hover:border-ember/30 hover:text-ember',
                )}
              >
                {item}
              </Link>
            ))}
          </div>

          {mode === 'news' ? (
            <div className="space-y-4">
              <label className="block">
                <span className="mb-2 block font-mono text-xs uppercase tracking-[0.28em] text-soot/50">Source URL</span>
                <input
                  value={url}
                  onChange={(event) => setUrl(event.target.value)}
                  placeholder="https://example.com/story"
                  className="w-full rounded-[1rem] border border-soot/10 bg-paper/60 px-4 py-3 outline-none transition focus:border-ember/40"
                />
              </label>
              <label className="block">
                <span className="mb-2 block font-mono text-xs uppercase tracking-[0.28em] text-soot/50">Article text</span>
                <textarea
                  value={text}
                  onChange={(event) => setText(event.target.value)}
                  placeholder="Paste the headline, article, or suspicious claim here."
                  rows={10}
                  className="w-full rounded-[1rem] border border-soot/10 bg-paper/60 px-4 py-3 outline-none transition focus:border-ember/40"
                />
              </label>
            </div>
          ) : (
            <label className="flex min-h-56 cursor-pointer flex-col items-center justify-center rounded-[1.4rem] border border-dashed border-soot/20 bg-paper/55 p-6 text-center transition hover:border-ember/35 hover:bg-paper/85">
              <ShieldQuestion className="h-10 w-10 text-ember" />
              <p className="mt-4 font-[family-name:var(--font-display)] text-3xl text-soot">Drop the suspect file here</p>
              <p className="mt-3 max-w-md text-sm leading-7 text-soot/60">Add a short clip, interview, voicemail, or evidence sample. This prototype reads the file and routes it through the backend analysis contract.</p>
              <input
                type="file"
                className="mt-6 block w-full text-sm text-soot/60 file:mr-4 file:rounded-full file:border-0 file:bg-soot file:px-4 file:py-3 file:font-semibold file:text-paper"
                onChange={(event) => setFile(event.target.files?.[0] ?? null)}
              />
              {file ? <p className="mt-4 font-mono text-xs uppercase tracking-[0.24em] text-moss">Loaded: {file.name}</p> : null}
            </label>
          )}

          <div className="rounded-[1.25rem] border border-soot/10 bg-soot px-5 py-4 text-paper">
            <div className="flex items-center justify-between gap-4">
              <div>
                <p className="font-mono text-xs uppercase tracking-[0.3em] text-paper/55">Case status</p>
                <p className="mt-2 text-sm text-paper/75">{statusNote || 'Awaiting new evidence.'}</p>
              </div>
              {loading ? <LoaderCircle className="h-5 w-5 animate-spin text-paper" /> : null}
            </div>
            {latestTask ? (
              <div className="mt-4">
                <div className="mb-2 flex items-center justify-between text-xs uppercase tracking-[0.22em] text-paper/55">
                  <span>{latestTask.status}</span>
                  <span>{latestTask.progress}%</span>
                </div>
                <div className="h-2 rounded-full bg-paper/10">
                  <div className="h-2 rounded-full bg-ember transition-all" style={{ width: `${latestTask.progress}%` }} />
                </div>
              </div>
            ) : null}
          </div>

          <button
            type="button"
            disabled={!canSubmit || loading}
            onClick={handleSubmit}
            className="inline-flex w-full items-center justify-center rounded-full bg-ember px-6 py-4 text-sm font-semibold uppercase tracking-[0.24em] text-paper transition hover:bg-soot disabled:cursor-not-allowed disabled:bg-soot/25"
          >
            Launch analysis
          </button>
        </div>

        <div className="space-y-6">
          {latestTask?.result ? (
            <ResultPanel result={latestTask.result} />
          ) : (
            <div className="rounded-docket border border-soot/12 bg-white/70 p-8 shadow-docket">
              <p className="font-mono text-xs uppercase tracking-[0.3em] text-soot/50">No result yet</p>
              <h2 className="mt-4 font-[family-name:var(--font-display)] text-4xl text-soot">Run a case to populate the forensic board.</h2>
              <p className="mt-4 max-w-2xl text-base leading-8 text-soot/70">
                The UI is wired to the backend queue contract. Once a verification finishes, you will see the verdict, confidence, breakdown signals, and evidence notes here.
              </p>
            </div>
          )}

          <div className="rounded-docket border border-soot/12 bg-white/75 p-6 shadow-docket">
            <div className="flex items-center justify-between gap-4">
              <div>
                <p className="font-mono text-xs uppercase tracking-[0.3em] text-soot/50">Recent case log</p>
                <h2 className="mt-2 font-[family-name:var(--font-display)] text-3xl text-soot">Last five investigations</h2>
              </div>
              <Link href="/history" className="text-sm font-semibold uppercase tracking-[0.2em] text-ember">
                Open full log
              </Link>
            </div>
            <div className="mt-5 space-y-3">
              {history.length ? (
                history.map((item) => (
                  <article key={item.request_id} className="flex flex-wrap items-center justify-between gap-3 rounded-[1rem] border border-soot/10 bg-paper/75 px-4 py-3 text-sm text-soot/70">
                    <div>
                      <p className="font-semibold uppercase tracking-[0.16em] text-soot">{item.type}</p>
                      <p className="font-mono text-xs uppercase tracking-[0.18em] text-soot/45">{new Date(item.created_at).toLocaleString()}</p>
                    </div>
                    <div className="text-right">
                      <p className="font-semibold capitalize text-soot">{item.verdict ?? item.status}</p>
                      <p className="font-mono text-xs uppercase tracking-[0.18em] text-soot/45">{item.confidence ? `${Math.round(item.confidence * 100)}% confidence` : item.status}</p>
                    </div>
                  </article>
                ))
              ) : (
                <p className="rounded-[1rem] border border-dashed border-soot/15 bg-paper/65 px-4 py-6 text-sm leading-7 text-soot/60">Once you authenticate and run a case, the latest request history will appear here.</p>
              )}
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
