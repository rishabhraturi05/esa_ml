import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, GridSearchCV, StratifiedKFold
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.pipeline import Pipeline
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score, precision_recall_fscore_support

df_raw = pd.read_csv('fault_dataset.csv')
feature_cols = [c for c in df_raw.columns if c not in ['fault', 'line', 'position']]
LABEL = 'fault'

df_clean = df_raw.dropna(subset=feature_cols + [LABEL]).drop_duplicates().copy()
X = df_clean[feature_cols]
y = df_clean[LABEL]

le = LabelEncoder()
y_enc = le.fit_transform(y)

# 70/15/15 Stratified Split
X_train, X_temp, y_train, y_temp = train_test_split(X, y_enc, test_size=0.30, stratify=y_enc, random_state=42)
X_val, X_test, y_val, y_test = train_test_split(X_temp, y_temp, test_size=0.50, stratify=y_temp, random_state=42)

print(f"Train size: {len(X_train)}, Val size: {len(X_val)}, Test size: {len(X_test)}")

# 1. SVM Grid Search on Training Set
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
grid_search.fit(X_train, y_train)

best_svm = grid_search.best_estimator_

# 2. Validation Phase Evaluation
val_pred = best_svm.predict(X_val)
val_acc = accuracy_score(y_val, val_pred)
val_prec, val_rec, val_f1, _ = precision_recall_fscore_support(y_val, val_pred, average='macro')
val_cm = confusion_matrix(y_val, val_pred)

print(f"\n--- VALIDATION PHASE (N={len(X_val)}) ---")
print(f"Validation Accuracy: {val_acc*100:.2f}%")
print(f"Validation Macro F1: {val_f1:.4f}")
print("Validation Confusion Matrix:\n", val_cm)
print("Validation Report:\n", classification_report(y_val, val_pred, target_names=le.classes_, digits=4))

# 3. Final Testing Phase Evaluation
test_pred = best_svm.predict(X_test)
test_acc = accuracy_score(y_test, test_pred)
test_prec, test_rec, test_f1, _ = precision_recall_fscore_support(y_test, test_pred, average='macro')
test_cm = confusion_matrix(y_test, test_pred)

print(f"\n--- TESTING PHASE (N={len(X_test)}) ---")
print(f"Test Accuracy: {test_acc*100:.2f}%")
print(f"Test Macro F1: {test_f1:.4f}")
print("Test Confusion Matrix:\n", test_cm)
print("Test Report:\n", classification_report(y_test, test_pred, target_names=le.classes_, digits=4))

# 4. Baselines on Val and Test
rf = Pipeline([('scaler', StandardScaler()), ('rf', RandomForestClassifier(n_estimators=100, random_state=42))])
rf.fit(X_train, y_train)
rf_val_acc = accuracy_score(y_val, rf.predict(X_val))
rf_test_acc = accuracy_score(y_test, rf.predict(X_test))

knn = Pipeline([('scaler', StandardScaler()), ('knn', KNeighborsClassifier(n_neighbors=5))])
knn.fit(X_train, y_train)
knn_val_acc = accuracy_score(y_val, knn.predict(X_val))
knn_test_acc = accuracy_score(y_test, knn.predict(X_test))

print(f"\n--- BASELINE COMPARISON ---")
print(f"Model          | Validation Acc | Test Acc")
print(f"SVM (Proposed) | {val_acc*100:14.2f}% | {test_acc*100:8.2f}%")
print(f"Random Forest  | {rf_val_acc*100:14.2f}% | {rf_test_acc*100:8.2f}%")
print(f"KNN (K=5)      | {knn_val_acc*100:14.2f}% | {knn_test_acc*100:8.2f}%")
