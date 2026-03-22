export type AnalysisMode = 'image' | 'news' | 'audio';

export type EvidenceItem = {
  category: string;
  severity: 'low' | 'medium' | 'high';
  description: string;
  timestamp?: number | null;
  details?: Record<string, string | number | boolean | null>;
  visualization_hint?: string | null;
};

export type AnalysisInputProfile = {
  mode: AnalysisMode;
  filename?: string | null;
  content_type?: string | null;
  size_bytes?: number | null;
  url_domain?: string | null;
  text_length?: number | null;
  analyzer_family: string;
};

export type AnalysisResult = {
  authenticity_score: number;
  verdict: string;
  confidence: number;
  summary: string;
  disclaimer: string;
  breakdown: Record<string, number>;
  evidence: EvidenceItem[];
  recommended_actions: string[];
  input_profile: AnalysisInputProfile;
  processing_time_seconds: number;
  model_version: string;
  gradcam_overlay_url?: string | null;
};

export type TaskStatus = {
  task_id: string;
  status: string;
  progress: number;
  current_step: string;
  result?: AnalysisResult | null;
};

export type HistoryItem = {
  request_id: string;
  type: AnalysisMode;
  status: string;
  verdict?: string | null;
  confidence?: number | null;
  created_at: string;
};
