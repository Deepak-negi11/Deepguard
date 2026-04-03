import Link from 'next/link';
import { ShieldCheck } from 'lucide-react';

export function SiteFooter() {
  return (
    <footer className="border-t border-white/8 bg-black/30 px-6 py-12 backdrop-blur-xl lg:px-10">
      <div className="mx-auto flex max-w-7xl flex-col items-center justify-between gap-6 md:flex-row">
        <div className="flex items-center gap-3">
          <span className="flex h-10 w-10 items-center justify-center rounded-full border border-white/12 bg-white/6 text-[#6ba4ff]">
            <ShieldCheck className="h-4 w-4" />
          </span>
          <div>
            <p className="font-[family-name:var(--font-headline)] text-xl font-bold text-white">
              Deep<span className="text-[#6ba4ff]">Guard</span>
            </p>
            <p className="font-[family-name:var(--font-body)] text-[11px] font-semibold uppercase tracking-[0.22em] text-white/45">
              Image and news authenticity desk
            </p>
          </div>
        </div>

        <div className="flex flex-wrap items-center gap-6">
          <Link
            href="/analyze/image"
            className="font-[family-name:var(--font-body)] text-sm font-medium text-white/55 transition hover:text-[#6ba4ff]"
          >
            Image Lab
          </Link>
          <Link
            href="/analyze/news"
            className="font-[family-name:var(--font-body)] text-sm font-medium text-white/55 transition hover:text-[#6ba4ff]"
          >
            News Desk
          </Link>
          <Link
            href="/system"
            className="font-[family-name:var(--font-body)] text-sm font-medium text-white/55 transition hover:text-[#6ba4ff]"
          >
            System
          </Link>
          <Link
            href="/history"
            className="font-[family-name:var(--font-body)] text-sm font-medium text-white/55 transition hover:text-[#6ba4ff]"
          >
            Case Log
          </Link>
        </div>

        <p className="font-[family-name:var(--font-body)] text-[13px] font-normal text-white/40">
          © 2026 DeepGuard. Investigation support for manipulated media.
        </p>
      </div>
    </footer>
  );
}
