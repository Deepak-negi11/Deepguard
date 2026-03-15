import { notFound } from 'next/navigation';

import { AnalysisConsole } from '@/components/analysis-console';
import type { AnalysisMode } from '@/types/analysis';

const MODES: AnalysisMode[] = ['video', 'news', 'audio'];

export default async function AnalyzeModePage({ params }: { params: Promise<{ mode: string }> }) {
  const { mode } = await params;
  if (!MODES.includes(mode as AnalysisMode)) {
    notFound();
  }

  return <AnalysisConsole mode={mode as AnalysisMode} />;
}
