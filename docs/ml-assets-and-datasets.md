# ML assets and datasets

## Dataset registry

DeepGuard tracks dataset acquisition notes in `docs/dataset-registry.json`.

You can (re)generate the registry and prepare any direct-download datasets via:

```bash
python ml_models/dataset_downloader.py --dataset all
```

Notes:
- Some datasets are **manual** (you must accept terms and follow the upstream tooling).
- Some are **Kaggle** (requires Kaggle account + CLI).

## Model weights

This repo is designed to work without committed weights by using demo/prototype analyzers.

- **Do not commit weights to git**. Keep them in `ml_models/weights/` locally (ignored by `.gitignore`).
- For production deployments, store weights outside git (object storage / model registry) and fetch them at deploy/startup time.

## Runtime behavior

- Backend analyzer adapters live in `backend/app/services/analyzers.py`.
- If full ML inference isn’t available in the environment, the backend falls back to deterministic demo analyzers so requests still complete.

