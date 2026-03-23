'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';

import { fetchHistory, logout } from '@/lib/api';
import { asConfidencePercent, confidenceBand } from '@/lib/utils';
import { useAuthStore } from '@/store/use-auth-store';
import type { HistoryItem } from '@/types/analysis';
import { AuthCard } from './auth-card';

export function HistoryList() {
  const { userId, email, clearSession, hasHydrated } = useAuthStore();
  const [rows, setRows] = useState<HistoryItem[]>([]);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!hasHydrated) {
      return;
    }
    if (!userId) {
      setRows([]);
      setError('');
      return;
    }

    async function run() {
      try {
        const history = await fetchHistory();
        setRows(history.results.filter((row) => row.type !== 'audio'));
        setError('');
      } catch {
        setError('Start the backend to load the case history.');
      }
    }

    void run();
  }, [hasHydrated, userId]);

  async function handleSignOut() {
    try {
      await logout();
    } catch {
      // ignore logout errors; clear client auth state regardless
    }
    clearSession();
  }

  if (!hasHydrated) {
    return <p className="rounded-[1rem] border border-dashed border-paper/14 bg-paper/5 px-4 py-5 text-sm text-paper/62">Restoring your session...</p>;
  }

  if (!userId) {
    return (
      <AuthCard
        title="Sign in to view the case log"
        copy="History is now account-scoped instead of using a shared demo user, so each analyst sees their own verification trail."
      />
    );
  }

  if (error) {
    return <p className="rounded-[1rem] border border-dashed border-paper/14 bg-paper/5 px-4 py-5 text-sm text-paper/62">{error}</p>;
  }

  if (!rows.length) {
    return <p className="rounded-[1rem] border border-dashed border-paper/14 bg-paper/5 px-4 py-5 text-sm text-paper/62">No investigations yet. Run the first case from any analysis desk.</p>;
  }

  return (
    <div className="space-y-4">
      <div className="deepglass-soft flex flex-wrap items-center justify-between gap-3 rounded-[1rem] px-4 py-4 text-sm text-paper/72">
        <span>Signed in as {email}</span>
        <div className="flex flex-wrap gap-2">
          <Link
            href="/system"
            className="rounded-full border border-paper/12 px-4 py-2 text-xs font-semibold uppercase tracking-[0.18em] text-paper transition hover:border-moss/35 hover:text-moss"
          >
            System desk
          </Link>
          <button
            type="button"
            onClick={() => void handleSignOut()}
            className="rounded-full border border-paper/12 px-4 py-2 text-xs font-semibold uppercase tracking-[0.18em] text-paper transition hover:border-moss/35 hover:text-moss"
          >
            Sign out
          </button>
        </div>
      </div>
      <div className="deepglass overflow-hidden rounded-docket">
        <table className="w-full border-collapse text-left text-sm">
          <thead className="bg-paper/6 text-paper">
            <tr>
              <th className="px-4 py-3 font-mono text-[11px] uppercase tracking-[0.25em]">Type</th>
              <th className="px-4 py-3 font-mono text-[11px] uppercase tracking-[0.25em]">Status</th>
              <th className="px-4 py-3 font-mono text-[11px] uppercase tracking-[0.25em]">Verdict</th>
              <th className="px-4 py-3 font-mono text-[11px] uppercase tracking-[0.25em]">Confidence</th>
              <th className="px-4 py-3 font-mono text-[11px] uppercase tracking-[0.25em]">Created</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((row) => (
              <tr key={row.request_id} className="border-t border-paper/8 bg-transparent text-paper/74">
                <td className="px-4 py-4 font-semibold uppercase tracking-[0.16em] text-paper">{row.type}</td>
                <td className="px-4 py-4 capitalize">{row.status}</td>
                <td className="px-4 py-4 capitalize">{row.verdict ?? '-'}</td>
                <td className="px-4 py-4">
                  {row.confidence != null ? (
                    <div>
                      <p>{asConfidencePercent(row.confidence)}</p>
                      <p className="font-mono text-[11px] uppercase tracking-[0.18em] text-paper/42">{confidenceBand(row.confidence)}</p>
                    </div>
                  ) : (
                    '-'
                  )}
                </td>
                <td className="px-4 py-4">{new Date(row.created_at).toLocaleString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
