import Link from 'next/link';
import { ArrowRight, Brain, Globe, ImagePlus, Lock, Newspaper, Radar, ShieldCheck, Sparkles, Zap } from 'lucide-react';

const detectionCards = [
  {
    id: 'image',
    title: 'Image Deepfake',
    description: 'Inspect manipulated or AI-generated imagery through provenance, frequency artifacts, metadata anomalies, and detector support signals.',
    href: '/analyze/image',
    icon: ImagePlus,
    accuracy: 'Layered review',
    speed: '< 20 sec',
    accepts: 'PNG, JPG, WEBP',
    models: ['C2PA', 'SDXL detector', 'FFT scan', 'EXIF review'],
  },
  {
    id: 'news',
    title: 'Fake News',
    description: 'Analyze short claims and article text with the fine-tuned RoBERTa classifier, source context, and benchmarked verdict mapping.',
    href: '/analyze/news',
    icon: Newspaper,
    accuracy: 'Benchmarked',
    speed: '< 20 sec',
    accepts: 'URL or text',
    models: ['RoBERTa', 'URL fetch', 'Signal breakdown', 'Case history'],
  },
] as const;

const features = [
  {
    icon: Brain,
    title: 'Neural analysis',
    desc: 'Image and news desks combine model output with forensic context instead of hiding behind a single score.',
  },
  {
    icon: Zap,
    title: 'Real-time workflow',
    desc: 'FastAPI, Redis, and Celery keep verification requests asynchronous while the UI polls progress live.',
  },
  {
    icon: Lock,
    title: 'Secure by design',
    desc: 'JWT auth, CSRF protection, rate limiting, and account-scoped history keep each analyst session isolated.',
  },
  {
    icon: Radar,
    title: 'System desk',
    desc: 'A live status page exposes model registry, warm-up state, datasets, and benchmark expectations without opening Docker logs.',
  },
  {
    icon: ShieldCheck,
    title: 'Evidence first',
    desc: 'C2PA and provenance cues outrank generic classifier output so results read like investigation support, not magic truth.',
  },
  {
    icon: Globe,
    title: 'Extensible API',
    desc: 'The backend already exposes clean verification, history, and runtime endpoints for future integrations.',
  },
] as const;

const stats = [
  { value: '2', label: 'Live Desks', sub: 'Image and news' },
  { value: '< 20s', label: 'Analysis Time', sub: 'Warm request path' },
  { value: '1', label: 'System Desk', sub: 'Runtime visibility' },
  { value: '24/7', label: 'Workflow Ready', sub: 'Anytime local testing' },
] as const;

export default function HomePage() {
  return (
    <div className="relative overflow-hidden">
      <div
        className="pointer-events-none absolute inset-0 bg-cover bg-center bg-no-repeat opacity-55"
        style={{ backgroundImage: "url('/bg-main.png')" }}
      />
      <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_24%_4%,rgba(116,154,255,0.44),transparent_0,transparent_20%,rgba(56,92,244,0.16)_42%,transparent_64%),linear-gradient(180deg,rgba(3,8,23,0.08),rgba(3,8,23,0.54)_42%,rgba(3,8,23,0.9)_100%)]" />
      <div className="pointer-events-none absolute inset-0 scan-line opacity-15" />

      <section className="relative flex min-h-[calc(100vh-73px)] items-center justify-center px-6 py-20 lg:px-10">
        <div className="mx-auto flex w-full max-w-6xl flex-col items-center text-center">
          <div className="inline-flex items-center gap-2 rounded-full border border-[#3261bc] bg-[rgba(29,56,122,0.16)] px-5 py-2 text-[#4c8fff]">
            <Sparkles className="h-4 w-4" />
            <span className="text-sm font-medium">AI-Powered Authenticity Detection</span>
          </div>

          <h1 className="mt-10 max-w-5xl font-[family-name:var(--font-display)] text-6xl font-semibold leading-[0.9] tracking-[-0.07em] text-paper md:text-[7rem]">
            Detect <span className="text-[#4c8fff]">Deepfakes</span>
            <br />
            Before They <span className="text-[#4c8fff]">Spread</span>
          </h1>

          <p className="mt-8 max-w-3xl text-xl leading-10 text-paper/48 md:text-[2rem] md:leading-[1.55]">
            Advanced verification workflows for manipulated images and deceptive news. Protect truth with accountable evidence, live status, and investigation-ready results.
          </p>

          <div className="mt-12 flex flex-col items-center gap-4 sm:flex-row">
            <Link
              href="/analyze/news"
              className="glow-primary inline-flex min-w-[210px] items-center justify-center gap-2 rounded-2xl bg-[#4c8fff] px-8 py-5 text-lg font-semibold text-white transition hover:bg-[#68a0ff]"
            >
              Start Scanning
              <ArrowRight className="h-5 w-5" />
            </Link>
            <Link
              href="/system"
              className="inline-flex min-w-[170px] items-center justify-center rounded-2xl border border-[#2452a8] bg-[rgba(5,17,46,0.45)] px-8 py-5 text-lg font-medium text-[#4c8fff] transition hover:border-[#4c8fff] hover:text-paper"
            >
              View System
            </Link>
          </div>

          <div id="stats" className="mt-24 grid w-full max-w-5xl grid-cols-2 gap-y-8 md:grid-cols-4">
            {stats.map((stat) => (
              <div key={stat.label} className="text-center">
                <p className="text-glow font-[family-name:var(--font-display)] text-4xl font-semibold tracking-[-0.05em] text-[#4c8fff] md:text-5xl">
                  {stat.value}
                </p>
                <p className="mt-2 text-lg font-medium text-paper/62">{stat.label}</p>
                <p className="mt-1 text-sm text-paper/34">{stat.sub}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section id="detection" className="relative px-6 py-24 lg:px-10">
        <div className="mx-auto max-w-5xl">
          <div className="mb-16 text-center">
            <h2 className="font-[family-name:var(--font-display)] text-4xl font-semibold tracking-[-0.05em] text-paper md:text-6xl">
              Investigation <span className="text-glow text-[#4c8fff]">desks</span>
            </h2>
            <p className="mx-auto mt-4 max-w-2xl text-base leading-8 text-paper/54">
              The landing page now looks like the reference, but the buttons still lead into the real product screens and backend-connected workflow.
            </p>
          </div>

          <div className="grid gap-6 md:grid-cols-2">
            {detectionCards.map((type) => (
              <article key={type.id} className="deepglass-soft group rounded-docket p-6 transition duration-300 hover:-translate-y-1 hover:border-[#4c8fff]/40">
                <div className="mb-4 flex items-start gap-4">
                  <div className="rounded-2xl border border-paper/12 bg-paper/6 p-3">
                    <type.icon className="h-6 w-6 text-[#4c8fff]" />
                  </div>
                  <div>
                    <h3 className="font-[family-name:var(--font-display)] text-2xl font-semibold text-paper">{type.title}</h3>
                    <div className="mt-1 flex gap-3">
                      <span className="text-xs font-medium text-[#4c8fff]">{type.accuracy}</span>
                      <span className="text-xs text-paper/42">{type.speed}</span>
                    </div>
                  </div>
                </div>

                <p className="mb-5 text-sm leading-7 text-paper/60">{type.description}</p>

                <div className="mb-5 flex flex-wrap gap-2">
                  {type.models.map((model) => (
                    <span key={model} className="rounded-full border border-paper/10 bg-paper/5 px-3 py-1 text-[11px] uppercase tracking-[0.14em] text-paper/62">
                      {model}
                    </span>
                  ))}
                </div>

                <div className="rounded-[1.35rem] border border-dashed border-paper/14 bg-paper/4 p-6 text-center">
                  <p className="text-sm text-paper/50">Ready for live input</p>
                  <p className="mt-1 text-[11px] uppercase tracking-[0.22em] text-paper/30">{type.accepts}</p>
                </div>

                <Link
                  href={type.href}
                  className="glow-primary mt-5 inline-flex w-full items-center justify-center gap-2 rounded-2xl bg-[#4c8fff] px-6 py-4 text-sm font-semibold uppercase tracking-[0.18em] text-white transition hover:bg-[#68a0ff]"
                >
                  Open desk
                  <ArrowRight className="h-4 w-4" />
                </Link>
              </article>
            ))}
          </div>
        </div>
      </section>

      <section id="features" className="relative border-t border-paper/8 px-6 py-24 lg:px-10">
        <div className="mx-auto max-w-5xl">
          <div className="mb-16 text-center">
            <h2 className="font-[family-name:var(--font-display)] text-4xl font-semibold tracking-[-0.05em] text-paper md:text-6xl">
              Built for <span className="text-glow text-[#4c8fff]">precision</span>
            </h2>
            <p className="mx-auto mt-4 max-w-2xl text-base leading-8 text-paper/54">
              The styling now matches your reference image more closely, while the internals still use the existing DeepGuard frontend and backend logic.
            </p>
          </div>

          <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {features.map((feature) => (
              <article key={feature.title} className="deepglass-soft rounded-docket p-6 transition duration-300 hover:border-[#4c8fff]/34">
                <feature.icon className="h-8 w-8 text-[#4c8fff]" />
                <h3 className="mt-5 text-xl font-semibold text-paper">{feature.title}</h3>
                <p className="mt-3 text-sm leading-7 text-paper/60">{feature.desc}</p>
              </article>
            ))}
          </div>
        </div>
      </section>
    </div>
  );
}
