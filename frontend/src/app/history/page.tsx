import Link from 'next/link';
import { ArrowLeft } from 'lucide-react';

import { HistoryList } from '@/components/history-list';

export default function HistoryPage() {
  return (
    <section className="px-6 py-12 lg:px-10 lg:py-16">
      <div className="mx-auto max-w-7xl space-y-6">
        <Link href="/" className="inline-flex items-center gap-2 text-sm font-semibold uppercase tracking-[0.22em] text-soot/60 transition hover:text-ember">
          <ArrowLeft className="h-4 w-4" />
          Back to overview
        </Link>
        <div className="rounded-docket border border-soot/12 bg-white/75 p-8 shadow-docket">
          <p className="font-mono text-xs uppercase tracking-[0.3em] text-soot/50">Case log</p>
          <h1 className="mt-4 font-[family-name:var(--font-display)] text-5xl text-soot">Verification history and recent outcomes.</h1>
          <p className="mt-4 max-w-3xl text-base leading-8 text-soot/70">
            This log reads from the backend history endpoint using the shared analysis schema, so it stays aligned with the verification desks.
          </p>
        </div>
        <HistoryList />
      </div>
    </section>
  );
}
