import torch
import cv2
import numpy as np
from src.csrnet import MCNN
from torchvision import transforms

class CrowdCounter:
    def __init__(self, model_path, device=None):
        if device is None:
            self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        else:
            self.device = device
            
        self.model = MCNN().to(self.device)
        self.model.load_state_dict(torch.load(model_path, map_location=self.device))
        self.model.eval()
        
        # Standard ImageNet normalization used during training
        self.transform = transforms.Compose([
            transforms.ToTensor(),
        ])

    def predict(self, frame):
        """
        Estimate crowd density and count for a single frame.
        """
        # Convert BGR (OpenCV) to RGB
        img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Resize to be divisible by 8 (standard for many dilated-backbone models)
        h, w = img.shape[:2]
        new_h = (h // 8) * 8
        new_w = (w // 8) * 8
        img_resized = cv2.resize(img, (new_w, new_h))
        
        input_tensor = self.transform(img_resized).unsqueeze(0).to(self.device)
        
        with torch.no_grad():
            output = self.model(input_tensor)
            
        # Density map is the output
        density_map = output.cpu().numpy().squeeze()
        
        # Ensure non-negative density values
        density_map = np.maximum(0, density_map)
        
        # The sum of density map values equals the predicted number of people
        count = float(density_map.sum())
        
        return density_map, count

    def get_heatmap(self, density_map, original_shape):
        """
        Convert density map to a color heatmap overlay.
        """
        # Normalize for visualization
        if density_map.max() > 0:
            nm_dmap = density_map / density_map.max()
        else:
            nm_dmap = density_map
            
        nm_dmap = (nm_dmap * 255).astype(np.uint8)
        heatmap = cv2.applyColorMap(nm_dmap, cv2.COLORMAP_JET)
        
        # Resize back to original frame size
        heatmap_resized = cv2.resize(heatmap, (original_shape[1], original_shape[0]))
        return heatmap_resized
