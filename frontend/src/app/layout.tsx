import type { Metadata } from 'next';
import type { ReactNode } from 'react';

import './globals.css';
import { AuthSessionSync } from '@/components/auth-session-sync';
import { SiteHeader } from '@/components/site-header';

export const metadata: Metadata = {
  title: 'DeepGuard',
  description: 'Investigate suspicious videos, news, and audio with a forensic editorial workflow.',
};

export default function RootLayout({ children }: Readonly<{ children: ReactNode }>) {
  return (
    <html lang="en">
      <body className="bg-paper text-soot antialiased">
        <AuthSessionSync />
        <a
          href="#main-content"
          className="sr-only focus:not-sr-only focus:fixed focus:left-4 focus:top-4 focus:z-50 focus:rounded-full focus:bg-soot focus:px-4 focus:py-3 focus:text-sm focus:font-semibold focus:text-paper"
        >
          Skip to content
        </a>
        <SiteHeader />
        <main id="main-content">{children}</main>
      </body>
    </html>
  );
}
