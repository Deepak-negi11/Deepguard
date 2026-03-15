from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np
import torch
from torch import Tensor


def extract_frames(video_path: str | Path, sequence_length: int = 30, image_size: int = 224) -> list[np.ndarray]:
    """Extract evenly spaced RGB frames from a video file."""

    capture = cv2.VideoCapture(str(video_path))
    total_frames = int(capture.get(cv2.CAP_PROP_FRAME_COUNT)) or sequence_length
    frame_indexes = np.linspace(0, max(total_frames - 1, 0), num=sequence_length, dtype=int)
    frames: list[np.ndarray] = []
    for index in frame_indexes:
        capture.set(cv2.CAP_PROP_POS_FRAMES, int(index))
        success, frame = capture.read()
        if not success:
            break
        resized = cv2.resize(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB), (image_size, image_size))
        frames.append(resized)
    capture.release()
    if not frames:
        raise ValueError(f"No frames could be decoded from {video_path}")
    while len(frames) < sequence_length:
        frames.append(frames[-1].copy())
    return frames


def frames_to_tensor(frames: list[np.ndarray]) -> Tensor:
    array = np.stack(frames).astype("float32") / 255.0
    return torch.from_numpy(array).permute(0, 3, 1, 2)


def frames_to_frequency_maps(frames: list[np.ndarray]) -> Tensor:
    maps: list[np.ndarray] = []
    for frame in frames:
        grayscale = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
        fft = np.fft.fftshift(np.fft.fft2(grayscale))
        magnitude = np.log1p(np.abs(fft))
        normalized = cv2.normalize(magnitude, None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX).astype("uint8")
        maps.append(np.repeat(normalized[:, :, None], 3, axis=2))
    array = np.stack(maps).astype("float32") / 255.0
    return torch.from_numpy(array).permute(0, 3, 1, 2)
