import os
import numpy as np
import joblib
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score, confusion_matrix
import matplotlib.pyplot as plt
from collections import deque

# Path to save trained model
MODEL_PATH = "knn_model.pkl"

# Folder containing recorded sensor data
RECORDS_FOLDER = "records"

# Number of previous samples to use (history window)
N_PREVIOUS_POINTS = 5  

# Drum classes (mapped from filenames)
DRUM_CLASSES = {1: "kick", 2: "snare", 3: "hihat", 4: "tom", 5: "ride"}

def load_data():
    """Loads training data from all recorded files (left & right sticks combined)."""
    all_data = []
    all_labels = []

    for filename in os.listdir(RECORDS_FOLDER):
        if filename.endswith(".txt"):
            label = get_label_from_filename(filename)
            if label is None:
                continue  # Ignore non-drum files

            filepath = os.path.join(RECORDS_FOLDER, filename)
            with open(filepath, "r") as file:
                lines = file.readlines()

            # Extract numeric values (ignoring headers)
            sensor_data = [list(map(float, line.strip().split(","))) for line in lines if line.strip()]
            
            # Use only yaw (heading) & pitch
            sensor_data = [[entry[6], entry[7]] for entry in sensor_data]  # heading = [6], pitch = [7]

            # Apply sliding window
            feature_vectors = create_sliding_window(sensor_data, N_PREVIOUS_POINTS)

            all_data.extend(feature_vectors)
            all_labels.extend([label] * len(feature_vectors))

    return np.array(all_data), np.array(all_labels)

def get_label_from_filename(filename):
    """Extracts class label from filename (first number)."""
    try:
        class_number = int(filename.split("_")[0])  # Get first number
        return DRUM_CLASSES.get(class_number, None)  # Map number to drum type
    except ValueError:
        return None  # Ignore if the filename is incorrectly formatted

def create_sliding_window(data, window_size):
    """Transforms raw sensor data into a time-series feature vector."""
    queue = deque(maxlen=window_size)
    feature_vectors = []
    
    for point in data:
        queue.append(point)
        if len(queue) == window_size:
            feature_vectors.append(np.array(queue).flatten())
    
    return feature_vectors

def train_and_evaluate_knn(X, y, model_path, test_size=0.2):
    """Trains and evaluates a KNN model."""
    if len(X) == 0:
        print(f"⚠️ No valid data found.")
        return None

    # Split data (80% train, 20% test)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, stratify=y, random_state=42)

    # Train KNN classifier
    knn = KNeighborsClassifier(n_neighbors=5)
    knn.fit(X_train, y_train)

    # Evaluate on test data
    y_pred = knn.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)

    print(f"\n🔍 KNN Model Evaluation")
    print(f"✅ Accuracy: {accuracy:.2%}")

    # Save model
    joblib.dump(knn, model_path)
    print(f"✅ Model saved: {model_path}")

def main():
    """Train and evaluate the KNN model."""
    X, y = load_data()
    train_and_evaluate_knn(X, y, MODEL_PATH)

if __name__ == "__main__":
    main()
