import pandas as pd
from sklearn.datasets import load_iris
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
import matplotlib.pyplot as plt

data = load_iris()
X = data.data[:, [0, 2]]
feature_names = [data.feature_names[0], data.feature_names[2]]

kmeans = KMeans(n_clusters=3, random_state=42, n_init="auto")
labels = kmeans.fit_predict(X)

centers = kmeans.cluster_centers_
print("Centers:", centers)
print("Silhouette Score:", silhouette_score(X, labels))
df = pd.DataFrame({
    "cluster": labels,
    "true_species": [data.target_names[i] for i in data.target]
})

plt.figure(figsize=(6,5))
plt.scatter(X[:, 0], X[:, 1], c=labels, s=30)
plt.scatter(centers[:, 0], centers[:, 1], s=200, marker="x", edgecolors="k")
for cid, (sx, px) in enumerate(centers):
    plt.text(sx, px, cid, ha="center", va="center")

plt.xlabel("Sepal Length")
plt.ylabel("Petal Length")
plt.show()