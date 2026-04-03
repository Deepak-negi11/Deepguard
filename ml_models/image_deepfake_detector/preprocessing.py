from PIL import Image

try:
    from torchvision import transforms
    
    # Preprocessing transforms for EfficientNet
    get_transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(
            mean=[0.485, 0.456, 0.406], 
            std=[0.229, 0.224, 0.225]
        )
    ])
except ImportError:
    get_transform = None

def preprocess_image(image_path: str):
    image = Image.open(image_path).convert('RGB')
    if get_transform is None:
        return None
    tensor = get_transform(image)
    return tensor.unsqueeze(0)  # Add batch dimension

def compute_noise_uniformity(image_path: str) -> float:
    """Calculates noise variance uniformity across blocks using cv2."""
    try:
        import cv2
        import numpy as np
        
        img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        if img is None:
            return 0.5
            
        # Apply a simple high-pass filter to extract noise
        laplacian = cv2.Laplacian(img, cv2.CV_64F)
        
        # Split into blocks (e.g., 8x8) and compute variance per block
        h, w = laplacian.shape
        block_size = 16
        variances = []
        for y in range(0, h - block_size, block_size):
            for x in range(0, w - block_size, block_size):
                block = laplacian[y:y+block_size, x:x+block_size]
                variances.append(np.var(block))
                
        # Unnaturally low standard deviation of block variances implies uniform noise (e.g., GANs)
        std_var = np.std(variances)
        # Normalize to an anomaly score
        # Calibration: 1200 is more realistic for modern high-res denoised phones
        score = max(0.0, min(1.0, 1.0 - (std_var / 1200.0)))
        return float(score)
    except Exception:
        return 0.5
