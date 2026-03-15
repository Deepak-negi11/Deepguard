'use client';

import { useState } from 'react';
import { LoaderCircle, LockKeyhole, UserRoundPlus } from 'lucide-react';

import { login, register, setToken as setApiToken } from '@/lib/api';
import { useAuthStore } from '@/store/use-auth-store';

type AuthMode = 'login' | 'register';

export function AuthCard({ title, copy }: { title: string; copy: string }) {
  const { setSession } = useAuthStore();
  const [mode, setMode] = useState<AuthMode>('login');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  async function handleSubmit(activeMode: AuthMode) {
    setMode(activeMode);
    setLoading(true);
    setError('');
    try {
      const session = activeMode === 'register' ? await register(email, password) : await login(email, password);
      setApiToken(session.access_token);
      setSession({
        token: session.access_token,
        email: session.email,
        userId: session.user_id,
      });
    } catch {
      setError(activeMode === 'register' ? 'Could not create the account. Try signing in if it already exists.' : 'Sign in failed. Check the credentials and try again.');
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="rounded-docket border border-soot/12 bg-white/80 p-8 shadow-docket">
      <div className="flex items-start gap-4">
        <span className="flex h-14 w-14 items-center justify-center rounded-full border border-ember/20 bg-ember/10 text-ember">
          {mode === 'register' ? <UserRoundPlus className="h-6 w-6" /> : <LockKeyhole className="h-6 w-6" />}
        </span>
        <div>
          <p className="font-mono text-xs uppercase tracking-[0.3em] text-soot/50">Secure access</p>
          <h2 className="mt-2 font-[family-name:var(--font-display)] text-4xl text-soot">{title}</h2>
          <p className="mt-3 max-w-2xl text-base leading-8 text-soot/70">{copy}</p>
        </div>
      </div>

      <div className="mt-8 grid gap-4 md:grid-cols-2">
        <label className="block">
          <span className="mb-2 block font-mono text-xs uppercase tracking-[0.28em] text-soot/50">Email</span>
          <input
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            placeholder="analyst@example.com"
            className="w-full rounded-[1rem] border border-soot/10 bg-paper/60 px-4 py-3 outline-none transition focus:border-ember/40"
          />
        </label>
        <label className="block">
          <span className="mb-2 block font-mono text-xs uppercase tracking-[0.28em] text-soot/50">Password</span>
          <input
            type="password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            placeholder="At least 8 characters"
            className="w-full rounded-[1rem] border border-soot/10 bg-paper/60 px-4 py-3 outline-none transition focus:border-ember/40"
          />
        </label>
      </div>

      {error ? <p className="mt-4 rounded-[1rem] border border-ember/20 bg-ember/8 px-4 py-3 text-sm text-ember">{error}</p> : null}

      <div className="mt-6 flex flex-col gap-3 sm:flex-row">
        <button
          type="button"
          disabled={loading || !email || password.length < 8}
          onClick={() => void handleSubmit('login')}
          className="inline-flex items-center justify-center gap-2 rounded-full bg-soot px-6 py-4 text-sm font-semibold uppercase tracking-[0.24em] text-paper transition hover:bg-ember disabled:cursor-not-allowed disabled:bg-soot/25"
        >
          {loading && mode === 'login' ? <LoaderCircle className="h-4 w-4 animate-spin" /> : null}
          Sign in
        </button>
        <button
          type="button"
          disabled={loading || !email || password.length < 8}
          onClick={() => void handleSubmit('register')}
          className="inline-flex items-center justify-center gap-2 rounded-full border border-soot/15 bg-paper px-6 py-4 text-sm font-semibold uppercase tracking-[0.24em] text-soot transition hover:border-ember/35 hover:text-ember disabled:cursor-not-allowed disabled:text-soot/30"
        >
          {loading && mode === 'register' ? <LoaderCircle className="h-4 w-4 animate-spin" /> : null}
          Create account
        </button>
      </div>
    </div>
  );
}
