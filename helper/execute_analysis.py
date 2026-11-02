import os
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

# Set overall aesthetic style
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['font.sans-serif'] = 'Arial'
plt.rcParams['font.size'] = 10
plt.rcParams['axes.titlesize'] = 12
plt.rcParams['axes.labelsize'] = 11

def main():
    print("=" * 60)
    print("ESA PROJECT 15: FAULT CLASSIFICATION PIPELINE")
    print("=" * 60)

    # 1. Load data
    data_path = 'fault_dataset.csv'
    df_raw = pd.read_csv(data_path)
    print(f"Loaded {data_path} with shape: {df_raw.shape}")
    print("\nColumns:", list(df_raw.columns))

    print("\n--- Summary Statistics (Describe) ---")
    desc = df_raw.describe()
    print(desc)

    print("\n--- Missing values count ---")
    print(df_raw.isnull().sum())

    print("\n--- Class distribution before cleaning ---")
    print(df_raw['fault'].value_counts())

    print(f"\nTotal duplicates across all columns: {df_raw.duplicated().sum()}")
    
    # 2. Data Cleaning & Feature Separation
    # Features are electrical measurements: 9 voltages (Ua1..Uc3) and 15 currents (Ia1..Ic5)
    feature_cols = [c for c in df_raw.columns if c not in ['fault', 'line', 'position']]
    LABEL_COL = 'fault'

    # Remove exact duplicate rows (73 identical rows in 'no fault' from static load steps)
    df_clean = df_raw.drop_duplicates().copy()
    print(f"\nAfter dropping duplicate records, shape: {df_clean.shape}")
    print("Class distribution after dropping duplicates:")
    print(df_clean[LABEL_COL].value_counts())

    X = df_clean[feature_cols].copy()
    y = df_clean[LABEL_COL].copy()

    # Encode labels
    le = LabelEncoder()
    y_enc = le.fit_transform(y)
    classes = list(le.classes_)
    print(f"\nClasses encoded: {dict(enumerate(classes))}")

    # Output directory for plots
    plot_dir = 'plots'
    os.makedirs(plot_dir, exist_ok=True)

    # -------------------------------------------------------------
    # 3. Exploratory Data Analysis (EDA) Plots (Step 5)
    # -------------------------------------------------------------
    print("\nGenerating EDA Plots...")

    # Plot 1: Class Distribution
    fig, ax = plt.subplots(figsize=(7, 4.5), dpi=300)
    counts = df_clean[LABEL_COL].value_counts()
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']
    bars = ax.bar(counts.index, counts.values, color=colors, edgecolor='black', alpha=0.85, width=0.55)
    for bar in bars:
        yval = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2.0, yval + 3, f"{int(yval)}", ha='center', va='bottom', fontweight='bold')
    ax.set_title('Figure 1: Distribution of Operating and Fault Conditions', pad=12, fontweight='bold')
    ax.set_xlabel('Class Label (Fault Type / Normal Operation)', labelpad=8)
    ax.set_ylabel('Sample Count', labelpad=8)
    ax.set_ylim(0, max(counts.values) * 1.15)
    plt.tight_layout()
    p1_path = os.path.join(plot_dir, 'fig1_class_distribution.png')
    fig.savefig(p1_path)
    plt.close()
    print(f"Saved {p1_path}")

    # Plot 2: Histograms / KDE of Key Current Features per Class
    # Ia1 (Line 1 Phase A current) and Ua1 (Bus 1 Phase A voltage)
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5), dpi=300)
    palette = {'no fault': '#1f77b4', '3psc': '#d62728', '2psc': '#ff7f0e', 'spgf': '#2ca02c'}
    
    sns.histplot(data=df_clean, x='Ia1', hue=LABEL_COL, kde=True, ax=axes[0], palette=palette, bins=25, alpha=0.5)
    axes[0].set_title('(a) Phase A Current at Bus 1 ($I_{a1}$)', fontweight='bold')
    axes[0].set_xlabel('Current $I_{a1}$ (kA)')
    axes[0].set_ylabel('Density / Frequency')

    sns.histplot(data=df_clean, x='Ua1', hue=LABEL_COL, kde=True, ax=axes[1], palette=palette, bins=25, alpha=0.5)
    axes[1].set_title('(b) Phase A Voltage at Bus 1 ($U_{a1}$)', fontweight='bold')
    axes[1].set_xlabel('Voltage $U_{a1}$ (kV)')
    axes[1].set_ylabel('Density / Frequency')

    fig.suptitle('Figure 2: Feature Distributions Across Fault Types and Normal State', fontweight='bold', y=1.02)
    plt.tight_layout()
    p2_path = os.path.join(plot_dir, 'fig2_feature_distributions.png')
    fig.savefig(p2_path, bbox_inches='tight')
    plt.close()
    print(f"Saved {p2_path}")

    # Plot 3: Correlation Heatmap
    fig, ax = plt.subplots(figsize=(10, 8), dpi=300)
    corr = X.corr()
    mask = np.triu(np.ones_like(corr, dtype=bool))
    sns.heatmap(corr, mask=mask, cmap='vlag', vmin=-1, vmax=1, annot=False,
                linewidths=0.5, cbar_kws={'label': 'Pearson Correlation'}, ax=ax)
    ax.set_title('Figure 3: Feature Correlation Heatmap (24 Voltages and Currents)', pad=12, fontweight='bold')
    plt.tight_layout()
    p3_path = os.path.join(plot_dir, 'fig3_correlation_heatmap.png')
    fig.savefig(p3_path)
    plt.close()
    print(f"Saved {p3_path}")

    # Plot 4: Box Plots of Voltages and Currents across Fault Types
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.8), dpi=300)
    # Average voltage at Bus 1 and Bus 2
    df_clean['U_mean'] = df_clean[['Ua1', 'Ub1', 'Uc1']].mean(axis=1)
    df_clean['I_max'] = df_clean[['Ia1', 'Ib1', 'Ic1']].max(axis=1)

    sns.boxplot(data=df_clean, x=LABEL_COL, y='U_mean', ax=axes[0], palette=palette)
    axes[0].set_title('(a) Mean Bus 1 Voltage by Condition', fontweight='bold')
    axes[0].set_xlabel('Fault Type')
    axes[0].set_ylabel('Mean Phase Voltage (kV)')

    sns.boxplot(data=df_clean, x=LABEL_COL, y='I_max', ax=axes[1], palette=palette)
    axes[1].set_title('(b) Maximum Line 1 Current by Condition', fontweight='bold')
    axes[1].set_xlabel('Fault Type')
    axes[1].set_ylabel('Peak Phase Current (kA)')

    fig.suptitle('Figure 4: Voltage Sags and Current Inrushes Across Fault Categories', fontweight='bold', y=1.02)
    plt.tight_layout()
    p4_path = os.path.join(plot_dir, 'fig4_boxplots_voltages_currents.png')
    fig.savefig(p4_path, bbox_inches='tight')
    plt.close()
    print(f"Saved {p4_path}")

    # Plot 5: 2D PCA Scatter Plot
    scaler_pca = StandardScaler()
    X_scaled_all = scaler_pca.fit_transform(X)
    pca = PCA(n_components=2, random_state=42)
    X_pca = pca.fit_transform(X_scaled_all)
    var_exp = pca.explained_variance_ratio_

    fig, ax = plt.subplots(figsize=(8, 5.5), dpi=300)
    for c_idx, c_name in enumerate(classes):
        mask_c = (y_enc == c_idx)
        ax.scatter(X_pca[mask_c, 0], X_pca[mask_c, 1],
                   label=c_name, color=palette[c_name],
                   alpha=0.75, edgecolors='k', s=50)
    ax.set_title(f'Figure 5: 2D PCA Feature Space Representation (Explained Variance: {var_exp.sum()*100:.1f}%)', pad=12, fontweight='bold')
    ax.set_xlabel(f'Principal Component 1 ({var_exp[0]*100:.1f}% variance)')
    ax.set_ylabel(f'Principal Component 2 ({var_exp[1]*100:.1f}% variance)')
    ax.legend(title='Fault Type / Condition', frameon=True)
    plt.tight_layout()
    p5_path = os.path.join(plot_dir, 'fig5_pca_scatter.png')
    fig.savefig(p5_path)
    plt.close()
    print(f"Saved {p5_path}")

    # -------------------------------------------------------------
    # 4. Training, Validation, and Testing Split (Step 6)
    # -------------------------------------------------------------
    print("\n--- Splitting Dataset (70% Train, 15% Validation, 15% Test) ---")
    X_train, X_temp, y_train, y_temp = train_test_split(
        X, y_enc, test_size=0.30, stratify=y_enc, random_state=42
    )
    X_val, X_test, y_val, y_test = train_test_split(
        X_temp, y_temp, test_size=0.50, stratify=y_temp, random_state=42
    )
    print(f"Train samples: {len(X_train)} (70%)")
    print(f"Val samples:   {len(X_val)} (15%)")
    print(f"Test samples:  {len(X_test)} (15%)")

    # -------------------------------------------------------------
    # 5. Hyperparameter Tuning using GridSearchCV
    # -------------------------------------------------------------
    print("\n--- Running GridSearchCV for SVM ---")
    pipe_svm = Pipeline([
        ('scaler', StandardScaler()),
        ('svm', SVC(probability=True, random_state=42))
    ])

    param_grid = {
        'svm__kernel': ['linear', 'rbf'],
        'svm__C': [0.1, 1, 10, 100],
        'svm__gamma': ['scale', 0.01, 0.1, 1]
    }

    cv_stratified = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    grid_search = GridSearchCV(
        pipe_svm, param_grid, cv=cv_stratified,
        scoring='f1_macro', n_jobs=1, return_train_score=True
    )
    grid_search.fit(X_train, y_train)

    best_params = grid_search.best_params_
    best_cv_f1 = grid_search.best_score_
    print(f"Best Hyperparameters: {best_params}")
    print(f"Best 5-Fold Stratified CV Macro F1-Score: {best_cv_f1:.4f}")

    best_svm = grid_search.best_estimator_

    # -------------------------------------------------------------
    # 6. Model Evaluation on Validation and Test Sets (Step 7)
    # -------------------------------------------------------------
    y_val_pred = best_svm.predict(X_val)
    val_acc = accuracy_score(y_val, y_val_pred)
    print(f"Validation Accuracy: {val_acc:.4f} ({val_acc*100:.2f}%)")

    y_test_pred = best_svm.predict(X_test)
    test_acc = accuracy_score(y_test, y_test_pred)
    print(f"Test Accuracy:       {test_acc:.4f} ({test_acc*100:.2f}%)")

    prec_m, rec_m, f1_m, _ = precision_recall_fscore_support(y_test, y_test_pred, average='macro')
    prec_w, rec_w, f1_w, _ = precision_recall_fscore_support(y_test, y_test_pred, average='weighted')
    print(f"Test Macro Precision: {prec_m:.4f}, Recall: {rec_m:.4f}, F1: {f1_m:.4f}")
    print(f"Test Weighted F1:     {f1_w:.4f}")

    clf_report = classification_report(y_test, y_test_pred, target_names=classes, digits=4)
    print("\n--- Test Set Classification Report ---")
    print(clf_report)

    cm = confusion_matrix(y_test, y_test_pred)
    print("\nConfusion Matrix:")
    print(cm)

    # Plot 6: Confusion Matrix
    fig, ax = plt.subplots(figsize=(6, 5), dpi=300)
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                xticklabels=classes, yticklabels=classes,
                cbar=True, ax=ax, annot_kws={'size': 12, 'weight': 'bold'})
    ax.set_title('Figure 6: Confusion Matrix of Optimized SVM on Test Set', pad=12, fontweight='bold')
    ax.set_xlabel('Predicted Fault Type', labelpad=8)
    ax.set_ylabel('Actual Ground-Truth Fault Type', labelpad=8)
    plt.tight_layout()
    p6_path = os.path.join(plot_dir, 'fig6_confusion_matrix.png')
    fig.savefig(p6_path)
    plt.close()
    print(f"Saved {p6_path}")

    # Plot 7: Hyperparameter Sensitivity (Accuracy vs C for different kernels & gamma)
    results_df = pd.DataFrame(grid_search.cv_results_)
    fig, ax = plt.subplots(figsize=(7.5, 4.5), dpi=300)
    
    # Filter for RBF gamma='scale' and linear
    rbf_scale = results_df[(results_df['param_svm__kernel'] == 'rbf') & (results_df['param_svm__gamma'] == 'scale')]
    linear_res = results_df[(results_df['param_svm__kernel'] == 'linear') & (results_df['param_svm__gamma'] == 'scale')]
    rbf_g01 = results_df[(results_df['param_svm__kernel'] == 'rbf') & (results_df['param_svm__gamma'] == 0.1)]

    ax.plot(rbf_scale['param_svm__C'].astype(float), rbf_scale['mean_test_score'],
            marker='o', lw=2, color='#1f77b4', label=r'RBF Kernel ($\gamma$=scale)')
    ax.plot(rbf_g01['param_svm__C'].astype(float), rbf_g01['mean_test_score'],
            marker='s', lw=2, color='#2ca02c', label=r'RBF Kernel ($\gamma$=0.1)')
    ax.plot(linear_res['param_svm__C'].astype(float), linear_res['mean_test_score'],
            marker='^', lw=2, color='#d62728', linestyle='--', label='Linear Kernel')

    ax.set_xscale('log')
    ax.set_title('Figure 7: SVM Hyperparameter Tuning (Cross-Validation Macro F1 vs Penalty Parameter C)', pad=12, fontweight='bold')
    ax.set_xlabel('Penalty Parameter C (log scale)', labelpad=8)
    ax.set_ylabel('5-Fold CV Macro F1-Score', labelpad=8)
    ax.grid(True, which='both', linestyle='--', alpha=0.6)
    ax.legend(frameon=True)
    plt.tight_layout()
    p7_path = os.path.join(plot_dir, 'fig7_hyperparameter_tuning.png')
    fig.savefig(p7_path)
    plt.close()
    print(f"Saved {p7_path}")

    # -------------------------------------------------------------
    # 7. Comparison with Random Forest and KNN Baseline Models
    # -------------------------------------------------------------
    print("\n--- Training Baseline Models (Random Forest & KNN) ---")
    pipe_rf = Pipeline([('scaler', StandardScaler()), ('rf', RandomForestClassifier(n_estimators=100, random_state=42))])
    pipe_rf.fit(X_train, y_train)
    rf_test_acc = accuracy_score(y_test, pipe_rf.predict(X_test))
    rf_f1_macro = precision_recall_fscore_support(y_test, pipe_rf.predict(X_test), average='macro')[2]

    pipe_knn = Pipeline([('scaler', StandardScaler()), ('knn', KNeighborsClassifier(n_neighbors=5))])
    pipe_knn.fit(X_train, y_train)
    knn_test_acc = accuracy_score(y_test, pipe_knn.predict(X_test))
    knn_f1_macro = precision_recall_fscore_support(y_test, pipe_knn.predict(X_test), average='macro')[2]

    print(f"SVM Test Accuracy:           {test_acc*100:.2f}% | Macro F1: {f1_m*100:.2f}%")
    print(f"Random Forest Test Accuracy:  {rf_test_acc*100:.2f}% | Macro F1: {rf_f1_macro*100:.2f}%")
    print(f"KNN Test Accuracy:            {knn_test_acc*100:.2f}% | Macro F1: {knn_f1_macro*100:.2f}%")

    # Plot 8: PCA 2D Decision Predictions
    pca_train = PCA(n_components=2, random_state=42)
    scaler_dec = StandardScaler()
    X_train_pca = pca_train.fit_transform(scaler_dec.fit_transform(X_train))
    X_test_pca = pca_train.transform(scaler_dec.transform(X_test))

    svm_pca = SVC(kernel=best_params['svm__kernel'], C=best_params['svm__C'], gamma='scale', random_state=42)
    svm_pca.fit(X_train_pca, y_train)
    y_test_pca_pred = svm_pca.predict(X_test_pca)

    fig, ax = plt.subplots(figsize=(8, 5.5), dpi=300)
    # Decision mesh
    x_min, x_max = X_test_pca[:, 0].min() - 1, X_test_pca[:, 0].max() + 1
    y_min, y_max = X_test_pca[:, 1].min() - 1, X_test_pca[:, 1].max() + 1
    xx, yy = np.meshgrid(np.linspace(x_min, x_max, 250), np.linspace(y_min, y_max, 250))
    Z = svm_pca.predict(np.c_[xx.ravel(), yy.ravel()])
    Z = Z.reshape(xx.shape)
    ax.contourf(xx, yy, Z, alpha=0.25, cmap='tab10')

    for c_idx, c_name in enumerate(classes):
        mask_test = (y_test == c_idx)
        ax.scatter(X_test_pca[mask_test, 0], X_test_pca[mask_test, 1],
                   label=f"Actual: {c_name}", color=palette[c_name],
                   s=65, edgecolors='k', alpha=0.9)
    ax.set_title('Figure 8: SVM Decision Regions and Test Set Predictions in 2D PCA Space', pad=12, fontweight='bold')
    ax.set_xlabel('Principal Component 1')
    ax.set_ylabel('Principal Component 2')
    ax.legend(title='Test Sample Classes', frameon=True)
    plt.tight_layout()
    p8_path = os.path.join(plot_dir, 'fig8_pca_decision_regions.png')
    fig.savefig(p8_path)
    plt.close()
    print(f"Saved {p8_path}")

    # -------------------------------------------------------------
    # 8. Prototype Digital Protection Module (Step 8)
    # -------------------------------------------------------------
    print("\n--- Building Prototype Protection Module ---")
    model_bundle = {
        'model': best_svm,
        'encoder': le,
        'feature_names': feature_cols,
        'best_params': best_params
    }
    bundle_path = 'fault_classifier.pkl'
    joblib.dump(model_bundle, bundle_path)
    print(f"Saved model bundle to {bundle_path}")

    def classify_fault(sample_vector):
        """
        Accepts a list or 1D array of 24 electrical measurement features:
        [Ua1, Ub1, Uc1, Ua2, Ub2, Uc2, Ua3, Ub3, Uc3,
         Ia1, Ib1, Ic1, Ia2, Ib2, Ic2, Ia3, Ib3, Ic3, Ia4, Ib4, Ic4, Ia5, Ib5, Ic5]
        Returns predicted fault classification string.
        """
        bundle = joblib.load('fault_classifier.pkl')
        model = bundle['model']
        encoder = bundle['encoder']
        arr = np.array(sample_vector).reshape(1, -1)
        pred = model.predict(arr)
        proba = model.predict_proba(arr)[0]
        label = encoder.inverse_transform(pred)[0]
        confidence = proba[pred[0]] * 100
        return label, confidence

    # Test on 3 representative samples from test set
    print("\nTesting Prototype Module on 3 Sample Rows:")
    test_indices = [0, 15, 30]
    sample_tests = []
    for idx in test_indices:
        sample_row = X_test.iloc[idx].values
        actual_label = classes[y_test[idx]]
        pred_label, conf = classify_fault(sample_row)
        sample_tests.append({
            'index': idx,
            'actual': actual_label,
            'predicted': pred_label,
            'confidence': conf,
            'sample_values': sample_row[:6] # first 6 features
        })
        print(f"Sample {idx} -> Actual: {actual_label:10s} | Predicted: {pred_label:10s} | Confidence: {conf:.2f}%")

    # Real-Time Inference Speed Benchmark (1000 iterations)
    sample_vec = X_test.iloc[0].values
    loaded_bundle = joblib.load('fault_classifier.pkl')
    m_pipeline = loaded_bundle['model']
    enc = loaded_bundle['encoder']

    # Warm-up
    for _ in range(50):
        _ = m_pipeline.predict(sample_vec.reshape(1, -1))

    n_runs = 1000
    t0 = time.perf_counter()
    for _ in range(n_runs):
        _ = m_pipeline.predict(sample_vec.reshape(1, -1))
    t1 = time.perf_counter()
    avg_inference_time_ms = ((t1 - t0) / n_runs) * 1000
    print(f"\nInference Benchmark: {avg_inference_time_ms:.4f} ms per sample ({avg_inference_time_ms*1000:.1f} microseconds)")
    print(f"In a 50 Hz power system (1 cycle = 20.0 ms), inference takes {avg_inference_time_ms / 20.0 * 100:.3f}% of one cycle.")

    # -------------------------------------------------------------
    # 9. Block Diagram Generation (Step 9)
    # -------------------------------------------------------------
    print("\nGenerating System Block Diagram (Figure 6.2)...")
    fig, ax = plt.subplots(figsize=(12, 4.2), dpi=300)
    ax.axis('off')

    blocks = [
        ("110 kV Grid\nRaw Dataset\n(618 Samples,\n24 Sensors)", "#E1F5FE", "#0288D1"),
        ("Data Cleaning\n& Verification\n(Deduplication,\nNo Nulls in X)", "#E8F5E9", "#388E3C"),
        ("Standard\nScaling\n(Z-Score Norm:\nMean 0, Var 1)", "#FFF3E0", "#F57C00"),
        ("Stratified Split\n(70% Train,\n15% Val,\n15% Test)", "#EDE7F6", "#7E57C2"),
        ("SVM Tuning\n(GridSearchCV,\n5-Fold CV,\nRBF / C / γ)", "#FCE4EC", "#C2185B"),
        ("Model\nEvaluation\n(Test Acc,\nConf Matrix,\nF1-Score)", "#E0F2F1", "#00897B"),
        ("Prototype\nFault Classifier\n(Sub-millisecond\nInference)", "#FFFDE7", "#FBC02D"),
        ("Relay Action\nDecision\n(Selective Trip\n& Reclosure)", "#FFEBEE", "#D32F2F")
    ]

    n_b = len(blocks)
    box_w = 0.095
    box_h = 0.65
    spacing = (1.0 - (n_b * box_w)) / (n_b + 1)

    from matplotlib.patches import FancyBboxPatch
    for i, (text, bg_color, border_color) in enumerate(blocks):
        x = spacing + i * (box_w + spacing)
        y = 0.18
        rect = FancyBboxPatch((x, y), box_w, box_h, facecolor=bg_color,
                              edgecolor=border_color, linewidth=2, transform=ax.transAxes,
                              boxstyle='round,pad=0.015')
        ax.add_patch(rect)
        ax.text(x + box_w/2, y + box_h/2, text, ha='center', va='center',
                fontsize=8.5, fontweight='bold', color='#1A237E', transform=ax.transAxes)

        # Draw connecting arrow to next block
        if i < n_b - 1:
            arrow_x = x + box_w
            arrow_next_x = x + box_w + spacing
            arrow_y = y + box_h/2
            ax.annotate('', xy=(arrow_next_x, arrow_y), xytext=(arrow_x, arrow_y),
                        xycoords='axes fraction', textcoords='axes fraction',
                        arrowprops=dict(arrowstyle="->", color="#37474F", lw=2, mutation_scale=15))

    ax.set_title("Figure 6.2: End-to-End Workflow Architecture of the Intelligent Fault Classification System",
                 fontsize=12, fontweight='bold', pad=15)
    plt.tight_layout()
    diagram_path = os.path.join(plot_dir, 'fig_block_diagram.png')
    fig.savefig(diagram_path, bbox_inches='tight')
    plt.close()
    print(f"Saved {diagram_path}")

    # Save summary stats and results to a dictionary for docx updating
    results_summary = {
        'total_raw_samples': len(df_raw),
        'clean_samples': len(df_clean),
        'num_features': len(feature_cols),
        'num_classes': len(classes),
        'classes': classes,
        'feature_names': feature_cols,
        'best_kernel': best_params['svm__kernel'],
        'best_C': best_params['svm__C'],
        'best_gamma': best_params['svm__gamma'],
        'best_cv_macro_f1': best_cv_f1,
        'val_accuracy': val_acc,
        'test_accuracy': test_acc,
        'test_macro_precision': prec_m,
        'test_macro_recall': rec_m,
        'test_macro_f1': f1_m,
        'test_weighted_f1': f1_w,
        'rf_test_acc': rf_test_acc,
        'rf_f1_macro': rf_f1_macro,
        'knn_test_acc': knn_test_acc,
        'knn_f1_macro': knn_f1_macro,
        'inference_time_ms': avg_inference_time_ms,
        'sample_tests': sample_tests,
        'classification_report_str': clf_report,
        'confusion_matrix': cm.tolist()
    }
    joblib.dump(results_summary, 'pipeline_results_summary.pkl')
    print("\nSaved pipeline_results_summary.pkl successfully!")
    print("=" * 60)

if __name__ == '__main__':
    main()
