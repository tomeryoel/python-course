from sklearn.datasets import load_breast_cancer

data = load_breast_cancer()
X = data.data[:, :2]
y = data.target
feature_names = data.feature_names[:2]
print(feature_names)