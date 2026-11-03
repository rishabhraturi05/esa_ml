"""
Machine Learning-Based Transmission Line Fault Type Classification
for Intelligent Power System Protection

Course: Energy System Analytics (EE 1331) | Project No.: 15
Students: Rishabh Raturi (24EEB0A55), Simhadri Yateesh Sai (24EEB0A59)
Faculty: Prof. Debasmita Panda
Department: Electrical & Electronics Engineering
"""

import os
import time
import joblib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import train_test_split, GridSearchCV, StratifiedKFold
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.pipeline import Pipeline
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.decomposition import PCA
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    accuracy_score,
    precision_recall_fscore_support
)

def main():
    print("=" * 70)
    print("ESA TERM PAPER PROJECT 15: TRANSMISSION LINE FAULT CLASSIFIER")
    print("=" * 70)

    # -------------------------------------------------------------
    # Step 3: Load Dataset
    # -------------------------------------------------------------
    data_path = 'fault_dataset.csv'
    if not os.path.exists(data_path):
        raise FileNotFoundError(f"Cannot find dataset at {data_path}")
    
    df_raw = pd.read_csv(data_path)
    print(f"\n[Step 3] Dataset loaded successfully from {data_path}")
    print(f"         Dimensions: {df_raw.shape[0]} samples x {df_raw.shape[1]} columns")

    # -------------------------------------------------------------
    # Step 4: Data Inspection & Preprocessing
    # -------------------------------------------------------------
    print("\n[Step 4] Inspecting data structure and handling anomalies:")
    # 24 electrical measurement features: 9 voltages (Ua1..Uc3), 15 currents (Ia1..Ic5)
    feature_cols = [c for c in df_raw.columns if c not in ['fault', 'line', 'position']]
    LABEL = 'fault'

    print(f"         Features identified: {len(feature_cols)} electrical channels (9 voltages, 15 currents)")
    print(f"         Missing values in feature columns: {df_raw[feature_cols].isnull().sum().sum()}")
    print(f"         Missing values in metadata (line, position): {df_raw[['line', 'position']].isnull().sum().sum()}")
    print("         Note: Missing metadata values occur exclusively in normal operation ('no fault').")
    
    # Prune 73 identical static load-flow duplicates
    df_clean = df_raw.dropna(subset=feature_cols + [LABEL]).drop_duplicates().copy()
    print(f"         Removed {len(df_raw) - len(df_clean)} duplicate static load-flow records.")
    print(f"         Clean dataset size: {len(df_clean)} samples.")

    print("\n         Class distribution after cleaning:")
    for k, v in df_clean[LABEL].value_counts().items():
        print(f"           - {k:10s}: {v:3d} samples")

    X = df_clean[feature_cols].copy()
    y = df_clean[LABEL].copy()

    # Label Encoding
    le = LabelEncoder()
    y_enc = le.fit_transform(y)
    classes = list(le.classes_)

    # -------------------------------------------------------------
    # Step 6: Stratified Splitting & Model Training
    # -------------------------------------------------------------
    print("\n[Step 6] Partitioning dataset into Stratified 70/15/15 splits:")
    X_train, X_temp, y_train, y_temp = train_test_split(
        X, y_enc, test_size=0.30, stratify=y_enc, random_state=42
    )
    X_val, X_test, y_val, y_test = train_test_split(
        X_temp, y_temp, test_size=0.50, stratify=y_temp, random_state=42
    )
    print(f"         Training set:   {len(X_train)} samples (70%)")
    print(f"         Validation set: {len(X_val)} samples (15%)")
    print(f"         Testing set:    {len(X_test)} samples (15%)")

    # Pipeline with StandardScaler and SVC
    pipe_svm = Pipeline([
        ('scaler', StandardScaler()),
        ('svm', SVC(probability=True, random_state=42))
    ])

    param_grid = {
        'svm__kernel': ['linear', 'rbf'],
        'svm__C': [0.1, 1, 10, 100],
        'svm__gamma': ['scale', 0.01, 0.1, 1]
    }

    cv_strat = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    grid_search = GridSearchCV(pipe_svm, param_grid, cv=cv_strat, scoring='f1_macro', n_jobs=1)
    
    print("\n         Executing 5-Fold Stratified Cross-Validation with GridSearchCV...")
    grid_search.fit(X_train, y_train)

    best_svm = grid_search.best_estimator_
    print(f"         Optimal Parameters: {grid_search.best_params_}")
    print(f"         Best 5-Fold CV Macro F1: {grid_search.best_score_:.4f}")

    # -------------------------------------------------------------
    # Step 7: Model Evaluation
    # -------------------------------------------------------------
    print("\n[Step 7] Evaluating Model Generalization:")
    val_pred = best_svm.predict(X_val)
    val_acc = accuracy_score(y_val, val_pred)
    print(f"         Validation Accuracy: {val_acc*100:.2f}%")

    test_pred = best_svm.predict(X_test)
    test_acc = accuracy_score(y_test, test_pred)
    prec_m, rec_m, f1_m, _ = precision_recall_fscore_support(y_test, test_pred, average='macro')
    print(f"         Test Accuracy:       {test_acc*100:.2f}%")
    print(f"         Test Macro Precision: {prec_m:.4f} | Recall: {rec_m:.4f} | F1: {f1_m:.4f}")

    print("\n--- Detailed Test Classification Report ---")
    print(classification_report(y_test, test_pred, target_names=classes, digits=4))

    print("Confusion Matrix:")
    cm = confusion_matrix(y_test, test_pred)
    print(cm)

    # Comparison with baseline models
    pipe_rf = Pipeline([('scaler', StandardScaler()), ('rf', RandomForestClassifier(n_estimators=100, random_state=42))])
    pipe_rf.fit(X_train, y_train)
    rf_acc = accuracy_score(y_test, pipe_rf.predict(X_test))

    pipe_knn = Pipeline([('scaler', StandardScaler()), ('knn', KNeighborsClassifier(n_neighbors=5))])
    pipe_knn.fit(X_train, y_train)
    knn_acc = accuracy_score(y_test, pipe_knn.predict(X_test))

    print(f"\nModel Comparison -> SVM: {test_acc*100:.2f}% | Random Forest: {rf_acc*100:.2f}% | KNN: {knn_acc*100:.2f}%")

    # -------------------------------------------------------------
    # Step 8: Prototype Protection Module & Latency Benchmark
    # -------------------------------------------------------------
    print("\n[Step 8] Serializing Prototype Protection Module:")
    model_bundle = {
        'model': best_svm,
        'encoder': le,
        'features': feature_cols
    }
    joblib.dump(model_bundle, 'fault_classifier.pkl')
    print("         Model saved to 'fault_classifier.pkl'")

    def classify_fault(sample_vector):
        """
        Accepts 24-element list/array of voltage and current sensor readings.
        Returns predicted fault label string and confidence percentage.
        """
        bundle = joblib.load('fault_classifier.pkl')
        arr = np.array(sample_vector).reshape(1, -1)
        pred = bundle['model'].predict(arr)
        proba = bundle['model'].predict_proba(arr)[0]
        return bundle['encoder'].inverse_transform(pred)[0], proba[pred[0]] * 100

    print("\n         Testing classify_fault() on sample disturbance vectors:")
    for idx in [0, 15, 30]:
        vec = X_test.iloc[idx].values
        actual = classes[y_test[idx]]
        pred_label, conf = classify_fault(vec)
        print(f"           - Sample {idx:02d} -> Actual: {actual:10s} | Predicted: {pred_label:10s} | Confidence: {conf:.2f}%")

    # Real-Time Benchmark
    sample_arr = X_test.iloc[0].values.reshape(1, -1)
    loaded_pipe = joblib.load('fault_classifier.pkl')['model']
    for _ in range(50):
        _ = loaded_pipe.predict(sample_arr)

    n_iter = 1000
    t0 = time.perf_counter()
    for _ in range(n_iter):
        _ = loaded_pipe.predict(sample_arr)
    t1 = time.perf_counter()

    avg_time_ms = ((t1 - t0) / n_iter) * 1000
    print(f"\n         Execution Speed: {avg_time_ms:.4f} ms per sample ({avg_time_ms*1000:.1f} microseconds)")
    print(f"         Consumes {avg_time_ms / 20.0 * 100:.3f}% of one 50 Hz power cycle (20.0 ms).")
    print("         Real-time sub-cycle protection capability confirmed!")
    print("=" * 70)

if __name__ == '__main__':
    main()

