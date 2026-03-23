import numpy as np
import cv2

def compute_frequency_anomaly(image_path: str) -> float:
    """
    Computes a frequency-based anomaly score for deepfake detection.
    This is an implementation of Option C: Frequency-domain analysis (DCT/FFT).
    AI generated images often have distinctive high-frequency artifacts or 
    lack the natural noise distribution of real camera sensors.
    """
    try:
        # Load in grayscale
        img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        if img is None:
            return 0.5
            
        # Compute 2D Fast Fourier Transform
        f = np.fft.fft2(img)
        fshift = np.fft.fftshift(f)
        magnitude_spectrum = 20 * np.log(np.abs(fshift) + 1e-8)
        
        # Calculate radial average of the power spectrum (1D profile)
        h, w = magnitude_spectrum.shape
        center = (int(h/2), int(w/2))
        
        y, x = np.indices((h, w))
        r = np.sqrt((x - center[1])**2 + (y - center[0])**2)
        r = r.astype(np.int32)
        
        # Bin the frequencies by radius
        tbin = np.bincount(r.ravel(), magnitude_spectrum.ravel())
        nr = np.bincount(r.ravel())
        radialprofile = tbin / np.maximum(nr, 1)
        
        # Simple heuristic: AI images tend to have abnormal high-frequency drop-offs
        # We look at the ratio of high-freq to mid-freq energy
        mid_freq_energy = np.mean(radialprofile[len(radialprofile)//4:len(radialprofile)//2])
        high_freq_energy = np.mean(radialprofile[len(radialprofile)//2:])
        
        if mid_freq_energy == 0:
            return 0.5
            
        ratio = high_freq_energy / mid_freq_energy
        
        # Normalize to a 0.0 - 1.0 anomaly score
        # Calibration: ratio > 0.6 is common for clean mobile photos
        anomaly_score = max(0.0, min(1.0, 1.0 - (ratio / 0.7)))
        return float(anomaly_score)
        
    except Exception:
        return 0.5
