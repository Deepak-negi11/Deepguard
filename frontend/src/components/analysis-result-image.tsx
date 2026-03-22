import Image from 'next/image';
import { Camera, Eye, Layers, Settings2, ShieldQuestion, SquareDashedMousePointer } from 'lucide-react';

import { asPercent, cn } from '@/lib/utils';
import type { AnalysisResult } from '@/types/analysis';

export function AnalysisResultImage({ result }: { result: AnalysisResult }) {
  const isImage = result.input_profile.mode === 'image';
  if (!isImage) return null;

  // Since we don't have the original image URL directly available in the frontend payload right now,
  // we'll display a generic placeholder or the gradcam URL if it exists.
  // In a real app, the backend would return `source_image_url` alongside `gradcam_overlay_url`.
  const overlayUrl = result.gradcam_overlay_url;
  const breakDownVals = result.breakdown || {};
  
  const signals = [
    { label: 'EXIF Metadata', key: 'exif_anomaly', icon: Camera, desc: 'Camera signature and software tags' },
    { label: 'Noise Uniformity', key: 'noise_pattern_score', icon: Settings2, desc: 'Block variance analysis' },
    { label: 'Frequency Artifacts', key: 'frequency_artifact_score', icon: Layers, desc: 'DCT/FFT high-freq anomaly' },
    { label: 'Model Confidence', key: 'model_confidence', icon: Eye, desc: 'EfficientNet-B4 patch score' },
  ];

  return (
    <div className="grid gap-6 lg:grid-cols-[1.1fr_0.9fr]">
      {/* Visual Sandbox */}
      <div className="flex flex-col overflow-hidden rounded-[1.3rem] border border-soot/10 bg-paper/70 shadow-sm">
        <div className="border-b border-soot/10 bg-white/60 px-5 py-4">
          <p className="font-mono text-xs uppercase tracking-[0.3em] text-soot/60">Image Forensics Lab</p>
          <div className="mt-2 flex items-center justify-between">
            <h4 className="font-[family-name:var(--font-display)] text-xl text-soot">Grad-CAM Overlay</h4>
            <span className="inline-flex items-center gap-1.5 rounded-full border border-ember/20 bg-ember/10 px-3 py-1 text-[10px] font-semibold uppercase tracking-widest text-ember">
              <SquareDashedMousePointer className="h-3 w-3" />
              GenImage V1
            </span>
          </div>
        </div>
        <div className="relative flex min-h-[300px] flex-1 items-center justify-center bg-[radial-gradient(ellipse_at_center,_var(--tw-gradient-stops))] from-soot/5 to-paper/80 p-6">
          {overlayUrl ? (
            <div className="relative aspect-video w-full max-w-sm overflow-hidden rounded-[1rem] border border-soot/15 shadow-xl">
              <img
                src={overlayUrl}
                alt="Grad-CAM Activation Map"
                className="h-full w-full object-cover"
                onError={(e) => {
                  (e.target as HTMLImageElement).style.display = 'none';
                }}
              />
              <div className="absolute inset-x-0 bottom-0 bg-gradient-to-t from-soot/80 to-transparent p-4 pb-3">
                <p className="font-mono text-[10px] uppercase tracking-widest text-paper/80">Heatmap Activation Zone</p>
              </div>
            </div>
          ) : (
            <div className="flex flex-col items-center justify-center space-y-3 text-soot/40">
              <ShieldQuestion className="h-12 w-12 opacity-50" />
              <p className="max-w-[200px] text-center text-sm">No spatial heatmap generated for this inference run.</p>
            </div>
          )}
        </div>
      </div>

      {/* Signal Breakdown */}
      <div className="rounded-[1.3rem] border border-soot/10 bg-soot p-6 text-paper shadow-sm">
        <p className="font-mono text-xs uppercase tracking-[0.3em] text-paper/50">Component Telemetry</p>
        <h4 className="mt-2 font-[family-name:var(--font-display)] text-2xl text-paper">Forensic Signals</h4>
        <p className="mt-2 text-sm leading-6 text-paper/70">
          The synthesized authenticity score is a weighted combination of these separate heuristic detectors. A higher anomaly signal implies synthetic generation.
        </p>
        
        <div className="mt-6 space-y-4">
          {signals.map(({ label, key, icon: Icon, desc }) => {
            const val = breakDownVals[key] ?? 0;
            const isHighRisk = val > 0.6;
            return (
              <div key={key} className={cn("rounded-xl border p-4 transition-colors", isHighRisk ? "border-ember/40 bg-ember/10" : "border-paper/10 bg-paper/5")}>
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-3">
                    <div className={cn("flex h-8 w-8 items-center justify-center rounded-full border", isHighRisk ? "border-ember/30 text-ember bg-soot/50" : "border-paper/20 text-paper/80 bg-soot")}>
                      <Icon className="h-4 w-4" />
                    </div>
                    <div>
                      <p className="font-mono text-[11px] uppercase tracking-[0.2em]">{label}</p>
                      <p className="mt-0.5 text-xs text-paper/50">{desc}</p>
                    </div>
                  </div>
                  <span className={cn("font-mono text-lg", isHighRisk ? "text-ember" : "text-paper")}>
                    {asPercent(val)}
                  </span>
                </div>
                <div className="mt-4 h-1.5 w-full overflow-hidden rounded-full bg-soot">
                  <div className={cn("h-full rounded-full", isHighRisk ? "bg-ember shadow-[0_0_10px_var(--tw-shadow-color)] shadow-ember/50" : "bg-paper/40")} style={{ width: `${Math.max(2, val * 100)}%` }} />
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
