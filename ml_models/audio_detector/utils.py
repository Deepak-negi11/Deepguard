from __future__ import annotations

from pathlib import Path

import librosa
import torch


def load_audio_spectrogram(
    audio_path: str | Path,
    sample_rate: int = 16000,
    n_mels: int = 128,
    n_fft: int = 2048,
    hop_length: int = 512,
) -> torch.Tensor:
    waveform, _ = librosa.load(str(audio_path), sr=sample_rate, mono=True)
    mel = librosa.feature.melspectrogram(
        y=waveform,
        sr=sample_rate,
        n_mels=n_mels,
        n_fft=n_fft,
        hop_length=hop_length,
        fmax=8000,
    )
    mel_db = librosa.power_to_db(mel, ref=mel.max())
    tensor = torch.tensor(mel_db, dtype=torch.float32)
    if tensor.shape[-1] < 128:
        tensor = torch.nn.functional.pad(tensor, (0, 128 - tensor.shape[-1]))
    tensor = tensor[:, :128]
    return tensor.unsqueeze(0)


def equal_error_rate(scores: torch.Tensor, labels: torch.Tensor) -> float:
    thresholds = torch.linspace(0, 1, steps=101)
    best_gap = 1.0
    best_threshold = 0.5
    for threshold in thresholds:
        predicted = (scores >= threshold).float()
        false_accept = ((predicted == 1) & (labels == 0)).float().mean().item()
        false_reject = ((predicted == 0) & (labels == 1)).float().mean().item()
        gap = abs(false_accept - false_reject)
        if gap < best_gap:
            best_gap = gap
            best_threshold = float((false_accept + false_reject) / 2)
    return best_threshold
