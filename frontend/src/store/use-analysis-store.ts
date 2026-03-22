'use client';

import { create } from 'zustand';

import type { AnalysisMode, TaskStatus } from '@/types/analysis';

type AnalysisState = {
  activeMode: AnalysisMode;
  latestTask: TaskStatus | null;
  setMode: (mode: AnalysisMode) => void;
  setLatestTask: (task: TaskStatus | null) => void;
};

export const useAnalysisStore = create<AnalysisState>((set) => ({
  activeMode: 'image',
  latestTask: null,
  setMode: (activeMode) => set({ activeMode }),
  setLatestTask: (latestTask) => set({ latestTask }),
}));
