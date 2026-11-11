import os
import json
import time
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import joblib

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

# Set clean academic publication style for matplotlib
plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.serif'] = ['Times New Roman', 'DejaVu Serif', 'Georgia']
plt.rcParams['font.size'] = 10
plt.rcParams['axes.titlesize'] = 11
plt.rcParams['axes.labelsize'] = 10
plt.rcParams['xtick.labelsize'] = 9
plt.rcParams['ytick.labelsize'] = 9
plt.rcParams['legend.fontsize'] = 9
plt.rcParams['figure.titlesize'] = 12

def run_academic_pipeline():
    print("=" * 70)
    print("RUNNING ACADEMIC ML PIPELINE & GENERATING PUBLICATION ARTIFACTS")
    print("=" * 70)

    # 1. Ingest Data
    data_path = 'fault_dataset.csv'
    df_raw = pd.read_csv(data_path)
    feature_cols = [c for c in df_raw.columns if c not in ['fault', 'line', 'position']]
    LABEL = 'fault'

    # Clean duplicates and incomplete rows
    df_clean = df_raw.dropna(subset=feature_cols + [LABEL]).drop_duplicates().copy()
    X = df_clean[feature_cols].copy()
    y = df_clean[LABEL].copy()

    le = LabelEncoder()
    y_enc = le.fit_transform(y)
    classes = list(le.classes_)

    plot_dir = 'plots'
    os.makedirs(plot_dir, exist_ok=True)

    # 2. Academic Color Palette (Minimalist, scholarly grey/slate/muted tones)
    # 2psc: slate blue, 3psc: dark crimson/maroon, no fault: charcoal/navy, spgf: forest green
    acad_colors = ['#4A6572', '#B71C1C', '#263238', '#2E7D32']
    palette = dict(zip(classes, acad_colors))

    # --- Plot 1: Class Distribution ---
    fig, ax = plt.subplots(figsize=(6.5, 3.8), dpi=300)
    counts = df_clean[LABEL].value_counts()
    bars = ax.bar(counts.index, counts.values, color=['#37474F', '#455A64', '#546E7A', '#607D8B'],
                  edgecolor='black', linewidth=1.0, width=0.5)
    for bar in bars:
        h = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., h + 3, f"{int(h)}",
                ha='center', va='bottom', fontsize=9.5, fontweight='bold')
    ax.set_title('Class Distribution across Operating and Fault Regimes', pad=10, fontweight='bold')
    ax.set_xlabel('Condition Category', labelpad=6)
    ax.set_ylabel('Sample Frequency', labelpad=6)
    ax.set_ylim(0, max(counts.values) * 1.15)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    plt.tight_layout()
    fig.savefig(os.path.join(plot_dir, 'fig1_class_distribution.png'))
    plt.close()

    # --- Plot 2: Histograms & Density Curves ---
    fig, axes = plt.subplots(1, 2, figsize=(9.5, 3.8), dpi=300)
    sns.histplot(data=df_clean, x='Ia1', hue=LABEL, kde=True, ax=axes[0], palette=palette, bins=25, alpha=0.35, edgecolor='black', linewidth=0.5)
    axes[0].set_title('(a) Phase A Current at Bus 1 ($I_{a1}$)', fontweight='bold')
    axes[0].set_xlabel('Current $I_{a1}$ (kA)')
    axes[0].set_ylabel('Density / Frequency')
    axes[0].spines['top'].set_visible(False)
    axes[0].spines['right'].set_visible(False)

    sns.histplot(data=df_clean, x='Ua1', hue=LABEL, kde=True, ax=axes[1], palette=palette, bins=25, alpha=0.35, edgecolor='black', linewidth=0.5)
    axes[1].set_title('(b) Phase A Voltage at Bus 1 ($U_{a1}$)', fontweight='bold')
    axes[1].set_xlabel('Voltage $U_{a1}$ (kV)')
    axes[1].set_ylabel('Density / Frequency')
    axes[1].spines['top'].set_visible(False)
    axes[1].spines['right'].set_visible(False)

    plt.tight_layout()
    fig.savefig(os.path.join(plot_dir, 'fig2_feature_distributions.png'))
    plt.close()

    # --- Plot 3: Correlation Matrix ---
    fig, ax = plt.subplots(figsize=(8.5, 7.0), dpi=300)
    corr = X.corr()
    mask = np.triu(np.ones_like(corr, dtype=bool))
    sns.heatmap(corr, mask=mask, cmap='Greys', vmin=-1, vmax=1, annot=False,
                linewidths=0.3, linecolor='#BDBDBD', cbar_kws={'label': 'Pearson Correlation Coefficient $r$'}, ax=ax)
    ax.set_title('Cross-Correlation Matrix of 24 Sensor Measurement Features', pad=10, fontweight='bold')
    plt.tight_layout()
    fig.savefig(os.path.join(plot_dir, 'fig3_correlation_heatmap.png'))
    plt.close()

    # --- Plot 4: Box Plots ---
    df_clean['U_mean'] = df_clean[['Ua1', 'Ub1', 'Uc1']].mean(axis=1)
    df_clean['I_max'] = df_clean[['Ia1', 'Ib1', 'Ic1']].max(axis=1)

    fig, axes = plt.subplots(1, 2, figsize=(9.5, 3.8), dpi=300)
    sns.boxplot(data=df_clean, x=LABEL, y='U_mean', ax=axes[0], hue=LABEL, palette=['#ECEFF1', '#CFD8DC', '#B0BEC5', '#90A4AE'], legend=False, width=0.5, boxprops=dict(edgecolor='black'), medianprops=dict(color='black', linewidth=1.5), whiskerprops=dict(color='black'), capprops=dict(color='black'))
    axes[0].set_title('(a) Bus 1 Mean Phase Voltage (kV)', fontweight='bold')
    axes[0].set_xlabel('Operating / Fault Condition')
    axes[0].set_ylabel('Voltage $U_{mean}$ (kV)')
    axes[0].spines['top'].set_visible(False)
    axes[0].spines['right'].set_visible(False)

    sns.boxplot(data=df_clean, x=LABEL, y='I_max', ax=axes[1], hue=LABEL, palette=['#ECEFF1', '#CFD8DC', '#B0BEC5', '#90A4AE'], legend=False, width=0.5, boxprops=dict(edgecolor='black'), medianprops=dict(color='black', linewidth=1.5), whiskerprops=dict(color='black'), capprops=dict(color='black'))
    axes[1].set_title('(b) Line 1 Maximum Phase Current (kA)', fontweight='bold')
    axes[1].set_xlabel('Operating / Fault Condition')
    axes[1].set_ylabel('Current $I_{max}$ (kA)')
    axes[1].spines['top'].set_visible(False)
    axes[1].spines['right'].set_visible(False)

    plt.tight_layout()
    fig.savefig(os.path.join(plot_dir, 'fig4_boxplots_voltages_currents.png'))
    plt.close()

    # --- Plot 5: 2D PCA Scatter ---
    scaler_pca = StandardScaler()
    X_scaled = scaler_pca.fit_transform(X)
    pca = PCA(n_components=2, random_state=42)
    X_pca = pca.fit_transform(X_scaled)
    var_exp = pca.explained_variance_ratio_

    fig, ax = plt.subplots(figsize=(7.0, 4.8), dpi=300)
    markers = ['o', 's', '^', 'D']
    for c_idx, c_name in enumerate(classes):
        mask_c = (y_enc == c_idx)
        ax.scatter(X_pca[mask_c, 0], X_pca[mask_c, 1],
                   label=c_name, color=palette[c_name],
                   marker=markers[c_idx], alpha=0.75, edgecolors='black', s=45)
    ax.set_title(f'Two-Dimensional PCA Projection (Variance Captured: {var_exp.sum()*100:.1f}%)', pad=10, fontweight='bold')
    ax.set_xlabel(f'Principal Component 1 ({var_exp[0]*100:.1f}% Variance)')
    ax.set_ylabel(f'Principal Component 2 ({var_exp[1]*100:.1f}% Variance)')
    ax.legend(title='Condition Class', frameon=True, edgecolor='black')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    plt.tight_layout()
    fig.savefig(os.path.join(plot_dir, 'fig5_pca_scatter.png'))
    plt.close()

    # 3. Stratified Data Split (70/15/15)
    X_train, X_temp, y_train, y_temp = train_test_split(
        X, y_enc, test_size=0.30, stratify=y_enc, random_state=42
    )
    X_val, X_test, y_val, y_test = train_test_split(
        X_temp, y_temp, test_size=0.50, stratify=y_temp, random_state=42
    )
    print(f"Dataset Partitions: Train={len(X_train)} (70%), Val={len(X_val)} (15%), Test={len(X_test)} (15%)")

    # 4. Model Training & 5-Fold Stratified Cross-Validation
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
    grid_search = GridSearchCV(pipe_svm, param_grid, cv=cv_strat, scoring='f1_macro', n_jobs=1, return_train_score=True)
    grid_search.fit(X_train, y_train)

    best_svm = grid_search.best_estimator_
    best_params = grid_search.best_params_
    best_cv_f1 = grid_search.best_score_
    print(f"Optimal Hyperparameters: {best_params} | 5-Fold CV Macro F1: {best_cv_f1:.4f}")

    # --- Plot: Hyperparameter Sensitivity Curve ---
    res_df = pd.DataFrame(grid_search.cv_results_)
    fig, ax = plt.subplots(figsize=(6.5, 3.8), dpi=300)
    rbf_scale = res_df[(res_df['param_svm__kernel'] == 'rbf') & (res_df['param_svm__gamma'] == 'scale')]
    linear_res = res_df[(res_df['param_svm__kernel'] == 'linear') & (res_df['param_svm__gamma'] == 'scale')]
    
    ax.plot(rbf_scale['param_svm__C'].astype(float), rbf_scale['mean_test_score'],
            marker='s', lw=1.5, color='#263238', label=r'RBF Kernel ($\gamma$=scale)')
    ax.plot(linear_res['param_svm__C'].astype(float), linear_res['mean_test_score'],
            marker='o', lw=1.5, color='#B71C1C', linestyle='--', label='Linear Kernel')
    ax.set_xscale('log')
    ax.set_title('Cross-Validation Macro F1-Score versus Regularization Parameter $C$', pad=10, fontweight='bold')
    ax.set_xlabel('Penalty Parameter $C$ (Log Scale)')
    ax.set_ylabel('Mean 5-Fold CV Macro F1')
    ax.grid(True, linestyle=':', alpha=0.6)
    ax.legend(frameon=True, edgecolor='black')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    plt.tight_layout()
    fig.savefig(os.path.join(plot_dir, 'fig7_hyperparameter_tuning.png'))
    plt.close()

    # 5. DEDICATED VALIDATION PHASE EVALUATION (N = 82)
    val_pred = best_svm.predict(X_val)
    val_acc = accuracy_score(y_val, val_pred)
    val_prec, val_rec, val_f1, _ = precision_recall_fscore_support(y_val, val_pred, average='macro')
    val_cm = confusion_matrix(y_val, val_pred)
    val_report = classification_report(y_val, val_pred, target_names=classes, digits=4)
    print("\n--- VALIDATION EVALUATION (N = 82) ---")
    print(f"Validation Accuracy: {val_acc*100:.2f}% | Macro F1: {val_f1:.4f}")

    # Plot: Validation Confusion Matrix
    fig, ax = plt.subplots(figsize=(5.0, 4.2), dpi=300)
    sns.heatmap(val_cm, annot=True, fmt='d', cmap='Greys', xticklabels=classes, yticklabels=classes,
                cbar=False, annot_kws={'size': 11, 'fontweight': 'bold'}, linewidths=0.5, linecolor='black', ax=ax)
    ax.set_title('Confusion Matrix: Validation Set ($N = 82$)', pad=10, fontweight='bold')
    ax.set_xlabel('Predicted Condition Class', labelpad=6)
    ax.set_ylabel('Ground-Truth Class', labelpad=6)
    plt.tight_layout()
    fig.savefig(os.path.join(plot_dir, 'fig_val_confusion_matrix.png'))
    plt.close()

    # 6. DEDICATED FINAL TESTING PHASE EVALUATION (N = 82)
    test_pred = best_svm.predict(X_test)
    test_acc = accuracy_score(y_test, test_pred)
    test_prec, test_rec, test_f1, _ = precision_recall_fscore_support(y_test, test_pred, average='macro')
    test_cm = confusion_matrix(y_test, test_pred)
    test_report = classification_report(y_test, test_pred, target_names=classes, digits=4)
    print("\n--- HELD-OUT TESTING EVALUATION (N = 82) ---")
    print(f"Test Accuracy: {test_acc*100:.2f}% | Macro F1: {test_f1:.4f}")

    # Plot: Test Confusion Matrix
    fig, ax = plt.subplots(figsize=(5.0, 4.2), dpi=300)
    sns.heatmap(test_cm, annot=True, fmt='d', cmap='Greys', xticklabels=classes, yticklabels=classes,
                cbar=False, annot_kws={'size': 11, 'fontweight': 'bold'}, linewidths=0.5, linecolor='black', ax=ax)
    ax.set_title('Confusion Matrix: Held-Out Test Set ($N = 82$)', pad=10, fontweight='bold')
    ax.set_xlabel('Predicted Condition Class', labelpad=6)
    ax.set_ylabel('Ground-Truth Class', labelpad=6)
    plt.tight_layout()
    fig.savefig(os.path.join(plot_dir, 'fig6_confusion_matrix.png'))
    plt.close()

    # 7. Benchmark Baseline Models (Random Forest & KNN)
    rf = Pipeline([('scaler', StandardScaler()), ('rf', RandomForestClassifier(n_estimators=100, random_state=42))])
    rf.fit(X_train, y_train)
    rf_val_acc = accuracy_score(y_val, rf.predict(X_val))
    rf_test_acc = accuracy_score(y_test, rf.predict(X_test))
    rf_test_f1 = precision_recall_fscore_support(y_test, rf.predict(X_test), average='macro')[2]

    knn = Pipeline([('scaler', StandardScaler()), ('knn', KNeighborsClassifier(n_neighbors=5))])
    knn.fit(X_train, y_train)
    knn_val_acc = accuracy_score(y_val, knn.predict(X_val))
    knn_test_acc = accuracy_score(y_test, knn.predict(X_test))
    knn_test_f1 = precision_recall_fscore_support(y_test, knn.predict(X_test), average='macro')[2]

    # --- Plot: 2D PCA Decision Regions ---
    pca_train = PCA(n_components=2, random_state=42)
    scaler_dec = StandardScaler()
    X_train_pca = pca_train.fit_transform(scaler_dec.fit_transform(X_train))
    X_test_pca = pca_train.transform(scaler_dec.transform(X_test))

    svm_pca = SVC(kernel=best_params['svm__kernel'], C=best_params['svm__C'], gamma='scale', random_state=42)
    svm_pca.fit(X_train_pca, y_train)

    fig, ax = plt.subplots(figsize=(7.0, 4.8), dpi=300)
    x_min, x_max = X_test_pca[:, 0].min() - 1, X_test_pca[:, 0].max() + 1
    y_min, y_max = X_test_pca[:, 1].min() - 1, X_test_pca[:, 1].max() + 1
    xx, yy = np.meshgrid(np.linspace(x_min, x_max, 250), np.linspace(y_min, y_max, 250))
    Z = svm_pca.predict(np.c_[xx.ravel(), yy.ravel()])
    Z = Z.reshape(xx.shape)
    ax.contourf(xx, yy, Z, alpha=0.15, cmap='Greys')

    for c_idx, c_name in enumerate(classes):
        mask_test = (y_test == c_idx)
        ax.scatter(X_test_pca[mask_test, 0], X_test_pca[mask_test, 1],
                   label=f"Class {c_name}", color=palette[c_name],
                   marker=markers[c_idx], s=55, edgecolors='black', alpha=0.85)
    ax.set_title('SVM Decision Partitions and Test Projections in 2D PCA Space', pad=10, fontweight='bold')
    ax.set_xlabel('Principal Component 1')
    ax.set_ylabel('Principal Component 2')
    ax.legend(title='Test Sample Classes', frameon=True, edgecolor='black')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    plt.tight_layout()
    fig.savefig(os.path.join(plot_dir, 'fig8_pca_decision_regions.png'))
    plt.close()

    # 8. Prototype Protection Module & Latency Benchmark
    bundle = {
        'model': best_svm,
        'encoder': le,
        'features': feature_cols
    }
    joblib.dump(bundle, 'fault_classifier.pkl')

    # Benchmark Latency over 1,000 runs
    test_sample = X_test.iloc[0].values.reshape(1, -1)
    for _ in range(50):
        _ = best_svm.predict(test_sample)

    N_RUNS = 1000
    t0 = time.perf_counter()
    for _ in range(N_RUNS):
        _ = best_svm.predict(test_sample)
    t1 = time.perf_counter()
    avg_latency_ms = ((t1 - t0) / N_RUNS) * 1000
    print(f"Average Inference Latency: {avg_latency_ms:.4f} ms ({avg_latency_ms*1000:.1f} microseconds)")

    # Save summary dictionary for report generation
    summary = {
        'total_raw_samples': len(df_raw),
        'clean_samples': len(df_clean),
        'num_features': len(feature_cols),
        'classes': classes,
        'best_kernel': best_params['svm__kernel'],
        'best_C': best_params['svm__C'],
        'best_gamma': best_params['svm__gamma'],
        'best_cv_macro_f1': best_cv_f1,
        'val_samples': len(X_val),
        'val_accuracy': val_acc,
        'val_macro_f1': val_f1,
        'val_cm': val_cm.tolist(),
        'val_report': val_report,
        'test_samples': len(X_test),
        'test_accuracy': test_acc,
        'test_macro_precision': test_prec,
        'test_macro_recall': test_rec,
        'test_macro_f1': test_f1,
        'test_cm': test_cm.tolist(),
        'test_report': test_report,
        'rf_val_acc': rf_val_acc,
        'rf_test_acc': rf_test_acc,
        'rf_test_f1': rf_test_f1,
        'knn_val_acc': knn_val_acc,
        'knn_test_acc': knn_test_acc,
        'knn_test_f1': knn_test_f1,
        'inference_time_ms': avg_latency_ms
    }
    joblib.dump(summary, 'academic_pipeline_results.pkl')
    print("Academic Pipeline Completed Successfully!")

if __name__ == '__main__':
    run_academic_pipeline()
