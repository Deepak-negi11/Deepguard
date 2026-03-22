import os
from huggingface_hub import snapshot_download

def main():
    print("==================================================")
    print("  DeepGuard Pre-Trained Model Downloader")
    print("  Fetching State-of-the-Art weights for Inference")
    print("==================================================\n")
    
    os.makedirs("/app/models/ateeqq-detector", exist_ok=True)
    os.makedirs("/app/models/fake-news-detector", exist_ok=True)
    
    print("[*] Downloading Ateeqq/ai-vs-human-image-detector...")
    snapshot_download(
        repo_id="Ateeqq/ai-vs-human-image-detector",
        local_dir="/app/models/ateeqq-detector"
    )
    
    print("[*] Downloading mrm8488/bert-tiny-finetuned-fake-news-detection...")
    snapshot_download(
        repo_id="mrm8488/bert-tiny-finetuned-fake-news-detection",
        local_dir="/app/models/fake-news-detector"
    )
    
    print("[+] All pre-trained models downloaded successfully.")

if __name__ == "__main__":
    main()
