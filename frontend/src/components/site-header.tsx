import Link from 'next/link';
import { ShieldCheck, Siren, Waypoints } from 'lucide-react';

const navItems = [
  { href: '/analyze/video', label: 'Video Lab' },
  { href: '/analyze/news', label: 'News Desk' },
  { href: '/analyze/audio', label: 'Audio Trace' },
  { href: '/history', label: 'Case Log' },
];

export function SiteHeader() {
  return (
    <header className="sticky top-0 z-40 border-b border-soot/10 bg-paper/80 backdrop-blur-xl">
      <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-4 lg:px-10">
        <Link href="/" className="flex items-center gap-3 text-soot">
          <span className="flex h-12 w-12 items-center justify-center rounded-full border border-soot/15 bg-soot text-paper shadow-docket">
            <ShieldCheck className="h-5 w-5" />
          </span>
          <div>
            <p className="font-[family-name:var(--font-display)] text-2xl leading-none">DeepGuard</p>
            <p className="font-mono text-[11px] uppercase tracking-[0.35em] text-soot/60">Forensic verification desk</p>
          </div>
        </Link>
        <nav className="hidden items-center gap-6 text-sm uppercase tracking-[0.22em] text-soot/70 md:flex">
          {navItems.map((item) => (
            <Link key={item.href} href={item.href} className="transition hover:text-ember">
              {item.label}
            </Link>
          ))}
        </nav>
        <div className="hidden items-center gap-2 md:flex">
          <span className="inline-flex items-center gap-2 rounded-full border border-moss/30 bg-moss/10 px-3 py-2 text-xs font-medium text-moss">
            <Waypoints className="h-3.5 w-3.5" />
            Multi-modal queue
          </span>
          <span className="inline-flex items-center gap-2 rounded-full border border-ember/30 bg-ember/10 px-3 py-2 text-xs font-medium text-ember">
            <Siren className="h-3.5 w-3.5" />
            Human review ready
          </span>
        </div>
      </div>
    </header>
  );
}
