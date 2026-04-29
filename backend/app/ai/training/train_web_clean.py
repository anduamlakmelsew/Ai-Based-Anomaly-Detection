import pandas as pd
import os
import pickle

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report

BASE_PATH = "datasets"

# =========================
# LOAD CSIC DATASET
# =========================
csic_path = os.path.join(BASE_PATH, "owasp_secdata/csic_database.csv")
csic = pd.read_csv(csic_path, low_memory=False)

# Fill missing values
csic = csic.fillna("")

# Build text input
csic["text_input"] = (
    csic["Method"] + " " +
    csic["URL"] + " " +
    csic["User-Agent"] + " " +
    csic["content"]
)

csic["label"] = csic["classification"]

csic = csic[["text_input", "label"]]

# =========================
# LOAD XSS DATASET
# =========================
xss_path = os.path.join(BASE_PATH, "owasp_secdata/XSS_dataset.csv")
xss = pd.read_csv(xss_path)

xss = xss.rename(columns={
    "Sentence": "text_input",
    "Label": "label"
})

xss = xss[["text_input", "label"]]

# =========================
# MERGE DATASETS
# =========================
df = pd.concat([csic, xss], ignore_index=True)

print("Final dataset shape:", df.shape)

# =========================
# TRAIN TEST SPLIT
# =========================
X_train, X_test, y_train, y_test = train_test_split(
    df["text_input"],
    df["label"],
    test_size=0.2,
    random_state=42
)

# =========================
# TF-IDF VECTORIZER
# =========================
vectorizer = TfidfVectorizer(
    max_features=5000,
    ngram_range=(1,2)
)

X_train_vec = vectorizer.fit_transform(X_train)
X_test_vec = vectorizer.transform(X_test)

# =========================
# MODEL
# =========================
model = RandomForestClassifier(n_estimators=100)

print("Training model...")
model.fit(X_train_vec, y_train)

# =========================
# EVALUATION
# =========================
y_pred = model.predict(X_test_vec)

print("\n📊 Classification Report:\n")
print(classification_report(y_test, y_pred))

# =========================
# SAVE FILES (IMPORTANT)
# =========================
os.makedirs("../models", exist_ok=True)

with open("../models/web_model.pkl", "wb") as f:
    pickle.dump(model, f)

with open("../models/web_vectorizer.pkl", "wb") as f:
    pickle.dump(vectorizer, f)

print("\n✅ Web model saved successfully!")
