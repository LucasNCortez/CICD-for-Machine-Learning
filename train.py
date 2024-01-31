import pandas as pd
import skops.io as sio
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import accuracy_score, f1_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OrdinalEncoder, StandardScaler

## Loading the Data
drug_df = pd.read_csv("Data/drug200.csv")
drug_df = drug_df.sample(frac=1)

## Train Test Split
from sklearn.model_selection import train_test_split

X = drug_df.drop("Drug", axis=1)
y = drug_df.Drug

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, random_state=125
)


## Pipeline
cat_col = X.select_dtypes(include=["object", "bool"]).columns.tolist()
num_col = X.select_dtypes(include=["int64", "float64"]).columns.tolist()

transform = ColumnTransformer(
    [
        ("encoder", OrdinalEncoder(), cat_col),
        ("num_imputer", SimpleImputer(strategy="median"), num_col),
        ("num_scaler", StandardScaler(), num_col),
    ]
)
pipe = Pipeline(
    steps=[
        ("preprocessing", transform),
        ("model", RandomForestClassifier(n_estimators=100, random_state=125)),
    ]
)

## Training
pipe.fit(X_train, y_train)


## Model Evaluation
predictions = pipe.predict(X_test)
accuracy = accuracy_score(y_test, predictions)
f1 = f1_score(y_test, predictions, average="macro")

print("Accuracy: ", str(accuracy.round(2) * 100) + "%", "F1: ", f1.round(2))

## Write metrics to file
with open("Results/metrics.txt", "w") as outfile:
    outfile.write(f"\nAccuracy = {accuracy.round(2)}, F1 Score = {f1.round(2)}.")


## Confusion Matrix Plot
import matplotlib.pyplot as plt
from sklearn.metrics import ConfusionMatrixDisplay, confusion_matrix

predictions = pipe.predict(X_test)
cm = confusion_matrix(y_test, predictions, labels=pipe.classes_)
disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=pipe.classes_)
disp.plot()
plt.savefig("Results/model_results.png", dpi=120)


## Saving the model
sio.dump(pipe, "Model/drug_pipeline.skops")