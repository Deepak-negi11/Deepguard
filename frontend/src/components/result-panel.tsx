import { AlertTriangle, BadgeCheck, Clock3, Fingerprint } from 'lucide-react';

import { AnalysisResultImage } from './analysis-result-image';
import { asPercent } from '@/lib/utils';
import type { AnalysisResult } from '@/types/analysis';

const verdictTone: Record<string, string> = {
  'likely real': 'text-moss border-moss/30 bg-moss/10',
  uncertain: 'text-brass border-brass/30 bg-brass/10',
  'likely fake': 'text-ember border-ember/30 bg-ember/10',
};

function formatBytes(value?: number | null) {
  if (!value) {
    return 'n/a';
  }
  if (value < 1024) {
    return `${value} B`;
  }
  if (value < 1024 * 1024) {
    return `${(value / 1024).toFixed(1)} KB`;
  }
  return `${(value / (1024 * 1024)).toFixed(2)} MB`;
}

export function ResultPanel({ result }: { result: AnalysisResult }) {
  return (
    <div className="space-y-5 rounded-docket border border-soot/12 bg-white/80 p-6 shadow-docket">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <p className="font-mono text-xs uppercase tracking-[0.3em] text-soot/50">Latest verdict</p>
          <h3 className="mt-2 font-[family-name:var(--font-display)] text-4xl text-soot">{result.verdict}</h3>
        </div>
        <span className={`inline-flex rounded-full border px-4 py-2 text-xs font-semibold uppercase tracking-[0.22em] ${verdictTone[result.verdict] ?? 'text-soot border-soot/20 bg-soot/5'}`}>
          {asPercent(result.confidence)} confidence
        </span>
      </div>

      <div className="rounded-[1.3rem] border border-ember/15 bg-ember/8 p-5 text-soot">
        <p className="font-mono text-xs uppercase tracking-[0.3em] text-soot/50">Analyst summary</p>
        <p className="mt-3 text-base leading-8 text-soot/80">{result.summary}</p>
        <p className="mt-4 text-xs uppercase tracking-[0.16em] text-soot/48">{result.disclaimer}</p>
      </div>

      {result.input_profile.mode === 'image' && (
        <AnalysisResultImage result={result} />
      )}

      <div className="grid gap-4 md:grid-cols-3">
        <article className="rounded-[1.3rem] border border-soot/10 bg-paper/75 p-4">
          <Fingerprint className="h-5 w-5 text-ember" />
          <p className="mt-3 text-sm text-soot/60">Authenticity score</p>
          <p className="font-[family-name:var(--font-display)] text-4xl text-soot">{asPercent(result.authenticity_score)}</p>
        </article>
        <article className="rounded-[1.3rem] border border-soot/10 bg-paper/75 p-4">
          <Clock3 className="h-5 w-5 text-ember" />
          <p className="mt-3 text-sm text-soot/60">Processing time</p>
          <p className="font-[family-name:var(--font-display)] text-4xl text-soot">{result.processing_time_seconds}s</p>
        </article>
        <article className="rounded-[1.3rem] border border-soot/10 bg-paper/75 p-4">
          <BadgeCheck className="h-5 w-5 text-ember" />
          <p className="mt-3 text-sm text-soot/60">Model version</p>
          <p className="font-[family-name:var(--font-display)] text-2xl text-soot">{result.model_version}</p>
        </article>
      </div>

      <div className="grid gap-4 lg:grid-cols-[0.85fr_1.15fr]">
        <div className="rounded-[1.3rem] border border-soot/10 bg-paper/70 p-5">
          <p className="font-mono text-xs uppercase tracking-[0.3em] text-soot/50">Signal breakdown</p>
          <div className="mt-4 space-y-3">
            {Object.entries(result.breakdown).map(([label, value]) => (
              <div key={label}>
                <div className="mb-2 flex items-center justify-between text-sm text-soot/70">
                  <span className="capitalize">{label.replaceAll('_', ' ')}</span>
                  <span>{asPercent(value)}</span>
                </div>
                <div className="h-2 rounded-full bg-soot/8">
                  <div className="h-2 rounded-full bg-ember" style={{ width: `${Math.round(value * 100)}%` }} />
                </div>
              </div>
            ))}
          </div>
        </div>
        <div className="rounded-[1.3rem] border border-soot/10 bg-soot p-5 text-paper">
          <p className="font-mono text-xs uppercase tracking-[0.3em] text-paper/55">Evidence ledger</p>
          <div className="mt-4 space-y-4">
            {result.evidence.map((item) => (
              <article key={`${item.category}-${item.description}`} className="rounded-[1.15rem] border border-paper/10 bg-paper/5 p-4">
                <div className="flex items-center justify-between gap-4">
                  <p className="font-semibold uppercase tracking-[0.2em] text-paper">{item.category}</p>
                  <span className="rounded-full border border-paper/15 px-3 py-1 text-[11px] uppercase tracking-[0.22em] text-paper/70">{item.severity}</span>
                </div>
                <p className="mt-3 text-sm leading-7 text-paper/72">{item.description}</p>
                {item.visualization_hint ? (
                  <p className="mt-3 text-[11px] uppercase tracking-[0.18em] text-paper/45">Visualization: {item.visualization_hint.replaceAll('_', ' ')}</p>
                ) : null}
                {item.details && Object.keys(item.details).length ? (
                  <div className="mt-3 flex flex-wrap gap-2">
                    {Object.entries(item.details).map(([label, value]) => (
                      <span key={label} className="rounded-full border border-paper/10 px-3 py-1 text-[11px] uppercase tracking-[0.16em] text-paper/65">
                        {label.replaceAll('_', ' ')}: {String(value)}
                      </span>
                    ))}
                  </div>
                ) : null}
                {item.timestamp ? (
                  <p className="mt-3 inline-flex items-center gap-2 text-xs uppercase tracking-[0.2em] text-paper/45">
                    <AlertTriangle className="h-3.5 w-3.5" />
                    Event marker: {item.timestamp}s
                  </p>
                ) : null}
              </article>
            ))}
          </div>
        </div>
      </div>

      <div className="grid gap-4 lg:grid-cols-[0.8fr_1.2fr]">
        <div className="rounded-[1.3rem] border border-soot/10 bg-paper/70 p-5">
          <p className="font-mono text-xs uppercase tracking-[0.3em] text-soot/50">Input profile</p>
          <div className="mt-4 grid gap-3">
            {[
              ['Mode', result.input_profile.mode],
              ['Analyzer family', result.input_profile.analyzer_family],
              ['Filename', result.input_profile.filename ?? 'n/a'],
              ['Content type', result.input_profile.content_type ?? 'n/a'],
              ['Source domain', result.input_profile.url_domain ?? 'n/a'],
              ['Text length', result.input_profile.text_length ? `${result.input_profile.text_length} chars` : 'n/a'],
              ['Payload size', formatBytes(result.input_profile.size_bytes)],
            ].map(([label, value]) => (
              <div key={label} className="flex items-center justify-between gap-4 rounded-[1rem] border border-soot/10 bg-white/70 px-4 py-3 text-sm text-soot/70">
                <span className="uppercase tracking-[0.16em] text-soot/45">{label}</span>
                <span className="text-right font-medium text-soot">{value}</span>
              </div>
            ))}
          </div>
        </div>

        <div className="rounded-[1.3rem] border border-soot/10 bg-paper/70 p-5">
          <p className="font-mono text-xs uppercase tracking-[0.3em] text-soot/50">Recommended actions</p>
          <div className="mt-4 space-y-3">
            {result.recommended_actions.map((action) => (
              <div key={action} className="rounded-[1rem] border border-soot/10 bg-white/70 px-4 py-4 text-sm leading-7 text-soot/75">
                {action}
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
