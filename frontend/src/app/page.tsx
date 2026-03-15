import Link from 'next/link';
import { ArrowUpRight, CheckCircle2, Scale, Shield, Siren, Workflow } from 'lucide-react';

import { HomeHero } from '@/components/home-hero';

const pillars = [
  {
    title: 'Understandable evidence',
    copy: 'Each analysis returns a verdict, a confidence score, and plain-language evidence notes instead of a black-box answer.',
    icon: CheckCircle2,
  },
  {
    title: 'Three modalities, one workflow',
    copy: 'Video, news, and audio checks share a single request lifecycle so the product can grow into a full verification command center.',
    icon: Workflow,
  },
  {
    title: 'Human review preserved',
    copy: 'DeepGuard is designed as decision support. Investigators still see uncertainty, context, and a trail they can challenge.',
    icon: Scale,
  },
];

const stack = [
  'Next.js App Router',
  'TypeScript + Tailwind CSS',
  'FastAPI + SQLAlchemy',
  'JWT auth + background jobs',
  'Replaceable ML analyzer adapters',
  'Docker + GitHub Actions',
];

export default function HomePage() {
  return (
    <>
      <HomeHero />
      <section className="px-6 pb-8 lg:px-10">
        <div className="mx-auto grid max-w-7xl gap-6 lg:grid-cols-3">
          {pillars.map((pillar) => (
            <article key={pillar.title} className="rounded-docket border border-soot/10 bg-white/72 p-6 shadow-docket">
              <pillar.icon className="h-5 w-5 text-ember" />
              <h2 className="mt-4 font-[family-name:var(--font-display)] text-3xl text-soot">{pillar.title}</h2>
              <p className="mt-3 text-sm leading-7 text-soot/70">{pillar.copy}</p>
            </article>
          ))}
        </div>
      </section>

      <section className="px-6 py-12 lg:px-10">
        <div className="mx-auto grid max-w-7xl gap-8 lg:grid-cols-[1.1fr_0.9fr]">
          <div className="rounded-docket border border-soot/12 bg-soot p-8 text-paper shadow-docket">
            <p className="font-mono text-xs uppercase tracking-[0.3em] text-paper/55">System architecture</p>
            <h2 className="mt-4 max-w-2xl font-[family-name:var(--font-display)] text-5xl leading-none">A product-shaped prototype that can grow into the full research stack.</h2>
            <div className="mt-8 space-y-4">
              {[
                ['Interface', 'Next.js scenes for intake, results, and case history.'],
                ['API', 'FastAPI routes for auth, verification requests, polling, and history.'],
                ['Queue', 'Background task lifecycle with Celery-ready hooks and task state tracking.'],
                ['Model layer', 'Prototype analyzers today, PyTorch inference adapters tomorrow.'],
              ].map(([title, copy]) => (
                <div key={title} className="rounded-[1.25rem] border border-paper/10 bg-paper/5 p-4">
                  <p className="font-semibold uppercase tracking-[0.18em] text-paper">{title}</p>
                  <p className="mt-2 text-sm leading-7 text-paper/70">{copy}</p>
                </div>
              ))}
            </div>
          </div>

          <div className="rounded-docket border border-soot/12 bg-white/72 p-8 shadow-docket">
            <p className="font-mono text-xs uppercase tracking-[0.3em] text-soot/50">Core stack</p>
            <div className="mt-5 grid gap-3 sm:grid-cols-2">
              {stack.map((item) => (
                <div key={item} className="rounded-[1rem] border border-soot/10 bg-paper/70 px-4 py-3 text-sm text-soot/72">
                  {item}
                </div>
              ))}
            </div>
            <div className="mt-8 rounded-[1.3rem] border border-ember/15 bg-ember/8 p-5 text-soot">
              <p className="font-mono text-xs uppercase tracking-[0.3em] text-soot/55">Ideal users</p>
              <div className="mt-4 space-y-4">
                {[
                  ['Journalists', 'Check anonymous footage before publication.'],
                  ['Finance and security teams', 'Flag voice-clone or panic-inducing fake media before action.'],
                  ['Legal reviewers', 'Add explainable authenticity checks to evidence screening.'],
                ].map(([title, copy]) => (
                  <div key={title} className="flex items-start gap-3">
                    <Shield className="mt-1 h-4 w-4 text-ember" />
                    <div>
                      <p className="font-semibold uppercase tracking-[0.15em]">{title}</p>
                      <p className="text-sm leading-7 text-soot/70">{copy}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className="px-6 pb-16 lg:px-10">
        <div className="mx-auto rounded-docket border border-soot/12 bg-white/74 p-8 shadow-docket lg:max-w-7xl">
          <div className="flex flex-col gap-6 lg:flex-row lg:items-end lg:justify-between">
            <div>
              <p className="font-mono text-xs uppercase tracking-[0.3em] text-soot/50">Start building</p>
              <h2 className="mt-4 font-[family-name:var(--font-display)] text-5xl text-soot">Open the first investigation desk and wire in the real models next.</h2>
            </div>
            <div className="flex flex-col gap-3 sm:flex-row">
              <Link href="/analyze/video" className="inline-flex items-center justify-center gap-2 rounded-full bg-soot px-6 py-4 text-sm font-semibold uppercase tracking-[0.24em] text-paper transition hover:bg-ember">
                Launch video desk
                <ArrowUpRight className="h-4 w-4" />
              </Link>
              <Link href="/history" className="inline-flex items-center justify-center gap-2 rounded-full border border-soot/15 bg-paper px-6 py-4 text-sm font-semibold uppercase tracking-[0.24em] text-soot transition hover:border-ember/35 hover:text-ember">
                Review case log
                <Siren className="h-4 w-4" />
              </Link>
            </div>
          </div>
        </div>
      </section>
    </>
  );
}
