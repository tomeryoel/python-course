from sklearn.datasets import load_iris
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
import numpy as np


# ==================================================
# 1. Load the Iris dataset
# ==================================================

iris = load_iris()

print("Dataset loaded successfully!")


# ==================================================
# 2. Investigate the dataset
# ==================================================

print("\n--- Dataset Investigation ---")

print("\nFeature names:")
print(iris.feature_names)

print("\nTarget names:")
print(iris.target_names)

print("\nData shape:")
print(iris.data.shape)

print("\nTarget shape:")
print(iris.target.shape)

print("\nFirst 5 rows of the data:")
print(iris.data[:5])

print("\nFirst 5 labels:")
print(iris.target[:5])


# ==================================================
# 3. Select only the required two features
# ==================================================
# The exercise says to use only:
# ['sepal length (cm)', 'petal length (cm)']

feature_names = list(iris.feature_names)

sepal_length_index = feature_names.index("sepal length (cm)")
petal_length_index = feature_names.index("petal length (cm)")

X = iris.data[:, [sepal_length_index, petal_length_index]]

print("\n--- Selected Features ---")
print("We are using only:")
print("1. sepal length (cm)")
print("2. petal length (cm)")

print("\nFirst 5 rows of X:")
print(X[:5])

print("\nFeature ranges:")
print("sepal length min:", X[:, 0].min())
print("sepal length max:", X[:, 0].max())
print("petal length min:", X[:, 1].min())
print("petal length max:", X[:, 1].max())


# ==================================================
# 4. Create and train the K-Means model
# ==================================================
# We know there are 3 flower species,
# so we ask K-Means to create 3 clusters.

kmeans = KMeans(
    n_clusters=3,
    random_state=42,
    n_init=10
)

cluster_numbers = kmeans.fit_predict(X)

print("\n--- K-Means Finished ---")
print("First 20 cluster numbers:")
print(cluster_numbers[:20])


# ==================================================
# 5. Get the centroids
# ==================================================

centroids = kmeans.cluster_centers_

print("\n--- Centroids ---")
print(centroids)


# ==================================================
# 6. Label the clusters by petal length order
# ==================================================
# The exercise says:
# smallest petal length  -> setosa
# middle petal length    -> versicolor
# largest petal length   -> virginica

# centroids[:, 1] means:
# take the second column of the centroids,
# which is petal length.

centroid_order = np.argsort(centroids[:, 1])

cluster_to_species = {
    centroid_order[0]: "setosa",
    centroid_order[1]: "versicolor",
    centroid_order[2]: "virginica"
}

print("\n--- Cluster Mapping ---")

for cluster_id in range(3):
    print(
        "Cluster",
        cluster_id,
        "is labeled as:",
        cluster_to_species[cluster_id],
        "| centroid:",
        centroids[cluster_id]
    )


# ==================================================
# 7. Convert each cluster number to a flower name
# ==================================================

predicted_species = np.array([
    cluster_to_species[cluster_id]
    for cluster_id in cluster_numbers
])

print("\nFirst 20 predicted species:")
print(predicted_species[:20])


# ==================================================
# 8. Count how many flowers are in each predicted group
# ==================================================

print("\n--- Predicted Group Counts ---")

for species_name in ["setosa", "versicolor", "virginica"]:
    count = np.sum(predicted_species == species_name)
    print(species_name, ":", count)


# ==================================================
# 9. Draw the K-Means clustering graph
# ==================================================

plt.figure(figsize=(9, 6))

for cluster_id in range(3):
    cluster_points = X[cluster_numbers == cluster_id]

    plt.scatter(
        cluster_points[:, 0],
        cluster_points[:, 1],
        label=cluster_to_species[cluster_id]
    )

plt.scatter(
    centroids[:, 0],
    centroids[:, 1],
    marker="X",
    s=250,
    color="black",
    label="Centroids"
)

for cluster_id in range(3):
    centroid_x = centroids[cluster_id, 0]
    centroid_y = centroids[cluster_id, 1]
    species_name = cluster_to_species[cluster_id]

    plt.text(
        centroid_x + 0.05,
        centroid_y + 0.05,
        species_name,
        fontsize=10
    )

plt.xlabel("sepal length (cm)")
plt.ylabel("petal length (cm)")
plt.title("K-Means Clustering on Iris Dataset")
plt.legend()
plt.grid(True)
plt.show()