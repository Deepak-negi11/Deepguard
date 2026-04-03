'use client';

import { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { LoaderCircle, LockKeyhole, UserRoundPlus } from 'lucide-react';

import { getApiErrorMessage, login, register } from '@/lib/api';
import { useAuthStore } from '@/store/use-auth-store';

type AuthMode = 'login' | 'register';

export function AuthCard({
  title,
  copy,
  defaultMode = 'login',
}: {
  title: string;
  copy: string;
  defaultMode?: AuthMode;
}) {
  const { setSession } = useAuthStore();
  const router = useRouter();
  const [mode, setMode] = useState<AuthMode>(defaultMode);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  async function handleSubmit(activeMode: AuthMode) {
    setMode(activeMode);
    setLoading(true);
    setError('');
    try {
      const normalizedEmail = email.trim().toLowerCase();
      const session = activeMode === 'register' ? await register(normalizedEmail, password) : await login(normalizedEmail, password);
      setSession({
        email: session.email,
        userId: session.user_id,
      });
      router.push('/analyze/news');
      router.refresh();
    } catch (error) {
      setError(
        getApiErrorMessage(
          error,
          activeMode === 'register'
            ? 'Could not create the account. Try signing in if it already exists.'
            : 'Sign in failed. Check the credentials and try again.',
        ),
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="deepglass rounded-docket p-8 text-white">
      <div className="flex items-start gap-4">
        <span className="flex h-14 w-14 items-center justify-center rounded-full border border-white/12 bg-white/6 text-[#6ba4ff]">
          {mode === 'register' ? <UserRoundPlus className="h-6 w-6" /> : <LockKeyhole className="h-6 w-6" />}
        </span>
        <div>
          <p className="font-[family-name:var(--font-body)] text-xs font-semibold uppercase tracking-[0.25em] text-white/55">
            Secure access
          </p>
          <h2 className="mt-2 font-[family-name:var(--font-headline)] text-3xl font-bold tracking-[-0.02em] text-white md:text-4xl">
            {title}
          </h2>
          <p className="mt-3 max-w-2xl font-[family-name:var(--font-body)] text-base leading-[1.7] text-white/70">
            {copy}
          </p>
        </div>
      </div>

      <div className="mt-8 grid gap-5 md:grid-cols-2">
        <label className="block">
          <span className="mb-2 block font-[family-name:var(--font-body)] text-xs font-bold uppercase tracking-[0.2em] text-white/65">
            Email
          </span>
          <input
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            placeholder="analyst@example.com"
            className="w-full rounded-[1rem] border border-white/12 bg-white/6 px-4 py-3.5 font-[family-name:var(--font-body)] text-[15px] text-white outline-none transition placeholder:text-white/35 focus:border-[#6ba4ff]/50 focus:ring-1 focus:ring-[#6ba4ff]/20"
          />
        </label>
        <label className="block">
          <span className="mb-2 block font-[family-name:var(--font-body)] text-xs font-bold uppercase tracking-[0.2em] text-white/65">
            Password
          </span>
          <input
            type="password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            placeholder="At least 8 characters"
            className="w-full rounded-[1rem] border border-white/12 bg-white/6 px-4 py-3.5 font-[family-name:var(--font-body)] text-[15px] text-white outline-none transition placeholder:text-white/35 focus:border-[#6ba4ff]/50 focus:ring-1 focus:ring-[#6ba4ff]/20"
          />
        </label>
      </div>

      {error ? (
        <p className="mt-4 rounded-[1rem] border border-red-400/20 bg-red-500/10 px-4 py-3 font-[family-name:var(--font-body)] text-sm font-medium text-white">
          {error}
        </p>
      ) : null}

      <div className="mt-7 flex flex-col gap-3 sm:flex-row">
        <button
          type="button"
          disabled={loading || !email || password.length < 8}
          onClick={() => void handleSubmit('login')}
          className="inline-flex items-center justify-center gap-2 rounded-full bg-white px-7 py-4 font-[family-name:var(--font-body)] text-sm font-bold uppercase tracking-[0.18em] text-[#0a0e1a] transition-all duration-300 hover:bg-[#6ba4ff] hover:text-white disabled:cursor-not-allowed disabled:bg-white/20 disabled:text-white/40"
        >
          {loading && mode === 'login' ? <LoaderCircle className="h-4 w-4 animate-spin" /> : null}
          Sign in
        </button>
        <button
          type="button"
          disabled={loading || !email || password.length < 8}
          onClick={() => void handleSubmit('register')}
          className="inline-flex items-center justify-center gap-2 rounded-full border border-white/15 bg-white/6 px-7 py-4 font-[family-name:var(--font-body)] text-sm font-bold uppercase tracking-[0.18em] text-white/80 transition-all duration-300 hover:border-[#6ba4ff]/40 hover:text-[#6ba4ff] disabled:cursor-not-allowed disabled:text-white/25"
        >
          {loading && mode === 'register' ? <LoaderCircle className="h-4 w-4 animate-spin" /> : null}
          Create account
        </button>
      </div>

      <div className="mt-5 font-[family-name:var(--font-body)] text-sm text-white/60">
        {mode === 'register' ? (
          <p>
            Already have an account?{' '}
            <Link href="/signin" className="font-semibold text-[#6ba4ff] transition hover:text-white">
              Sign in
            </Link>
          </p>
        ) : (
          <p>
            Need a new account?{' '}
            <Link href="/signup" className="font-semibold text-[#6ba4ff] transition hover:text-white">
              Create one
            </Link>
          </p>
        )}
      </div>
    </div>
  );
}
