'use client';

import { create } from 'zustand';
import { createJSONStorage, persist } from 'zustand/middleware';

type AuthSession = {
  token: string;
  email: string;
  userId: number;
};

type AuthState = {
  token: string | null;
  email: string | null;
  userId: number | null;
  setSession: (session: AuthSession) => void;
  clearSession: () => void;
};

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      token: null,
      email: null,
      userId: null,
      setSession: (session) =>
        set({
          token: session.token,
          email: session.email,
          userId: session.userId,
        }),
      clearSession: () =>
        set({
          token: null,
          email: null,
          userId: null,
        }),
    }),
    {
      name: 'deepguard-auth',
      storage: createJSONStorage(() => localStorage),
    },
  ),
);
