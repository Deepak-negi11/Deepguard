import Link from 'next/link';
import { ArrowRight, AudioLines, Newspaper, ScanSearch, ShieldAlert, ImagePlus } from 'lucide-react';

const lanes = [
  { icon: ImagePlus, title: 'Image', detail: 'Pixel noise, EXIF anomalies, and inserted regional manipulation.' },
  { icon: Newspaper, title: 'News', detail: 'Credibility scoring, rhetoric analysis, and source reputation.' },
  { icon: AudioLines, title: 'Audio', detail: 'Spectral artifacts, prosody irregularities, and voice-clone signals.' },
];

export function HomeHero() {
  return (
    <section className="relative overflow-hidden px-6 py-16 lg:px-10 lg:py-24">
      <div className="mx-auto grid max-w-7xl gap-10 lg:grid-cols-[1.25fr_0.85fr] lg:items-end">
        <div className="space-y-8">
          <div className="inline-flex items-center gap-3 rounded-full border border-soot/15 bg-white/55 px-4 py-2 font-mono text-xs uppercase tracking-[0.3em] text-soot/60">
            <ScanSearch className="h-4 w-4 text-ember" />
            Content authenticity laboratory
          </div>
          <div className="space-y-5">
            <p className="max-w-xl font-mono text-sm uppercase tracking-[0.4em] text-soot/50">Truth needs tooling.</p>
            <h1 className="max-w-4xl font-[family-name:var(--font-display)] text-5xl leading-[0.94] text-soot md:text-7xl">
              Investigate suspicious media like an editorial forensic desk, not a toy detector.
            </h1>
            <p className="max-w-2xl text-lg leading-8 text-soot/72">
              DeepGuard lets journalists, legal teams, security desks, and everyday users run authenticity checks on images, news, and audio from one unified caseboard.
            </p>
          </div>
          <div className="flex flex-col gap-4 sm:flex-row">
            <Link href="/analyze/image" className="inline-flex items-center justify-center gap-2 rounded-full bg-soot px-6 py-4 text-sm font-semibold uppercase tracking-[0.24em] text-paper transition hover:bg-ember">
              Start a case
              <ArrowRight className="h-4 w-4" />
            </Link>
            <Link href="/demo" className="inline-flex items-center justify-center rounded-full border border-soot/15 bg-white/40 px-6 py-4 text-sm font-semibold uppercase tracking-[0.24em] text-soot transition hover:border-ember/40 hover:text-ember">
              Open teacher demo
            </Link>
            <Link href="/history" className="inline-flex items-center justify-center rounded-full border border-soot/15 bg-white/40 px-6 py-4 text-sm font-semibold uppercase tracking-[0.24em] text-soot transition hover:border-ember/40 hover:text-ember">
              View investigation log
            </Link>
          </div>
        </div>
        <div className="rounded-docket border border-soot/10 bg-white/50 p-6 shadow-docket backdrop-blur-sm">
          <div className="grid gap-4 sm:grid-cols-3 lg:grid-cols-1">
            {lanes.map((lane) => (
              <article key={lane.title} className="rounded-[1.35rem] border border-soot/10 bg-paper/80 p-5">
                <lane.icon className="h-5 w-5 text-ember" />
                <h2 className="mt-4 font-[family-name:var(--font-display)] text-2xl text-soot">{lane.title}</h2>
                <p className="mt-2 text-sm leading-7 text-soot/70">{lane.detail}</p>
              </article>
            ))}
          </div>
          <div className="mt-6 rounded-[1.35rem] border border-ember/20 bg-soot p-5 text-paper">
            <div className="flex items-center justify-between font-mono text-xs uppercase tracking-[0.35em] text-paper/65">
              <span>Case throughput</span>
              <span>Prototype</span>
            </div>
            <div className="mt-5 grid gap-4 sm:grid-cols-3 lg:grid-cols-3">
              {[
                ['10-20s', 'image analysis'],
                ['10-20s', 'news scoring'],
                ['10-15s', 'audio trace'],
              ].map(([value, label]) => (
                <div key={label}>
                  <p className="font-[family-name:var(--font-display)] text-3xl text-paper">{value}</p>
                  <p className="mt-1 text-sm text-paper/70">{label}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
      <div className="pointer-events-none absolute inset-x-0 top-0 -z-10 h-[560px] bg-[radial-gradient(circle_at_top_left,rgba(178,58,32,0.2),transparent_36%),radial-gradient(circle_at_80%_20%,rgba(86,108,84,0.18),transparent_30%)]" />
      <div className="pointer-events-none absolute inset-0 -z-20 bg-forensic-grid bg-[size:36px_36px] opacity-20" />
    </section>
  );
}
