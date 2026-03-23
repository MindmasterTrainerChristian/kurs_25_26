import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import datasets, transforms
import matplotlib.pyplot as plt


# Data Loading
transform = transforms.Compose([transforms.ToTensor(), transforms.Normalize((0.5,), (0.5,))])
train_loader = torch.utils.data.DataLoader(
    datasets.MNIST('./data', train=True, download=True, transform=transform),
    batch_size=64, shuffle=True)


def plot_results(data, target ):
    pred = [0] * target.shape[0]
    print(pred)
    plt.figure(figsize=(12, 4))
    for i in range(8):
        plt.subplot(1, 8, i+1)
        plt.imshow(data[i].squeeze(), cmap='gray')
        plt.title(f"Pred: {pred[i]}\nActual: {target[i]}")
        plt.axis('off')
    plt.show()
