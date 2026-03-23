"""
Fine-tune the DeepGuard fake-news classifier on the local CSV dataset.

Usage:
    docker compose exec backend python ml_models/fake_news_detector/train.py

This script:
    1. Loads training_dataset/final_dataset_v4.csv
    2. Normalizes labels into FAKE / REAL
    3. Fine-tunes hamzab/roberta-fake-news-classification
    4. Saves the best checkpoint to ml_models/weights/fake_news/hamzab-roberta-fake-news-classification
    5. Prints validation metrics
"""

from __future__ import annotations

import csv
import logging
import random
from dataclasses import dataclass
from pathlib import Path

import torch
from torch.utils.data import DataLoader, Dataset
from transformers import AutoModelForSequenceClassification, AutoTokenizer


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-8s %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


ROOT = Path(__file__).resolve().parent
DATASET_PATH = ROOT / "training_dataset" / "final_dataset_v4.csv"
OUTPUT_DIR = ROOT.parent / "weights" / "fake_news" / "hamzab-roberta-fake-news-classification"
BASE_MODEL = "hamzab/roberta-fake-news-classification"

LABEL_TO_ID = {"FAKE": 0, "REAL": 1}
ID_TO_LABEL = {value: key for key, value in LABEL_TO_ID.items()}


@dataclass(slots=True)
class TrainingConfig:
    epochs: int = 3
    batch_size: int = 4
    learning_rate: float = 2e-5
    max_length: int = 128
    validation_ratio: float = 0.2
    seed: int = 42
    unfreeze_last_layers: int = 1


@dataclass(slots=True)
class Record:
    text: str
    label: str


class NewsDataset(Dataset):
    def __init__(self, records: list[Record], tokenizer: AutoTokenizer, max_length: int) -> None:
        self._records = records
        self._tokenizer = tokenizer
        self._max_length = max_length

    def __len__(self) -> int:
        return len(self._records)

    def __getitem__(self, index: int) -> dict[str, torch.Tensor]:
        row = self._records[index]
        encoded = self._tokenizer(
            row.text,
            truncation=True,
            padding="max_length",
            max_length=self._max_length,
            return_tensors="pt",
        )
        return {
            "input_ids": encoded["input_ids"].squeeze(0),
            "attention_mask": encoded["attention_mask"].squeeze(0),
            "labels": torch.tensor(LABEL_TO_ID[row.label], dtype=torch.long),
        }


def normalize_label(raw_label: str) -> str | None:
    value = raw_label.strip().upper()
    if value in {"FAKE", "FALSE", "1"}:
        return "FAKE"
    if value in {"REAL", "TRUE", "0"}:
        return "REAL"
    return None


def load_records(dataset_path: Path) -> list[Record]:
    if not dataset_path.exists():
        raise FileNotFoundError(f"Dataset not found: {dataset_path}")

    records: list[Record] = []
    with dataset_path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if "text" not in (reader.fieldnames or []) or "label" not in (reader.fieldnames or []):
            raise ValueError("CSV must contain 'text' and 'label' columns")

        for row in reader:
            text = (row.get("text") or "").strip()
            normalized_label = normalize_label(row.get("label") or "")
            if not text or normalized_label is None:
                continue
            records.append(Record(text=text, label=normalized_label))

    if not records:
        raise ValueError("No valid training rows were found in the dataset")

    fake_count = sum(1 for row in records if row.label == "FAKE")
    real_count = len(records) - fake_count
    logger.info("Loaded %d rows (%d FAKE, %d REAL)", len(records), fake_count, real_count)
    return records


def stratified_split(records: list[Record], validation_ratio: float, seed: int) -> tuple[list[Record], list[Record]]:
    by_label: dict[str, list[Record]] = {"FAKE": [], "REAL": []}
    for row in records:
        by_label[row.label].append(row)

    rng = random.Random(seed)
    train_records: list[Record] = []
    validation_records: list[Record] = []

    for label, rows in by_label.items():
        rng.shuffle(rows)
        validation_count = max(1, int(round(len(rows) * validation_ratio)))
        validation_count = min(validation_count, len(rows) - 1) if len(rows) > 1 else 1
        validation_records.extend(rows[:validation_count])
        train_records.extend(rows[validation_count:])
        logger.info("%s split -> %d train / %d validation", label, len(rows[validation_count:]), len(rows[:validation_count]))

    rng.shuffle(train_records)
    rng.shuffle(validation_records)
    return train_records, validation_records


def evaluate(
    model: AutoModelForSequenceClassification,
    loader: DataLoader,
    device: torch.device,
) -> tuple[float, dict[str, int]]:
    model.eval()
    correct = 0
    total = 0
    tp = fp = tn = fn = 0

    with torch.no_grad():
        for batch in loader:
            input_ids = batch["input_ids"].to(device)
            attention_mask = batch["attention_mask"].to(device)
            labels = batch["labels"].to(device)

            logits = model(input_ids=input_ids, attention_mask=attention_mask).logits
            predictions = logits.argmax(dim=-1)

            correct += (predictions == labels).sum().item()
            total += labels.size(0)

            for predicted, actual in zip(predictions.tolist(), labels.tolist()):
                if predicted == 1 and actual == 1:
                    tp += 1
                elif predicted == 1 and actual == 0:
                    fp += 1
                elif predicted == 0 and actual == 0:
                    tn += 1
                else:
                    fn += 1

    accuracy = correct / total if total else 0.0
    return accuracy, {"tp": tp, "fp": fp, "tn": tn, "fn": fn, "total": total}


def format_report(stats: dict[str, int]) -> str:
    tp = stats["tp"]
    fp = stats["fp"]
    tn = stats["tn"]
    fn = stats["fn"]

    def _safe_div(numerator: float, denominator: float) -> float:
        return numerator / denominator if denominator else 0.0

    fake_precision = _safe_div(tn, tn + fn)
    fake_recall = _safe_div(tn, tn + fp)
    real_precision = _safe_div(tp, tp + fp)
    real_recall = _safe_div(tp, tp + fn)

    return (
        "Validation report\n"
        f"FAKE precision: {fake_precision:.3f}\n"
        f"FAKE recall:    {fake_recall:.3f}\n"
        f"REAL precision: {real_precision:.3f}\n"
        f"REAL recall:    {real_recall:.3f}\n"
        f"Rows checked:   {stats['total']}"
    )


def configure_trainable_parameters(
    model: AutoModelForSequenceClassification,
    unfreeze_last_layers: int,
) -> int:
    for parameter in model.parameters():
        parameter.requires_grad = False

    if hasattr(model, "classifier"):
        for parameter in model.classifier.parameters():
            parameter.requires_grad = True

    backbone = getattr(model, "roberta", None)
    encoder_layers = getattr(getattr(backbone, "encoder", None), "layer", None)
    if encoder_layers:
        for layer in encoder_layers[-unfreeze_last_layers:]:
            for parameter in layer.parameters():
                parameter.requires_grad = True

    trainable_count = sum(parameter.numel() for parameter in model.parameters() if parameter.requires_grad)
    return trainable_count


def train(config: TrainingConfig) -> None:
    logger.info("=" * 60)
    logger.info("DeepGuard fake-news fine-tuning")
    logger.info("Base model : %s", BASE_MODEL)
    logger.info("Dataset    : %s", DATASET_PATH)
    logger.info("Output     : %s", OUTPUT_DIR)
    logger.info("=" * 60)

    random.seed(config.seed)
    torch.manual_seed(config.seed)

    records = load_records(DATASET_PATH)
    train_records, validation_records = stratified_split(records, config.validation_ratio, config.seed)
    logger.info("Final split -> %d train / %d validation", len(train_records), len(validation_records))

    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL)
    train_dataset = NewsDataset(train_records, tokenizer, config.max_length)
    validation_dataset = NewsDataset(validation_records, tokenizer, config.max_length)

    train_loader = DataLoader(train_dataset, batch_size=config.batch_size, shuffle=True)
    validation_loader = DataLoader(validation_dataset, batch_size=config.batch_size)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    logger.info("Using device: %s", device)

    model = AutoModelForSequenceClassification.from_pretrained(BASE_MODEL, low_cpu_mem_usage=True)
    model.config.label2id = LABEL_TO_ID.copy()
    model.config.id2label = ID_TO_LABEL.copy()
    trainable_count = configure_trainable_parameters(model, config.unfreeze_last_layers)
    logger.info("Trainable parameters: %d", trainable_count)
    model.to(device)

    optimizer = torch.optim.AdamW(
        [parameter for parameter in model.parameters() if parameter.requires_grad],
        lr=config.learning_rate,
    )
    total_steps = max(1, len(train_loader) * config.epochs)
    scheduler = torch.optim.lr_scheduler.LinearLR(optimizer, start_factor=0.2, total_iters=max(1, total_steps // 10))

    best_accuracy = -1.0
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    global_step = 0

    for epoch in range(1, config.epochs + 1):
        model.train()
        running_loss = 0.0

        for step, batch in enumerate(train_loader, start=1):
            input_ids = batch["input_ids"].to(device)
            attention_mask = batch["attention_mask"].to(device)
            labels = batch["labels"].to(device)

            optimizer.zero_grad()
            outputs = model(input_ids=input_ids, attention_mask=attention_mask, labels=labels)
            loss = outputs.loss
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()
            global_step += 1
            if global_step <= total_steps // 10:
                scheduler.step()

            running_loss += loss.item()
            if step % 10 == 0 or step == len(train_loader):
                logger.info(
                    "Epoch %d/%d step %d/%d loss=%.4f",
                    epoch,
                    config.epochs,
                    step,
                    len(train_loader),
                    running_loss / step,
                )

        accuracy, stats = evaluate(model, validation_loader, device)
        logger.info("Epoch %d validation accuracy: %.2f%%", epoch, accuracy * 100)

        if accuracy > best_accuracy:
            best_accuracy = accuracy
            model.save_pretrained(str(OUTPUT_DIR))
            tokenizer.save_pretrained(str(OUTPUT_DIR))
            logger.info("Saved new best checkpoint to %s", OUTPUT_DIR)
            logger.info("\n%s", format_report(stats))

    logger.info("=" * 60)
    logger.info("Training complete")
    logger.info("Best validation accuracy: %.2f%%", best_accuracy * 100)
    logger.info("Saved weights: %s", OUTPUT_DIR)
    logger.info("Restart services with: docker compose restart backend celery_worker")
    logger.info("=" * 60)


if __name__ == "__main__":
    train(TrainingConfig())
