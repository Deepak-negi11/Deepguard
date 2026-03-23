import Link from 'next/link';
import { ArrowRight, ImagePlus, Newspaper, ScanSearch } from 'lucide-react';

const lanes = [
  { icon: ImagePlus, title: 'Image', detail: 'Pixel noise, EXIF anomalies, and inserted regional manipulation.' },
  { icon: Newspaper, title: 'News', detail: 'Credibility scoring, rhetoric analysis, and source reputation.' },
];

export function HomeHero() {
  return (
    <section className="relative overflow-hidden px-6 py-16 lg:px-10 lg:py-24">
      <div className="mx-auto grid max-w-7xl gap-10 lg:grid-cols-[1.25fr_0.85fr] lg:items-end">
        <div className="space-y-8">
          <div className="inline-flex items-center gap-3 rounded-full border border-paper/12 bg-paper/6 px-4 py-2 font-mono text-xs uppercase tracking-[0.3em] text-paper/60">
            <ScanSearch className="h-4 w-4 text-moss" />
            Content authenticity laboratory
          </div>
          <div className="space-y-5">
            <p className="max-w-xl font-mono text-sm uppercase tracking-[0.4em] text-paper/42">Truth needs tooling.</p>
            <h1 className="max-w-4xl font-[family-name:var(--font-display)] text-5xl leading-[0.94] text-paper md:text-7xl">
              Investigate suspicious media like an editorial forensic desk, not a toy detector.
            </h1>
            <p className="max-w-2xl text-lg leading-8 text-paper/72">
              DeepGuard lets journalists, legal teams, security desks, and everyday users run authenticity checks on images and news from one unified caseboard.
            </p>
          </div>
          <div className="flex flex-col gap-4 sm:flex-row">
            <Link href="/analyze/image" className="inline-flex items-center justify-center gap-2 rounded-full bg-paper px-6 py-4 text-sm font-semibold uppercase tracking-[0.24em] text-soot transition hover:bg-moss">
              Start a case
              <ArrowRight className="h-4 w-4" />
            </Link>
            <Link href="/analyze/news" className="inline-flex items-center justify-center rounded-full border border-paper/14 bg-paper/6 px-6 py-4 text-sm font-semibold uppercase tracking-[0.24em] text-paper transition hover:border-moss/45 hover:text-moss">
              Open news desk
            </Link>
            <Link href="/history" className="inline-flex items-center justify-center rounded-full border border-paper/14 bg-paper/6 px-6 py-4 text-sm font-semibold uppercase tracking-[0.24em] text-paper transition hover:border-moss/45 hover:text-moss">
              View investigation log
            </Link>
          </div>
        </div>
        <div className="deepglass rounded-docket p-6">
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-1">
            {lanes.map((lane) => (
              <article key={lane.title} className="rounded-[1.35rem] border border-paper/10 bg-paper/6 p-5">
                <lane.icon className="h-5 w-5 text-moss" />
                <h2 className="mt-4 font-[family-name:var(--font-display)] text-2xl text-paper">{lane.title}</h2>
                <p className="mt-2 text-sm leading-7 text-paper/68">{lane.detail}</p>
              </article>
            ))}
          </div>
          <div className="mt-6 rounded-[1.35rem] border border-paper/10 bg-paper/6 p-5 text-paper">
            <div className="flex items-center justify-between font-mono text-xs uppercase tracking-[0.35em] text-paper/55">
              <span>Case throughput</span>
              <span>Prototype</span>
            </div>
            <div className="mt-5 grid gap-4 sm:grid-cols-2 lg:grid-cols-2">
              {[
                ['10-20s', 'image analysis'],
                ['10-20s', 'news scoring'],
              ].map(([value, label]) => (
                <div key={label}>
                  <p className="font-[family-name:var(--font-display)] text-3xl text-paper">{value}</p>
                  <p className="mt-1 text-sm text-paper/62">{label}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
      <div className="pointer-events-none absolute inset-x-0 top-0 -z-10 h-[620px] bg-[radial-gradient(circle_at_76%_18%,rgba(150,240,255,0.68),transparent_14%),radial-gradient(circle_at_66%_34%,rgba(82,121,255,0.38),transparent_24%),radial-gradient(circle_at_18%_62%,rgba(58,92,214,0.2),transparent_26%)]" />
      <div className="pointer-events-none absolute inset-0 -z-20 bg-forensic-grid bg-[size:42px_42px] opacity-15" />
    </section>
  );
}
