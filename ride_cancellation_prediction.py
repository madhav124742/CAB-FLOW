"""
ride_cancellation_prediction.py
PART 3:
- Concept of Classification & Classification vs Regression
- Performance Metrics for Classification:
  * Confusion Matrix
  * Precision, Recall, F1-Score, Accuracy, Specificity, ROC-AUC
- Classification Algorithms:
  * Logistic Regression
  * K-Nearest Neighbors (KNN)
  * Naive Bayes (GaussianNB)
  * Support Vector Machine (Linear / RBF SVC)
  * Decision Tree Classification (Information Gain / Entropy & Gini Index)
  * Random Forest Classification (Ensemble Bagging)
- Bias vs Variance Trade-off
- Understanding Underfitting & Overfitting
"""

import os
import matplotlib
matplotlib.use('Agg')
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import train_test_split, learning_curve
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, classification_report, roc_curve, auc
)

# Classifiers
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.svm import LinearSVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
import joblib

os.makedirs('plots', exist_ok=True)
os.makedirs('models', exist_ok=True)

def print_header(title):
    print("\n" + "="*80)
    print(f" {title} ")
    print("="*80)

def section_3_concept_theory():
    print_header("SECTION III [A]: CLASSIFICATION CONCEPTS & CLASSIFICATION VS REGRESSION")
    print("""
    [1] CLASSIFICATION VS REGRESSION:
    - Objective:
      * Regression predicts continuous numeric quantities (e.g., Booking Value / Fare ₹, ETAs).
      * Classification assigns ride observations to discrete categorical classes (e.g. Cancelled [1] vs Completed [0]).
    - Output Space:
      * Regression: y in R (scalar continuous domain).
      * Classification: y in {0, 1} with posterior probabilities P(Y=1|X) in [0, 1].
    - Loss Functions:
      * Regression: MSE, MAE, Huber Loss.
      * Classification: Binary Cross-Entropy (Log-Loss), Gini Impurity, Entropy (Information Gain).

    [2] BIAS VS VARIANCE DILEMMA:
    - High Bias (Underfitting): Model is overly rigid; fails to capture non-linear decision boundaries.
    - High Variance (Overfitting): Model captures noisy samples or idiosyncrasies in training sets.
    - Balanced Regularization: Ensembles (Random Forest) and tuned margin classifiers mitigating variance.
    """)

def run_classification_pipeline():
    print_header("SECTION III [B]: CLASSIFICATION MODEL BENCHMARKING & EVALUATION")
    
    # Load dataset
    if os.path.exists('ncr_ride_bookings.csv'):
        raw_df = pd.read_csv('ncr_ride_bookings.csv')
    else:
        raw_df = pd.read_csv('cab_rides_dataset.csv')
    
    print(f"Loaded dataset for classification analysis: {raw_df.shape}")

    # Binary Target Formulation: Trip Cancellation Risk (1 = Cancelled by Customer or Driver, 0 = Completed)
    if 'Booking Status' in raw_df.columns:
        # Filter completed vs cancelled
        target_df = raw_df[raw_df['Booking Status'].isin(['Completed', 'Cancelled by Driver', 'Cancelled by Customer'])].copy()
        target_df['trip_cancelled'] = target_df['Booking Status'].apply(lambda s: 0 if s == 'Completed' else 1)
        
        # Feature preparation
        if 'Date' in target_df.columns and 'Time' in target_df.columns:
            dt = pd.to_datetime(target_df['Date'] + ' ' + target_df['Time'], errors='coerce')
            target_df['hour'] = dt.dt.hour.fillna(12).astype(int)
            target_df['dayofweek'] = dt.dt.dayofweek.fillna(0).astype(int)
            target_df['is_weekend'] = target_df['dayofweek'].isin([5, 6]).astype(int)
        
        # Handling VTAT (Vehicle Time to Arrival at pickup)
        if 'Avg VTAT' in target_df.columns:
            target_df['Avg VTAT'] = target_df['Avg VTAT'].fillna(target_df['Avg VTAT'].median())
        
        features_num = ['Avg VTAT', 'hour', 'is_weekend']
        features_cat = ['Vehicle Type']
        
        df_encoded = pd.get_dummies(target_df[features_num + features_cat + ['trip_cancelled']], columns=features_cat, drop_first=True)
        feature_cols = [c for c in df_encoded.columns if c != 'trip_cancelled']
        
        # Subsample for balanced, fast evaluation across all classifiers
        df_sub = df_encoded.sample(n=min(25000, len(df_encoded)), random_state=42)
        X = df_sub[feature_cols].astype(float)
        y = df_sub['trip_cancelled'].astype(int)
    else:
        # Fallback to cleaned_cab_data format
        df = pd.read_csv('cleaned_cab_data.csv')
        nominal_cols = [c for c in ['cab_type', 'weather', 'pickup_location', 'payment_type'] if c in df.columns]
        df_encoded = pd.get_dummies(df, columns=nominal_cols, drop_first=True)
        ignore_cols = ['trip_id', 'timestamp', 'day_of_week', 'traffic_condition', 'trip_cancelled']
        feature_cols = [c for c in df_encoded.columns if c not in ignore_cols and np.issubdtype(df_encoded[c].dtype, np.number)]
        X = df_encoded[feature_cols].astype(float)
        y = df_encoded['trip_cancelled'].astype(int)

    print(f"Class distribution in trip_cancelled:\n{y.value_counts(normalize=True).round(3)}")

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=42, stratify=y
    )

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    joblib.dump(scaler, 'models/clf_scaler.joblib')

    # Classifiers to benchmark
    classifiers = {
        'Logistic Regression': LogisticRegression(max_iter=1000, random_state=42),
        'K-Nearest Neighbors (KNN)': KNeighborsClassifier(n_neighbors=7),
        'Naive Bayes (Gaussian)': GaussianNB(),
        'Support Vector Machine (Linear)': LinearSVC(C=1.0, random_state=42, max_iter=2000),
        'Decision Tree (Gini)': DecisionTreeClassifier(criterion='gini', max_depth=6, random_state=42),
        'Decision Tree (Information Gain)': DecisionTreeClassifier(criterion='entropy', max_depth=6, random_state=42),
        'Random Forest Classifier': RandomForestClassifier(n_estimators=100, max_depth=8, random_state=42, n_jobs=-1)
    }

    results = []
    trained_models = {}
    roc_curves = {}
    best_cm = None
    best_clf_name = ""
    best_f1 = -1

    for name, clf in classifiers.items():
        clf.fit(X_train_scaled, y_train)
        y_pred = clf.predict(X_test_scaled)

        # Probabilities or decision function for ROC
        if hasattr(clf, "predict_proba"):
            y_proba = clf.predict_proba(X_test_scaled)[:, 1]
        elif hasattr(clf, "decision_function"):
            y_proba = clf.decision_function(X_test_scaled)
        else:
            y_proba = y_pred

        acc = accuracy_score(y_test, y_pred)
        prec = precision_score(y_test, y_pred, zero_division=0)
        rec = recall_score(y_test, y_pred, zero_division=0)
        f1 = f1_score(y_test, y_pred, zero_division=0)

        fpr, tpr, _ = roc_curve(y_test, y_proba)
        roc_auc = auc(fpr, tpr)
        roc_curves[name] = (fpr, tpr, roc_auc)

        results.append({
            'Algorithm': name,
            'Accuracy': round(acc, 4),
            'Precision': round(prec, 4),
            'Recall': round(rec, 4),
            'F1-Score': round(f1, 4),
            'ROC_AUC': round(roc_auc, 4)
        })

        model_key = name.lower().replace(' ', '_').replace('(', '').replace(')', '')
        joblib.dump(clf, f"models/{model_key}.joblib")

        if f1 > best_f1:
            best_f1 = f1
            best_clf_name = name
            best_cm = confusion_matrix(y_test, y_pred)

    summary_df = pd.DataFrame(results).sort_values(by='F1-Score', ascending=False)
    print("\nClassification Benchmark Results:")
    print(summary_df.to_string(index=False))

    # Visualization
    fig, axes = plt.subplots(1, 3, figsize=(20, 6))
    fig.suptitle('Classification Benchmarking, Confusion Matrix & ROC Diagnostics', fontsize=15, fontweight='bold')

    # 1. Best Confusion Matrix
    sns.heatmap(best_cm, annot=True, fmt='d', cmap='Blues', ax=axes[0], cbar=False,
                xticklabels=['Completed (0)', 'Cancelled (1)'],
                yticklabels=['Completed (0)', 'Cancelled (1)'])
    axes[0].set_title(f'Top Classifier Confusion Matrix: {best_clf_name}\n(F1={best_f1:.3f})')
    axes[0].set_ylabel('True Label')
    axes[0].set_xlabel('Predicted Label')

    # 2. Multi-model ROC Curves
    for name, (fpr, tpr, roc_auc) in roc_curves.items():
        axes[1].plot(fpr, tpr, lw=1.8, label=f"{name[:14]} (AUC={roc_auc:.2f})")
    axes[1].plot([0, 1], [0, 1], 'k--', lw=1.5)
    axes[1].set_title('Receiver Operating Characteristic (ROC) Comparison')
    axes[1].set_xlabel('False Positive Rate (1 - Specificity)')
    axes[1].set_ylabel('True Positive Rate (Recall)')
    axes[1].legend(loc='lower right', fontsize=8)

    # 3. Learning Curves for Random Forest
    train_sizes, train_scores, val_scores = learning_curve(
        RandomForestClassifier(n_estimators=40, max_depth=6, random_state=42, n_jobs=-1),
        X_train_scaled, y_train, cv=3, scoring='f1',
        train_sizes=np.linspace(0.2, 1.0, 5), random_state=42
    )
    train_mean = np.mean(train_scores, axis=1)
    val_mean = np.mean(val_scores, axis=1)

    axes[2].plot(train_sizes, train_mean, 'o-', color='crimson', label='Training F1 (Bias check)')
    axes[2].plot(train_sizes, val_mean, 'o-', color='navy', label='Cross-Val F1 (Variance check)')
    axes[2].set_title('Learning Curves (Demonstrating Bias vs Variance Trade-off)')
    axes[2].set_xlabel('Training Samples')
    axes[2].set_ylabel('F1 Score')
    axes[2].legend()

    plt.tight_layout()
    clf_plot_path = os.path.join('plots', 'classification_benchmarks.png')
    plt.savefig(clf_plot_path, dpi=200)
    plt.close()
    print(f" -> Saved: {clf_plot_path}")

    return summary_df

if __name__ == '__main__':
    section_3_concept_theory()
    run_classification_pipeline()
