'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { ArrowRight, Shield } from 'lucide-react';

const marketingNav = [
  { href: '#features', label: 'Features' },
  { href: '#detection', label: 'Detection' },
  { href: '#stats', label: 'Stats' },
];

const productNav = [
  { href: '/analyze/image', label: 'Image Lab' },
  { href: '/analyze/news', label: 'News Desk' },
  { href: '/history', label: 'Case Log' },
  { href: '/system', label: 'System' },
];

export function SiteHeader() {
  const pathname = usePathname();
  const isHome = pathname === '/';
  const navItems = isHome ? marketingNav : productNav;

  return (
    <header className="sticky top-0 z-40 backdrop-blur-md bg-transparent">
      <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-5 lg:px-10">
        <Link href="/" className="flex items-center gap-3 text-white group">
          <span className="flex h-10 w-10 items-center justify-center rounded-full border border-white/15 bg-white/8 text-[#6ba4ff] shadow-docket transition-all duration-300 group-hover:bg-[#6ba4ff]/20 group-hover:border-[#6ba4ff]/40">
            <Shield className="h-4.5 w-4.5" />
          </span>
          <div className="flex items-baseline gap-0.5">
            <span className="font-[family-name:var(--font-headline)] text-[1.65rem] font-bold tracking-[-0.03em] text-white">
              Deep
            </span>
            <span className="font-[family-name:var(--font-headline)] text-[1.65rem] font-bold tracking-[-0.03em] text-[#6ba4ff]">
              Guard
            </span>
          </div>
        </Link>

        <nav className="hidden items-center gap-8 md:flex">
          {navItems.map((item) =>
            isHome ? (
              <a
                key={item.href}
                href={item.href}
                className="relative py-1 font-[family-name:var(--font-body)] text-[13px] font-medium tracking-wide text-white/55 transition-colors duration-200 hover:text-white after:absolute after:bottom-0 after:left-0 after:h-[2px] after:w-0 after:bg-[#6ba4ff] after:transition-all after:duration-300 hover:after:w-full"
              >
                {item.label}
              </a>
            ) : (
              <Link
                key={item.href}
                href={item.href}
                className="relative py-1 font-[family-name:var(--font-body)] text-[13px] font-medium tracking-wide text-white/55 transition-colors duration-200 hover:text-white after:absolute after:bottom-0 after:left-0 after:h-[2px] after:w-0 after:bg-[#6ba4ff] after:transition-all after:duration-300 hover:after:w-full"
              >
                {item.label}
              </Link>
            ),
          )}
        </nav>

        <Link
          href="/analyze/news"
          className="glow-primary inline-flex items-center gap-2 rounded-full bg-[#4c8fff] px-6 py-3 font-[family-name:var(--font-body)] text-[13px] font-bold tracking-wide text-white transition-all duration-300 hover:bg-[#68a0ff] hover:scale-[1.03]"
        >
          {isHome ? 'Get Started' : 'Start scan'}
          <ArrowRight className="h-4 w-4" />
        </Link>
      </div>
    </header>
  );
}
