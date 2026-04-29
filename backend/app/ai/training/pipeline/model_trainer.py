from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import joblib
import os

def train_model(X, y, model_name='rf_model', save_path='../processed'):
    """
    Train a Random Forest model on X, y and save it
    """
    print("Splitting dataset into train/test sets...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    print("Training Random Forest Classifier...")
    model = RandomForestClassifier(
    n_estimators=20,
    max_depth=10,
    n_jobs=-1,
    random_state=42 
    )
    model.fit(X_train, y_train)

    print("Training complete. Evaluating model...")
    y_pred = model.predict(X_test)

    print("Accuracy:", accuracy_score(y_test, y_pred))
    print("Classification Report:")
    print(classification_report(y_test, y_pred))
    print("Confusion Matrix:")
    print(confusion_matrix(y_test, y_pred))

    # Save model
    os.makedirs(save_path, exist_ok=True)
    model_file = os.path.join(save_path, f"{model_name}.joblib")
    joblib.dump(model, model_file)

    print(f"Model saved to {model_file}")
    return model
