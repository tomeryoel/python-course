from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import numpy as np


# --------------------------------------------------
# 1. Load the dataset
# --------------------------------------------------

data = load_breast_cancer()

print("Dataset loaded successfully!")
print("All feature names:")
print(data.feature_names)

print("\nTarget names:")
print(data.target_names)
print("0 =", data.target_names[0])
print("1 =", data.target_names[1])


# --------------------------------------------------
# 2. Investigate the dataset
# --------------------------------------------------

print("\nDataset shape:")
print(data.data.shape)

print("\nTarget shape:")
print(data.target.shape)

print("\nFirst 5 rows of the full dataset:")
print(data.data[:5])

print("\nFirst 5 labels:")
print(data.target[:5])


# --------------------------------------------------
# 3. Select only two features:
#    mean radius and mean texture
# --------------------------------------------------

feature_names = list(data.feature_names)

mean_radius_index = feature_names.index("mean radius")
mean_texture_index = feature_names.index("mean texture")

X = data.data[:, [mean_radius_index, mean_texture_index]]
y = data.target

print("\nSelected features:")
print("mean radius index:", mean_radius_index)
print("mean texture index:", mean_texture_index)

print("\nFirst 5 rows with only mean radius and mean texture:")
print(X[:5])

print("\nFeature ranges:")
print("mean radius min:", X[:, 0].min())
print("mean radius max:", X[:, 0].max())
print("mean texture min:", X[:, 1].min())
print("mean texture max:", X[:, 1].max())

print("\nLabels count:")
print("malignant / cancerous:", np.sum(y == 0))
print("benign / not cancerous:", np.sum(y == 1))


# --------------------------------------------------
# 4. Split the data into train and test
# --------------------------------------------------

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)


# --------------------------------------------------
# 5. Build a supervised classification model
# --------------------------------------------------
# We use Pipeline:
# First: StandardScaler - normalizes the numbers
# Second: LogisticRegression - supervised classification model

model = Pipeline([
    ("scaler", StandardScaler()),
    ("classifier", LogisticRegression())
])


# --------------------------------------------------
# 6. Train the model
# --------------------------------------------------

model.fit(X_train, y_train)

print("\nModel trained successfully!")


# --------------------------------------------------
# 7. Evaluate the model
# --------------------------------------------------

y_pred = model.predict(X_test)

accuracy = accuracy_score(y_test, y_pred)

print("\nModel accuracy:")
print(accuracy)

print("\nConfusion matrix:")
print(confusion_matrix(y_test, y_pred))

print("\nClassification report:")
print(classification_report(y_test, y_pred, target_names=data.target_names))


# --------------------------------------------------
# 8. Receive input from the user
# --------------------------------------------------

def get_float_from_user(message, min_value, max_value):
    while True:
        try:
            value = float(input(message))

            if value < min_value or value > max_value:
                print(f"Please enter a value between {min_value} and {max_value}.")
            else:
                return value

        except ValueError:
            print("Invalid input. Please enter a number.")


print("\nNow enter new cell values:")

user_mean_radius = get_float_from_user(
    "Enter mean radius, approximately 6 to 29: ",
    6,
    29
)

user_mean_texture = get_float_from_user(
    "Enter mean texture, approximately 9 to 40: ",
    9,
    40
)


# --------------------------------------------------
# 9. Predict the result
# --------------------------------------------------

new_sample = np.array([[user_mean_radius, user_mean_texture]])

prediction = model.predict(new_sample)[0]
prediction_probabilities = model.predict_proba(new_sample)[0]

print("\nPrediction result:")

if prediction == 0:
    print("The model predicts: cancerous / malignant")
else:
    print("The model predicts: not cancerous / benign")

print("\nPrediction probabilities:")
print("Cancerous / malignant probability:", prediction_probabilities[0])
print("Not cancerous / benign probability:", prediction_probabilities[1])


# --------------------------------------------------
# 10. Disclaimer
# --------------------------------------------------

print("\nImportant note:")
print("This is only a machine learning exercise and not a real medical diagnosis.")