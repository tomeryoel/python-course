import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

# Fake data: two loose groups of points
rng = np.random.default_rng(42)
A = rng.normal(loc=[2, 2], scale=0.6, size=(40, 2))
B = rng.normal(loc=[6, 5], scale=0.6, size=(40, 2))
X = np.vstack([A, B])

# 1) Choose number of clusters k
kmeans = KMeans(n_clusters=2, n_init="auto", random_state=42)

# 2) Fit and get cluster labels
labels = kmeans.fit_predict(X)

# 3) Inspect results
centers = kmeans.cluster_centers_

print("Cluster centers:\n", centers)
print("First 10 labels:", labels[:10])
print("Silhouette score:", silhouette_score(X, labels))

# 4) Draw the results
plt.figure(figsize=(8, 6))

# Points colored by cluster
plt.scatter(X[:, 0], X[:, 1], c=labels, s=60, label="Data Points")

# Cluster centers
plt.scatter(
    centers[:, 0],
    centers[:, 1],
    marker="X",
    s=250,
    label="Cluster Centers"
)

plt.title("KMeans Clustering Result")
plt.xlabel("Feature 1")
plt.ylabel("Feature 2")
plt.legend()
plt.grid(True)
plt.show()