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
    title: 'Neural Analysis',
    desc: 'Image and news desks combine model output with forensic context instead of hiding behind a single score.',
  },
  {
    icon: Zap,
    title: 'Real-time Workflow',
    desc: 'FastAPI, Redis, and Celery keep verification requests asynchronous while the UI polls progress live.',
  },
  {
    icon: Lock,
    title: 'Secure by Design',
    desc: 'JWT auth, CSRF protection, rate limiting, and account-scoped history keep each analyst session isolated.',
  },
  {
    icon: Radar,
    title: 'System Desk',
    desc: 'A live status page exposes model registry, warm-up state, datasets, and benchmark expectations without opening Docker logs.',
  },
  {
    icon: ShieldCheck,
    title: 'Evidence First',
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
  { value: '<20s', label: 'Analysis Time', sub: 'Warm request path' },
  { value: '1', label: 'System Desk', sub: 'Runtime visibility' },
  { value: '24/7', label: 'Workflow Ready', sub: 'Anytime local testing' },
] as const;

export default function HomePage() {
  return (
    <div className="relative overflow-hidden">

      {/* ─── Hero ─── */}
      <section className="relative flex min-h-[calc(100vh-73px)] items-center justify-center px-6 py-20 lg:px-10">
        <div className="mx-auto flex w-full max-w-6xl flex-col items-center text-center">

          {/* badge */}
          <div className="inline-flex items-center gap-2.5 rounded-full border border-white/15 bg-white/8 px-5 py-2.5 backdrop-blur-sm">
            <Sparkles className="h-4 w-4 text-[#6ba4ff]" />
            <span className="font-[family-name:var(--font-body)] text-[13px] font-medium tracking-wide text-white/80">
              AI-Powered Authenticity Detection
            </span>
          </div>

          {/* headline — Outfit for personality, tight tracking for editorial feel */}
          <h1 className="mt-10 max-w-5xl font-[family-name:var(--font-headline)] text-[3.5rem] font-extrabold leading-[1.05] tracking-[-0.035em] text-white sm:text-[4.5rem] md:text-[6rem] lg:text-[7rem]">
            Detect{' '}
            <span className="bg-gradient-to-r from-[#6ba4ff] to-[#a78bfa] bg-clip-text text-transparent">
              Deepfakes
            </span>
            <br />
            Before They{' '}
            <span className="bg-gradient-to-r from-[#f97316] to-[#fb923c] bg-clip-text text-transparent">
              Spread
            </span>
          </h1>

          {/* sub-copy — bumped to 70% opacity, proper 1.7 line-height */}
          <p className="mt-8 max-w-2xl font-[family-name:var(--font-body)] text-lg font-normal leading-[1.7] text-white/70 md:text-xl md:leading-[1.75]">
            Advanced verification workflows for manipulated images and
            deceptive news. Protect truth with accountable evidence, live
            status, and investigation-ready results.
          </p>

          {/* CTAs */}
          <div className="mt-12 flex flex-col items-center gap-4 sm:flex-row">
            <Link
              href="/analyze/news"
              className="glow-primary inline-flex min-w-[210px] items-center justify-center gap-2 rounded-2xl bg-[#4c8fff] px-8 py-5 font-[family-name:var(--font-body)] text-base font-semibold tracking-wide text-white transition-all duration-300 hover:bg-[#68a0ff] hover:scale-[1.02]"
            >
              Start Scanning
              <ArrowRight className="h-5 w-5" />
            </Link>
            <Link
              href="/system"
              className="inline-flex min-w-[170px] items-center justify-center rounded-2xl border border-white/18 bg-white/6 px-8 py-5 font-[family-name:var(--font-body)] text-base font-medium tracking-wide text-white/80 backdrop-blur-sm transition-all duration-300 hover:border-white/35 hover:text-white hover:bg-white/10"
            >
              View System
            </Link>
          </div>

          {/* stats strip */}
          <div id="stats" className="mt-24 grid w-full max-w-5xl grid-cols-2 gap-y-10 md:grid-cols-4">
            {stats.map((stat) => (
              <div key={stat.label} className="text-center">
                <p className="text-glow font-[family-name:var(--font-headline)] text-4xl font-bold tracking-[-0.03em] text-[#6ba4ff] md:text-5xl">
                  {stat.value}
                </p>
                <p className="mt-2.5 font-[family-name:var(--font-body)] text-base font-semibold text-white/75">
                  {stat.label}
                </p>
                <p className="mt-1 font-[family-name:var(--font-body)] text-sm font-normal text-white/45">
                  {stat.sub}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ─── Investigation Desks ─── */}
      <section id="detection" className="relative px-6 py-24 lg:px-10">
        <div className="mx-auto max-w-5xl">
          <div className="mb-16 text-center">
            <h2 className="font-[family-name:var(--font-headline)] text-4xl font-bold tracking-[-0.03em] text-white md:text-6xl">
              Investigation{' '}
              <span className="text-glow bg-gradient-to-r from-[#6ba4ff] to-[#a78bfa] bg-clip-text text-transparent">
                desks
              </span>
            </h2>
            <p className="mx-auto mt-5 max-w-2xl font-[family-name:var(--font-body)] text-base leading-[1.7] text-white/60">
              Choose the right desk for your investigation. Each one is backed
              by specialised models, structured signal breakdowns, and a live
              processing pipeline you can inspect in real time.
            </p>
          </div>

          <div className="grid gap-6 md:grid-cols-2">
            {detectionCards.map((type) => (
              <article key={type.id} className="deepglass-soft group rounded-docket p-7 transition duration-300 hover:-translate-y-1 hover:border-[#4c8fff]/40">
                <div className="mb-5 flex items-start gap-4">
                  <div className="rounded-2xl border border-white/10 bg-white/6 p-3.5">
                    <type.icon className="h-6 w-6 text-[#6ba4ff]" />
                  </div>
                  <div>
                    <h3 className="font-[family-name:var(--font-headline)] text-2xl font-bold tracking-[-0.02em] text-white">
                      {type.title}
                    </h3>
                    <div className="mt-1.5 flex gap-3">
                      <span className="font-[family-name:var(--font-body)] text-xs font-semibold text-[#6ba4ff]">
                        {type.accuracy}
                      </span>
                      <span className="font-[family-name:var(--font-body)] text-xs font-medium text-white/50">
                        {type.speed}
                      </span>
                    </div>
                  </div>
                </div>

                <p className="mb-5 font-[family-name:var(--font-body)] text-sm leading-[1.75] text-white/65">
                  {type.description}
                </p>

                <div className="mb-5 flex flex-wrap gap-2">
                  {type.models.map((model) => (
                    <span
                      key={model}
                      className="rounded-full border border-white/10 bg-white/5 px-3.5 py-1.5 font-[family-name:var(--font-body)] text-[11px] font-semibold uppercase tracking-[0.12em] text-white/65"
                    >
                      {model}
                    </span>
                  ))}
                </div>

                <div className="rounded-[1.35rem] border border-dashed border-white/12 bg-white/4 p-6 text-center">
                  <p className="font-[family-name:var(--font-body)] text-sm font-medium text-white/55">
                    Ready for live input
                  </p>
                  <p className="mt-1 font-[family-name:var(--font-body)] text-[11px] font-semibold uppercase tracking-[0.18em] text-white/38">
                    {type.accepts}
                  </p>
                </div>

                <Link
                  href={type.href}
                  className="glow-primary mt-6 inline-flex w-full items-center justify-center gap-2 rounded-2xl bg-[#4c8fff] px-6 py-4 font-[family-name:var(--font-body)] text-sm font-bold uppercase tracking-[0.14em] text-white transition-all duration-300 hover:bg-[#68a0ff] hover:scale-[1.01]"
                >
                  Open desk
                  <ArrowRight className="h-4 w-4" />
                </Link>
              </article>
            ))}
          </div>
        </div>
      </section>

      {/* ─── Features Grid ─── */}
      <section id="features" className="relative px-6 py-24 lg:px-10">
        <div className="mx-auto max-w-5xl">
          <div className="mb-16 text-center">
            <h2 className="font-[family-name:var(--font-headline)] text-4xl font-bold tracking-[-0.03em] text-white md:text-6xl">
              Built for{' '}
              <span className="text-glow bg-gradient-to-r from-[#6ba4ff] to-[#a78bfa] bg-clip-text text-transparent">
                precision
              </span>
            </h2>
            <p className="mx-auto mt-5 max-w-2xl font-[family-name:var(--font-body)] text-base leading-[1.7] text-white/60">
              Every component is designed around forensic accuracy, from the
              neural pipeline to the analyst-facing interface. No black boxes,
              no hidden scores.
            </p>
          </div>

          <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {features.map((feature) => (
              <article key={feature.title} className="deepglass-soft rounded-docket p-7 transition duration-300 hover:border-[#4c8fff]/34">
                <feature.icon className="h-8 w-8 text-[#6ba4ff]" />
                <h3 className="mt-5 font-[family-name:var(--font-headline)] text-xl font-bold tracking-[-0.01em] text-white">
                  {feature.title}
                </h3>
                <p className="mt-3 font-[family-name:var(--font-body)] text-sm leading-[1.75] text-white/60">
                  {feature.desc}
                </p>
              </article>
            ))}
          </div>
        </div>
      </section>
    </div>
  );
}
