import os

from huggingface_hub import snapshot_download


def main():
    print("==================================================")
    print("  DeepGuard Pre-Trained Model Downloader")
    print("  Fetching State-of-the-Art weights for Inference")
    print("==================================================\n")
    
    os.makedirs("/app/models/ateeqq-detector", exist_ok=True)
    os.makedirs("/app/models/fake-news-detector/hamzab-roberta-fake-news-classification", exist_ok=True)
    
    print("[*] Downloading Ateeqq/ai-vs-human-image-detector...")
    snapshot_download(
        repo_id="Ateeqq/ai-vs-human-image-detector",
        local_dir="/app/models/ateeqq-detector"
    )
    
    print("[*] Downloading hamzab/roberta-fake-news-classification...")
    snapshot_download(
        repo_id="hamzab/roberta-fake-news-classification",
        local_dir="/app/models/fake-news-detector/hamzab-roberta-fake-news-classification"
    )
    
    print("[+] All pre-trained models downloaded successfully.")

if __name__ == "__main__":
    main()
