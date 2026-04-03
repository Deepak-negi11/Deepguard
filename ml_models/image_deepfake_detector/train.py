import argparse
import logging
import os

try:
    import torch
    import torch.nn as nn
    import torch.optim as optim
    from torch.utils.data import DataLoader
    from torchvision.datasets import ImageFolder
except ImportError:
    pass

from ml_models.image_deepfake_detector.model import ImageDeepfakeDetector
from ml_models.image_deepfake_detector.preprocessing import get_transform

logger = logging.getLogger(__name__)

def train_model(data_dir: str, epochs: int, batch_size: int, lr: float):
    if get_transform is None:
        logger.error("torchvision not installed. Cannot run training.")
        return

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    logger.info(f"Using device: {device}")
    
    # Assuming standard ImageFolder layout: data_dir/real and data_dir/fake
    dataset = ImageFolder(root=data_dir, transform=get_transform)
    dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True, num_workers=4)
    
    model = ImageDeepfakeDetector(pretrained=True).to(device)
    criterion = nn.BCELoss()
    optimizer = optim.Adam(model.parameters(), lr=lr)
    
    os.makedirs("weights", exist_ok=True)
    
    for epoch in range(epochs):
        model.train()
        running_loss = 0.0
        
        for inputs, labels in dataloader:
            inputs = inputs.to(device)
            labels = labels.float().to(device).unsqueeze(1)
            
            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            
            loss.backward()
            optimizer.step()
            
            running_loss += loss.item()
            
        logger.info(f"Epoch {epoch+1}/{epochs} - Loss: {running_loss/len(dataloader):.4f}")
        
    torch.save(model.state_dict(), "weights/efficientnet_b4_genimage_finetuned.pth")
    logger.info("Training complete. model saved.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--data_dir", type=str, required=True, help="Path to GenImage dataset")
    parser.add_argument("--epochs", type=int, default=10)
    parser.add_argument("--batch_size", type=int, default=32)
    parser.add_argument("--lr", type=float, default=1e-4)
    args = parser.parse_args()
    
    train_model(args.data_dir, args.epochs, args.batch_size, args.lr)
