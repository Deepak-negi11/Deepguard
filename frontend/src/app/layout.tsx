import type { Metadata } from 'next';
import { Inter, Space_Grotesk, Outfit } from 'next/font/google';
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

const fontHeadline = Outfit({
  subsets: ['latin'],
  variable: '--font-headline',
  display: 'swap',
  weight: ['300', '400', '500', '600', '700', '800', '900'],
});

export const metadata: Metadata = {
  title: 'DeepGuard — AI-Powered Deepfake Detection',
  description: 'Investigate suspicious images and news with a forensic editorial workflow. Advanced verification for manipulated media.',
};

export default function RootLayout({ children }: Readonly<{ children: ReactNode }>) {
  return (
    <html lang="en">
      <body className={`${fontBody.variable} ${fontDisplay.variable} ${fontHeadline.variable} text-paper antialiased flex min-h-screen flex-col`} suppressHydrationWarning>
        <AuthSessionSync />
        <a
          href="#main-content"
          className="sr-only focus:not-sr-only focus:fixed focus:left-4 focus:top-4 focus:z-50 focus:rounded-full focus:bg-ember focus:px-4 focus:py-3 focus:text-sm focus:font-semibold focus:text-paper"
        >
          Skip to content
        </a>
        <SiteHeader />
        <main id="main-content" className="flex-1">{children}</main>
        <SiteFooter />
      </body>
    </html>
  );
}
