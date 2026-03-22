'use client';

import { useEffect, useState } from 'react';

import { fetchHistory, logout } from '@/lib/api';
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
        setRows(history.results);
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
    return <p className="rounded-[1rem] border border-dashed border-soot/15 bg-paper/65 px-4 py-5 text-sm text-soot/65">Restoring your session...</p>;
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
    return <p className="rounded-[1rem] border border-dashed border-soot/15 bg-paper/65 px-4 py-5 text-sm text-soot/65">{error}</p>;
  }

  if (!rows.length) {
    return <p className="rounded-[1rem] border border-dashed border-soot/15 bg-paper/65 px-4 py-5 text-sm text-soot/65">No investigations yet. Run the first case from any analysis desk.</p>;
  }

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center justify-between gap-3 rounded-[1rem] border border-soot/10 bg-paper/70 px-4 py-4 text-sm text-soot/70">
        <span>Signed in as {email}</span>
        <button
          type="button"
          onClick={() => void handleSignOut()}
          className="rounded-full border border-soot/15 px-4 py-2 text-xs font-semibold uppercase tracking-[0.18em] text-soot transition hover:border-ember/35 hover:text-ember"
        >
          Sign out
        </button>
      </div>
      <div className="overflow-hidden rounded-docket border border-soot/10 bg-white/85 shadow-docket">
        <table className="w-full border-collapse text-left text-sm">
          <thead className="bg-soot text-paper">
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
              <tr key={row.request_id} className="border-t border-soot/8 bg-paper/70 text-soot/75">
                <td className="px-4 py-4 font-semibold uppercase tracking-[0.16em] text-soot">{row.type}</td>
                <td className="px-4 py-4 capitalize">{row.status}</td>
                <td className="px-4 py-4 capitalize">{row.verdict ?? '-'}</td>
                <td className="px-4 py-4">{row.confidence ? `${Math.round(row.confidence * 100)}%` : '-'}</td>
                <td className="px-4 py-4">{new Date(row.created_at).toLocaleString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
