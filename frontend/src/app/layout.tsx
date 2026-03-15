import type { Metadata } from 'next';
import type { ReactNode } from 'react';
import { Fraunces, IBM_Plex_Mono } from 'next/font/google';

import './globals.css';
import { SiteHeader } from '@/components/site-header';

const display = Fraunces({
  subsets: ['latin'],
  variable: '--font-display',
  weight: ['400', '500', '600', '700'],
});

const mono = IBM_Plex_Mono({
  subsets: ['latin'],
  variable: '--font-mono',
  weight: ['400', '500', '600'],
});

export const metadata: Metadata = {
  title: 'DeepGuard',
  description: 'Investigate suspicious videos, news, and audio with a forensic editorial workflow.',
};

export default function RootLayout({ children }: Readonly<{ children: ReactNode }>) {
  return (
    <html lang="en">
      <body className={`${display.variable} ${mono.variable} bg-paper text-soot antialiased`}>
        <SiteHeader />
        <main>{children}</main>
      </body>
    </html>
  );
}
