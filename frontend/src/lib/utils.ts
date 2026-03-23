import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function asPercent(value: number) {
  return `${Math.round(value * 100)}%`;
}

export function asConfidencePercent(value: number) {
  const bounded = Math.max(0, Math.min(1, value));
  if (bounded < 1) {
    return `${Math.min(99.9, bounded * 100).toFixed(1)}%`;
  }
  return '100.0%';
}

export function confidenceBand(value: number) {
  if (value >= 0.9) {
    return 'High model confidence';
  }
  if (value >= 0.7) {
    return 'Moderate model confidence';
  }
  return 'Low model confidence';
}
