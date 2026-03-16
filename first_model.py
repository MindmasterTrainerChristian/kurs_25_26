import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Professional ML Libraries
from sklearn.datasets import load_iris


from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from sklearn.pipeline import Pipeline


iris = load_iris()

type(iris)

data = iris["data"]
target = iris["target"]


# Split: 80% for training, 20% for testing
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

print(f'Training samples: {len(X_train)}')
print(f'Testing samples: {len(X_test)}')


# 1. Initialize the model
model = KNeighborsClassifier(n_neighbors=5)

# 2. Train the model (fitting the data)
model.fit(X_train, y_train)

print('Model training complete!')

# Make predictions
predictions = model.predict(X_test)

# Calculate accuracy
accuracy = accuracy_score(y_test, predictions)

print(f'Model Accuracy: {accuracy * 100:.2f}%')






