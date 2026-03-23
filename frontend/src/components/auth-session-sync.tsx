'use client';

import { useEffect } from 'react';
import axios from 'axios';

import { fetchCurrentUser } from '@/lib/api';
import { useAuthStore } from '@/store/use-auth-store';

export function AuthSessionSync() {
  const { hasHydrated, setSession, clearSession } = useAuthStore();

  useEffect(() => {
    if (!hasHydrated) {
      return;
    }

    let cancelled = false;

    async function sync() {
      try {
        const user = await fetchCurrentUser();
        if (cancelled) return;
        setSession({
          email: user.email,
          userId: user.user_id,
        });
      } catch (error) {
        if (cancelled) return;
        if (axios.isAxiosError(error) && error.response && [401, 403].includes(error.response.status)) {
          clearSession();
        }
      }
    }

    void sync();

    return () => {
      cancelled = true;
    };
  }, [clearSession, hasHydrated, setSession]);

  return null;
}
