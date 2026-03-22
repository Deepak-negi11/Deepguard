'use client';

import { useEffect } from 'react';

import { fetchCurrentUser } from '@/lib/api';
import { useAuthStore } from '@/store/use-auth-store';

export function AuthSessionSync() {
  const { setSession, clearSession } = useAuthStore();

  useEffect(() => {
    let cancelled = false;

    async function sync() {
      try {
        const user = await fetchCurrentUser();
        if (cancelled) return;
        setSession({
          email: user.email,
          userId: user.user_id,
        });
      } catch {
        if (cancelled) return;
        clearSession();
      }
    }

    void sync();

    return () => {
      cancelled = true;
    };
  }, [clearSession, setSession]);

  return null;
}
