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
    <div className="deepglass rounded-docket p-8 text-paper">
      <div className="flex items-start gap-4">
        <span className="flex h-14 w-14 items-center justify-center rounded-full border border-paper/12 bg-paper/6 text-moss">
          {mode === 'register' ? <UserRoundPlus className="h-6 w-6" /> : <LockKeyhole className="h-6 w-6" />}
        </span>
        <div>
          <p className="font-mono text-xs uppercase tracking-[0.3em] text-paper/44">Secure access</p>
          <h2 className="mt-2 font-[family-name:var(--font-display)] text-4xl text-paper">{title}</h2>
          <p className="mt-3 max-w-2xl text-base leading-8 text-paper/66">{copy}</p>
        </div>
      </div>

      <div className="mt-8 grid gap-4 md:grid-cols-2">
        <label className="block">
          <span className="mb-2 block font-mono text-xs uppercase tracking-[0.28em] text-paper/44">Email</span>
          <input
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            placeholder="analyst@example.com"
            className="w-full rounded-[1rem] border border-paper/12 bg-paper/6 px-4 py-3 text-paper outline-none transition placeholder:text-paper/28 focus:border-moss/40"
          />
        </label>
        <label className="block">
          <span className="mb-2 block font-mono text-xs uppercase tracking-[0.28em] text-paper/44">Password</span>
          <input
            type="password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            placeholder="At least 8 characters"
            className="w-full rounded-[1rem] border border-paper/12 bg-paper/6 px-4 py-3 text-paper outline-none transition placeholder:text-paper/28 focus:border-moss/40"
          />
        </label>
      </div>

      {error ? <p className="mt-4 rounded-[1rem] border border-ember/20 bg-ember/10 px-4 py-3 text-sm text-paper">{error}</p> : null}

      <div className="mt-6 flex flex-col gap-3 sm:flex-row">
        <button
          type="button"
          disabled={loading || !email || password.length < 8}
          onClick={() => void handleSubmit('login')}
          className="inline-flex items-center justify-center gap-2 rounded-full bg-paper px-6 py-4 text-sm font-semibold uppercase tracking-[0.24em] text-soot transition hover:bg-moss disabled:cursor-not-allowed disabled:bg-paper/25"
        >
          {loading && mode === 'login' ? <LoaderCircle className="h-4 w-4 animate-spin" /> : null}
          Sign in
        </button>
        <button
          type="button"
          disabled={loading || !email || password.length < 8}
          onClick={() => void handleSubmit('register')}
          className="inline-flex items-center justify-center gap-2 rounded-full border border-paper/12 bg-paper/6 px-6 py-4 text-sm font-semibold uppercase tracking-[0.24em] text-paper transition hover:border-moss/35 hover:text-moss disabled:cursor-not-allowed disabled:text-paper/30"
        >
          {loading && mode === 'register' ? <LoaderCircle className="h-4 w-4 animate-spin" /> : null}
          Create account
        </button>
      </div>

      <div className="mt-5 text-sm text-paper/62">
        {mode === 'register' ? (
          <p>
            Already have an account?{' '}
            <Link href="/signin" className="font-semibold text-moss transition hover:text-paper">
              Sign in
            </Link>
          </p>
        ) : (
          <p>
            Need a new account?{' '}
            <Link href="/signup" className="font-semibold text-moss transition hover:text-paper">
              Create one
            </Link>
          </p>
        )}
      </div>
    </div>
  );
}
