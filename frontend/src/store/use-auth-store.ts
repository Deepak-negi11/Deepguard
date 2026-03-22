'use client';

import { create } from 'zustand';
import { createJSONStorage, persist } from 'zustand/middleware';

type AuthSession = {
  email: string;
  userId: number;
};

type AuthState = {
  email: string | null;
  userId: number | null;
  hasHydrated: boolean;
  setSession: (session: AuthSession) => void;
  clearSession: () => void;
  setHasHydrated: (value: boolean) => void;
};

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      email: null,
      userId: null,
      hasHydrated: false,
      setSession: (session) =>
        set({
          email: session.email,
          userId: session.userId,
        }),
      clearSession: () =>
        set({
          email: null,
          userId: null,
        }),
      setHasHydrated: (value) =>
        set({
          hasHydrated: value,
        }),
    }),
    {
      name: 'deepguard-auth',
      storage: createJSONStorage(() => localStorage),
      onRehydrateStorage: () => (state) => {
        state?.setHasHydrated(true);
      },
    },
  ),
);
