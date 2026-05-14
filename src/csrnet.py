import torch
import torch.nn as nn

class MCNN(nn.Module):
    """
    Multi-Column Convolutional Neural Network (MCNN)
    Exactly matching the architecture in crowd-density-estimation.ipynb
    """
    def __init__(self):
        super(MCNN, self).__init__()
        
        self.column1 = nn.Sequential(
            nn.Conv2d(3, 8, 9, padding='same'),
            nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Conv2d(8, 16, 7, padding='same'),
            nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Conv2d(16, 32, 7, padding='same'),
            nn.ReLU(),
            nn.Conv2d(32, 16, 7, padding='same'),
            nn.ReLU(),
            nn.Conv2d(16, 8, 7, padding='same'),
            nn.ReLU(),
        )

        self.column2 = nn.Sequential(
            nn.Conv2d(3, 10, 7, padding='same'),
            nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Conv2d(10, 20, 5, padding='same'),
            nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Conv2d(20, 40, 5, padding='same'),
            nn.ReLU(),
            nn.Conv2d(40, 20, 5, padding='same'),
            nn.ReLU(),
            nn.Conv2d(20, 10, 5, padding='same'),
            nn.ReLU(),
        )

        self.column3 = nn.Sequential(
            nn.Conv2d(3, 12, 5, padding='same'),
            nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Conv2d(12, 24, 3, padding='same'),
            nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Conv2d(24, 48, 3, padding='same'),
            nn.ReLU(),
            nn.Conv2d(48, 24, 3, padding='same'),
            nn.ReLU(),
            nn.Conv2d(24, 12, 3, padding='same'),
            nn.ReLU(),
        )
        
        self.fusion_layer = nn.Sequential(
            nn.Conv2d(30, 1, 1, padding=0),
        )

    def forward(self, x):
        x1 = self.column1(x)
        x2 = self.column2(x)
        x3 = self.column3(x)
        
        x = torch.cat((x1, x2, x3), 1)
        x = self.fusion_layer(x)
        return x
