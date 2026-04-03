from __future__ import annotations

import argparse
import json
import logging
import tarfile
import urllib.request
import zipfile
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Literal

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

ROOT_DIR = Path(__file__).resolve().parent.parent
DATASETS_DIR = ROOT_DIR / "datasets"
REGISTRY_PATH = ROOT_DIR / "docs" / "dataset-registry.json"


@dataclass(slots=True)
class DatasetSpec:
    key: str
    display_name: str
    category: Literal["video", "news", "audio"]
    target_dir: str
    source_url: str
    access: Literal["direct", "manual", "kaggle"]
    archive_name: str | None = None
    notes: list[str] | None = None


DATASET_SPECS: dict[str, DatasetSpec] = {
    "liar": DatasetSpec(
        key="liar",
        display_name="LIAR Dataset",
        category="news",
        target_dir="news/liar",
        source_url="https://www.cs.ucsb.edu/~william/data/liar_dataset.zip",
        access="direct",
        archive_name="liar_dataset.zip",
        notes=[
            "Official dataset from UCSB.",
            "Contains labeled political statements for fake-news classification research.",
        ],
    ),
    "faceforensics": DatasetSpec(
        key="faceforensics",
        display_name="FaceForensics++",
        category="video",
        target_dir="video/faceforensics",
        source_url="https://github.com/ondyari/FaceForensics",
        access="manual",
        notes=[
            "Access requires accepting terms and using the official download tooling from the project repository.",
            "Recommended compression setting for experiments is c23 unless higher fidelity is required.",
        ],
    ),
    "celebdf": DatasetSpec(
        key="celebdf",
        display_name="Celeb-DF",
        category="video",
        target_dir="video/celebdf",
        source_url="https://github.com/yuezunli/celeb-deepfakeforensics",
        access="manual",
        notes=[
            "Access is gated through the official project instructions.",
            "Use this as a generalization benchmark, not your only training source.",
        ],
    ),
    "fake_news": DatasetSpec(
        key="fake_news",
        display_name="Fake and Real News Dataset",
        category="news",
        target_dir="news/fake_news_corpus",
        source_url="https://www.kaggle.com/datasets/clmentbisaillon/fake-and-real-news-dataset",
        access="kaggle",
        notes=[
            "Requires the Kaggle CLI or a manual download through Kaggle.",
            "Store the unmodified CSV files in the target directory and build your own train/validation splits.",
        ],
    ),
    "asvspoof": DatasetSpec(
        key="asvspoof",
        display_name="ASVspoof 2019",
        category="audio",
        target_dir="audio/asvspoof2019",
        source_url="https://datashare.ed.ac.uk/handle/10283/3336",
        access="manual",
        notes=[
            "Access requires accepting the terms on the official DataShare page.",
            "Download both Logical Access and Physical Access subsets if you want broad spoof coverage.",
        ],
    ),
}


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def write_registry() -> None:
    ensure_dir(REGISTRY_PATH.parent)
    REGISTRY_PATH.write_text(json.dumps([asdict(spec) for spec in DATASET_SPECS.values()], indent=2))


def download_file(url: str, destination: Path) -> None:
    if destination.exists():
        logger.info("File %s already exists. Skipping download.", destination)
        return
    logger.info("Downloading %s -> %s", url, destination)
    urllib.request.urlretrieve(url, destination)


def extract_archive(archive_path: Path, extract_dir: Path) -> None:
    logger.info("Extracting %s -> %s", archive_path.name, extract_dir)
    if archive_path.suffix == ".zip":
        with zipfile.ZipFile(archive_path, "r") as archive:
            archive.extractall(extract_dir)
        return

    with tarfile.open(archive_path, "r:*") as archive:
        archive.extractall(extract_dir)


def dataset_directory(spec: DatasetSpec) -> Path:
    target = DATASETS_DIR / spec.target_dir
    ensure_dir(target)
    return target


def print_manual_instructions(spec: DatasetSpec) -> None:
    logger.warning("%s requires manual acquisition.", spec.display_name)
    logger.warning("Official source: %s", spec.source_url)
    for note in spec.notes or []:
        logger.warning("- %s", note)


def print_kaggle_instructions(spec: DatasetSpec) -> None:
    logger.warning("%s is distributed via Kaggle.", spec.display_name)
    logger.warning("Source: %s", spec.source_url)
    logger.warning("Suggested command:")
    logger.warning("  kaggle datasets download clmentbisaillon/fake-and-real-news-dataset")
    for note in spec.notes or []:
        logger.warning("- %s", note)


def fetch_dataset(key: str) -> None:
    spec = DATASET_SPECS[key]
    target_dir = dataset_directory(spec)

    if spec.access == "direct":
        if spec.archive_name is None:
            raise ValueError(f"Direct dataset {spec.key} is missing archive metadata")
        archive_path = target_dir / spec.archive_name
        download_file(spec.source_url, archive_path)
        extract_archive(archive_path, target_dir)
        archive_path.unlink(missing_ok=True)
        logger.info("%s is ready under %s", spec.display_name, target_dir)
        return

    if spec.access == "manual":
        print_manual_instructions(spec)
        return

    print_kaggle_instructions(spec)


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepare DeepGuard datasets using official sources and access guidance.")
    parser.add_argument(
        "--dataset",
        choices=["all", *DATASET_SPECS.keys()],
        default="all",
        help="Dataset to prepare",
    )
    args = parser.parse_args()

    ensure_dir(DATASETS_DIR)
    write_registry()

    if args.dataset == "all":
        for key in DATASET_SPECS:
            fetch_dataset(key)
        return

    fetch_dataset(args.dataset)


if __name__ == "__main__":
    main()
