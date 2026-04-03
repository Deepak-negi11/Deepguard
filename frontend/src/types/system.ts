export interface DemoDatasetEntry {
  key: string;
  display_name: string;
  category: string;
  source_url: string;
  access: string;
  notes: string[];
}

export interface DemoSourceLink {
  label: string;
  category: 'news' | 'image' | 'general';
  url: string;
  purpose: string;
}

export interface ModelRegistryEntry {
  key: string;
  mode: 'image' | 'news';
  display_name: string;
  provider: string;
  model_id: string;
  source: 'prototype' | 'local_weights' | 'huggingface';
  active_version: string;
  weights_path?: string | null;
  dataset_version?: string | null;
  trained_at?: string | null;
  validation_accuracy?: number | null;
  notes: string[];
}

export interface ModelStatusEntry {
  mode: 'image' | 'news';
  analyzer_family: string;
  source: 'prototype' | 'local_weights' | 'huggingface';
  model_id: string;
  local_weights_available: boolean;
  local_weights_path?: string | null;
  warmup_on_startup: boolean;
  notes: string[];
}

export interface BenchmarkCaseEntry {
  key: string;
  mode: 'image' | 'news';
  title: string;
  input_kind: 'text' | 'file';
  expected_verdict: 'likely real' | 'likely fake' | 'uncertain';
  text?: string | null;
  url?: string | null;
  sample_path?: string | null;
  required: boolean;
  notes: string[];
}

export interface SystemStatus {
  app_name: string;
  environment: string;
  supported_modes: ('image' | 'news')[];
  demo_analyzers_enabled: boolean;
  celery_workers_enabled: boolean;
  upload_storage: string;
  news_url_fetch_enabled: boolean;
  datasets: DemoDatasetEntry[];
  sample_sources: DemoSourceLink[];
  model_registry: ModelRegistryEntry[];
  model_status: ModelStatusEntry[];
  benchmark_suite: BenchmarkCaseEntry[];
}
