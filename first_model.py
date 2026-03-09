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






