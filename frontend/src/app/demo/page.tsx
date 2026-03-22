import Link from 'next/link';
import { ArrowUpRight, AudioLines, Database, ImagePlus, Newspaper, ShieldCheck, Workflow } from 'lucide-react';

type DemoDatasetEntry = {
  key: string;
  display_name: string;
  category: string;
  source_url: string;
  access: string;
  notes: string[];
};

type DemoSourceLink = {
  label: string;
  category: 'news' | 'image' | 'audio' | 'general';
  url: string;
  purpose: string;
};

type SystemStatusResponse = {
  app_name: string;
  environment: string;
  supported_modes: Array<'image' | 'news' | 'audio'>;
  demo_analyzers_enabled: boolean;
  celery_workers_enabled: boolean;
  upload_storage: string;
  news_url_fetch_enabled: boolean;
  datasets: DemoDatasetEntry[];
  sample_sources: DemoSourceLink[];
};

const iconByMode = {
  image: ImagePlus,
  news: Newspaper,
  audio: AudioLines,
} as const;

async function getSystemStatus(): Promise<SystemStatusResponse | null> {
  const baseUrl = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000/api/v1';

  try {
    const response = await fetch(`${baseUrl}/system/status`, {
      cache: 'no-store',
    });
    if (!response.ok) {
      return null;
    }
    return (await response.json()) as SystemStatusResponse;
  } catch {
    return null;
  }
}

export default async function DemoPage() {
  const status = await getSystemStatus();

  return (
    <section className="px-6 py-12 lg:px-10 lg:py-16">
      <div className="mx-auto max-w-7xl space-y-8">
        <div className="rounded-docket border border-soot/12 bg-white/80 p-8 shadow-docket">
          <p className="font-mono text-xs uppercase tracking-[0.3em] text-soot/50">Teacher demo board</p>
          <h1 className="mt-4 max-w-4xl font-[family-name:var(--font-display)] text-5xl text-soot">
            One page that explains what DeepGuard does, what is real in the backend, and what data you can demo safely.
          </h1>
          <p className="mt-4 max-w-3xl text-base leading-8 text-soot/72">
            Use this page before the live workflow. It gives a clean explanation of the system status, supported modes, and sample sources so you do not need to explain everything from memory.
          </p>
          <div className="mt-6 flex flex-col gap-3 sm:flex-row">
            <Link href="/analyze/news" className="inline-flex items-center justify-center gap-2 rounded-full bg-soot px-6 py-4 text-sm font-semibold uppercase tracking-[0.24em] text-paper transition hover:bg-ember">
              Start news demo
              <ArrowUpRight className="h-4 w-4" />
            </Link>
            <Link href="/analyze/image" className="inline-flex items-center justify-center gap-2 rounded-full border border-soot/15 bg-paper px-6 py-4 text-sm font-semibold uppercase tracking-[0.24em] text-soot transition hover:border-ember/35 hover:text-ember">
              Start image demo
              <ArrowUpRight className="h-4 w-4" />
            </Link>
          </div>
        </div>

        {status ? (
          <>
            <div className="grid gap-5 lg:grid-cols-4">
              <article className="rounded-[1.3rem] border border-soot/10 bg-paper/75 p-5">
                <ShieldCheck className="h-5 w-5 text-moss" />
                <p className="mt-3 text-sm text-soot/60">Backend mode</p>
                <p className="font-[family-name:var(--font-display)] text-3xl text-soot">
                  {status.demo_analyzers_enabled ? 'Prototype' : 'ML mode'}
                </p>
              </article>
              <article className="rounded-[1.3rem] border border-soot/10 bg-paper/75 p-5">
                <Workflow className="h-5 w-5 text-ember" />
                <p className="mt-3 text-sm text-soot/60">Async execution</p>
                <p className="font-[family-name:var(--font-display)] text-3xl text-soot">
                  {status.celery_workers_enabled ? 'Celery' : 'Background'}
                </p>
              </article>
              <article className="rounded-[1.3rem] border border-soot/10 bg-paper/75 p-5">
                <Database className="h-5 w-5 text-ember" />
                <p className="mt-3 text-sm text-soot/60">Upload storage</p>
                <p className="font-[family-name:var(--font-display)] text-3xl text-soot">{status.upload_storage}</p>
              </article>
              <article className="rounded-[1.3rem] border border-soot/10 bg-paper/75 p-5">
                <Newspaper className="h-5 w-5 text-ember" />
                <p className="mt-3 text-sm text-soot/60">URL article fetch</p>
                <p className="font-[family-name:var(--font-display)] text-3xl text-soot">
                  {status.news_url_fetch_enabled ? 'Enabled' : 'Off'}
                </p>
              </article>
            </div>

            <div className="grid gap-8 lg:grid-cols-[0.95fr_1.05fr]">
              <div className="rounded-docket border border-soot/12 bg-white/80 p-6 shadow-docket">
                <p className="font-mono text-xs uppercase tracking-[0.3em] text-soot/50">Supported modes</p>
                <div className="mt-5 grid gap-4 md:grid-cols-3">
                  {status.supported_modes.map((mode) => {
                    const Icon = iconByMode[mode];
                    return (
                      <article key={mode} className="rounded-[1.2rem] border border-soot/10 bg-paper/75 p-5 text-soot">
                        <Icon className="h-5 w-5 text-ember" />
                        <p className="mt-4 font-[family-name:var(--font-display)] text-3xl capitalize">{mode}</p>
                        <p className="mt-2 text-sm leading-7 text-soot/68">
                          {mode === 'image' && 'Best for AI-generated or edited still-image samples.'}
                          {mode === 'news' && 'Best for the strongest classroom demo because links and pasted text both work.'}
                          {mode === 'audio' && 'Best when you already have clearly labeled real and synthetic voice clips.'}
                        </p>
                      </article>
                    );
                  })}
                </div>
              </div>

              <div className="rounded-docket border border-soot/12 bg-soot p-6 text-paper shadow-docket">
                <p className="font-mono text-xs uppercase tracking-[0.3em] text-paper/55">What to say</p>
                <div className="mt-5 space-y-3 text-sm leading-7 text-paper/78">
                  <p>This project is a working full-stack verification prototype with authentication, file intake, background analysis, result polling, and stored case history.</p>
                  <p>The backend flow is real. The detection layer is prototype-first unless trained model weights are installed and demo mode is turned off.</p>
                  <p>For the clearest demo, show one news case, one image case, and then open the history log to prove persistence.</p>
                </div>
              </div>
            </div>

            <div className="grid gap-8 lg:grid-cols-[1.05fr_0.95fr]">
              <div className="rounded-docket border border-soot/12 bg-white/80 p-6 shadow-docket">
                <p className="font-mono text-xs uppercase tracking-[0.3em] text-soot/50">Dataset registry</p>
                <div className="mt-5 space-y-4">
                  {status.datasets.map((dataset) => (
                    <article key={dataset.key} className="rounded-[1.2rem] border border-soot/10 bg-paper/75 p-5">
                      <div className="flex flex-wrap items-start justify-between gap-3">
                        <div>
                          <h2 className="font-[family-name:var(--font-display)] text-3xl text-soot">{dataset.display_name}</h2>
                          <p className="mt-2 text-xs uppercase tracking-[0.22em] text-soot/45">
                            {dataset.category} · {dataset.access}
                          </p>
                        </div>
                        <a
                          href={dataset.source_url}
                          target="_blank"
                          rel="noreferrer"
                          className="inline-flex items-center gap-2 rounded-full border border-soot/12 px-4 py-2 text-xs font-semibold uppercase tracking-[0.2em] text-soot transition hover:border-ember/35 hover:text-ember"
                        >
                          Open source
                          <ArrowUpRight className="h-3.5 w-3.5" />
                        </a>
                      </div>
                      <div className="mt-4 space-y-2 text-sm leading-7 text-soot/72">
                        {dataset.notes.map((note) => (
                          <p key={note}>{note}</p>
                        ))}
                      </div>
                    </article>
                  ))}
                </div>
              </div>

              <div className="rounded-docket border border-soot/12 bg-white/80 p-6 shadow-docket">
                <p className="font-mono text-xs uppercase tracking-[0.3em] text-soot/50">Quick demo sources</p>
                <div className="mt-5 space-y-4">
                  {status.sample_sources.map((source) => (
                    <article key={source.url} className="rounded-[1.2rem] border border-soot/10 bg-paper/75 p-5">
                      <div className="flex flex-wrap items-start justify-between gap-3">
                        <div>
                          <h2 className="font-[family-name:var(--font-display)] text-2xl text-soot">{source.label}</h2>
                          <p className="mt-2 text-xs uppercase tracking-[0.22em] text-soot/45">{source.category}</p>
                        </div>
                        <a
                          href={source.url}
                          target="_blank"
                          rel="noreferrer"
                          className="inline-flex items-center gap-2 rounded-full border border-soot/12 px-4 py-2 text-xs font-semibold uppercase tracking-[0.2em] text-soot transition hover:border-ember/35 hover:text-ember"
                        >
                          Open
                          <ArrowUpRight className="h-3.5 w-3.5" />
                        </a>
                      </div>
                      <p className="mt-4 text-sm leading-7 text-soot/72">{source.purpose}</p>
                    </article>
                  ))}
                </div>
              </div>
            </div>
          </>
        ) : (
          <div className="rounded-docket border border-dashed border-soot/15 bg-paper/70 p-8 text-soot/70 shadow-docket">
            <p className="font-mono text-xs uppercase tracking-[0.3em] text-soot/45">Backend offline</p>
            <h2 className="mt-4 font-[family-name:var(--font-display)] text-4xl text-soot">Start the backend to populate the teacher demo board.</h2>
            <p className="mt-4 max-w-3xl text-base leading-8">
              Once the API is running, this page will show the live system status, supported modes, dataset registry, and curated source links for your presentation.
            </p>
          </div>
        )}
      </div>
    </section>
  );
}
