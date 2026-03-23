import Link from 'next/link';
import { ArrowLeft, Radar } from 'lucide-react';

import { HistoryList } from '@/components/history-list';

export default function HistoryPage() {
  return (
    <section className="px-6 py-12 lg:px-10 lg:py-16">
      <div className="mx-auto max-w-7xl space-y-6">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <Link href="/" className="inline-flex items-center gap-2 text-sm font-semibold uppercase tracking-[0.22em] text-paper/60 transition hover:text-moss">
            <ArrowLeft className="h-4 w-4" />
            Back to overview
          </Link>
          <Link href="/system" className="inline-flex items-center gap-2 text-sm font-semibold uppercase tracking-[0.22em] text-paper/60 transition hover:text-moss">
            <Radar className="h-4 w-4" />
            Open system desk
          </Link>
        </div>
        <div className="deepglass rounded-docket p-8 text-paper">
          <p className="font-mono text-xs uppercase tracking-[0.3em] text-paper/44">Case log</p>
          <h1 className="mt-4 font-[family-name:var(--font-display)] text-5xl text-paper">Verification history and recent outcomes.</h1>
          <p className="mt-4 max-w-3xl text-base leading-8 text-paper/68">
            This log reads from the backend history endpoint using the shared analysis schema, so it stays aligned with the verification desks and the
            live system status page.
          </p>
        </div>
        <HistoryList />
      </div>
    </section>
  );
}
