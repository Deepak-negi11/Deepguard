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
    <header className="sticky top-0 z-40 border-b border-paper/8 bg-soot/24 backdrop-blur-2xl">
      <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-4 lg:px-10">
        <Link href="/" className="flex items-center gap-3 text-paper">
          <span className="flex h-10 w-10 items-center justify-center rounded-full border border-paper/12 bg-paper/5 text-[#4c8fff] shadow-docket">
            <Shield className="h-4.5 w-4.5" />
          </span>
          <div className="flex items-baseline gap-0.5">
            <span className="font-[family-name:var(--font-display)] text-[1.75rem] font-semibold tracking-[-0.04em] text-paper">Deep</span>
            <span className="font-[family-name:var(--font-display)] text-[1.75rem] font-semibold tracking-[-0.04em] text-[#4c8fff]">Guard</span>
          </div>
        </Link>

        <nav className="hidden items-center gap-10 text-sm font-medium text-paper/48 md:flex">
          {navItems.map((item) =>
            isHome ? (
              <a key={item.href} href={item.href} className="transition hover:text-paper/90">
                {item.label}
              </a>
            ) : (
              <Link key={item.href} href={item.href} className="transition hover:text-paper/90">
                {item.label}
              </Link>
            ),
          )}
        </nav>

        <Link
          href="/analyze/news"
          className="glow-primary inline-flex items-center gap-2 rounded-2xl bg-[#4c8fff] px-5 py-3 text-sm font-semibold text-white transition hover:bg-[#68a0ff]"
        >
          {isHome ? 'Get Started' : 'Start scan'}
          <ArrowRight className="h-4 w-4" />
        </Link>
      </div>
    </header>
  );
}
