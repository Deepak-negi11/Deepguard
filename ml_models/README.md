# ML Models

These folders now contain implementation scaffolds for the future production model packages:

- `deepfake_detector/`
- `fake_news_detector/`
- `audio_detector/`
- `weights/` (local-only, ignored by git)

Each detector package now includes the module files expected by the project spec:

- `model.py`
- `inference.py`
- `train.py`
- `utils.py`

The video detector package also includes `preprocessing.py`.

The running backend still uses prototype analyzers from `backend/app/services/analyzers.py` so the full app can work before datasets, GPU training, and model artifact management are in place. The `ml_models/` code is the next integration layer, not yet the active runtime path.

## Large assets policy

- Do not commit model weights to git. Keep them under `ml_models/weights/` locally (this directory is ignored).
- For production, store weights in object storage or a model registry and download them at deploy/startup time.
