import type { Metadata } from 'next';
import { Inter, Space_Grotesk } from 'next/font/google';
import type { ReactNode } from 'react';

import './globals.css';
import { AuthSessionSync } from '@/components/auth-session-sync';
import { SiteFooter } from '@/components/site-footer';
import { SiteHeader } from '@/components/site-header';

const fontBody = Inter({
  subsets: ['latin'],
  variable: '--font-body',
  display: 'swap',
});

const fontDisplay = Space_Grotesk({
  subsets: ['latin'],
  variable: '--font-display',
  display: 'swap',
});

export const metadata: Metadata = {
  title: 'DeepGuard',
  description: 'Investigate suspicious images and news with a forensic editorial workflow.',
};

export default function RootLayout({ children }: Readonly<{ children: ReactNode }>) {
  return (
    <html lang="en">
      <body className={`${fontBody.variable} ${fontDisplay.variable} text-paper antialiased`}>
        <AuthSessionSync />
        <a
          href="#main-content"
          className="sr-only focus:not-sr-only focus:fixed focus:left-4 focus:top-4 focus:z-50 focus:rounded-full focus:bg-ember focus:px-4 focus:py-3 focus:text-sm focus:font-semibold focus:text-paper"
        >
          Skip to content
        </a>
        <SiteHeader />
        <main id="main-content">{children}</main>
        <SiteFooter />
      </body>
    </html>
  );
}
