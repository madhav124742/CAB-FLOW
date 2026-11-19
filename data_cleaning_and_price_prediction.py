"""
data_cleaning_and_price_prediction.py
PART 2:
- Data Pre-processing: Need & Phases of pre-processing
- Handling Duplicate Data & Missing Values (Mean/Median/Mode Imputation)
- Handling Categorical Data: Label Encoding, One-Hot Encoding & Dummy Variable Trap (drop_first)
- Dataset Splitting: Training Dataset vs Testing Dataset
- Feature Scaling: Standardization (Z-score) vs Normalization (Min-Max)
- Outlier Detection Approaches:
  * IQR (Interquartile Range) Method
  * Z-score Method
  * Isolation Forest
- Regression for Data Analysis:
  * Simple Linear Regression (Fare vs Distance)
  * Multiple Linear Regression (Fare vs all drivers)
  * Polynomial Regression (Degree 2 non-linear fit)
  * Random Forest Regression
- Performance Metrics for Regression:
  * Mean Squared Error (MSE)
  * Root Mean Squared Error (RMSE)
  * Mean Absolute Error (MAE)
  * R2 Score (Coefficient of Determination)
"""

import os
import matplotlib
matplotlib.use('Agg')
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, MinMaxScaler, LabelEncoder, PolynomialFeatures
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.ensemble import IsolationForest
import joblib

os.makedirs('plots', exist_ok=True)
os.makedirs('models', exist_ok=True)

def print_header(title):
    print("\n" + "="*80)
    print(f" {title} ")
    print("="*80)

def run_preprocessing_pipeline(df):
    print_header("SECTION II [A]: DATA PRE-PROCESSING & CLEANING PIPELINE")
    print(f"Initial raw dataset shape: {df.shape}")
    
    # 1. Handling Duplicate Data
    dup_count = df.duplicated().sum()
    print(f"1. Duplicate Rows Detected: {dup_count}")
    df_clean = df.drop_duplicates().copy()
    print(f"   Shape after dropping duplicates: {df_clean.shape}")
    
    # 2. Filtering for Fare/Pricing Machine Learning Target
    # In realistic ride-hailing data, fare is realized upon completion or trip commencement
    if 'Booking Status' in df_clean.columns:
        print("\n2. Filtering and Imputing for Fare Analysis:")
        # Focus on Completed rides where trip distance and fare amount are fully observed
        completed_mask = df_clean['Booking Status'] == 'Completed'
        df_pricing = df_clean[completed_mask].copy()
        print(f"   Filtered completed rides with observed fare: {df_pricing.shape[0]} rows")
    else:
        df_pricing = df_clean.copy()

    # Feature Engineering from Temporal fields
    if 'Date' in df_pricing.columns and 'Time' in df_pricing.columns:
        dt_series = pd.to_datetime(df_pricing['Date'] + ' ' + df_pricing['Time'], errors='coerce')
        df_pricing['hour'] = dt_series.dt.hour.fillna(12).astype(int)
        df_pricing['dayofweek'] = dt_series.dt.dayofweek.fillna(0).astype(int)
        df_pricing['is_weekend'] = df_pricing['dayofweek'].isin([5, 6]).astype(int)
        print("   Engineered temporal features: 'hour', 'dayofweek', 'is_weekend'")

    # Missing Value Handling
    print("\n3. Missing Value Imputation Analysis:")
    missing_series = df_pricing.isnull().sum()
    cols_with_missing = missing_series[missing_series > 0]
    if len(cols_with_missing) > 0:
        print(cols_with_missing)
        if 'Driver Ratings' in df_pricing.columns:
            med_driver_rating = df_pricing['Driver Ratings'].median()
            df_pricing['Driver Ratings'] = df_pricing['Driver Ratings'].fillna(med_driver_rating)
            print(f"   Imputed missing 'Driver Ratings' with Median: {med_driver_rating:.2f}")
        if 'Customer Rating' in df_pricing.columns:
            med_cust_rating = df_pricing['Customer Rating'].median()
            df_pricing['Customer Rating'] = df_pricing['Customer Rating'].fillna(med_cust_rating)
            print(f"   Imputed missing 'Customer Rating' with Median: {med_cust_rating:.2f}")
        if 'Payment Method' in df_pricing.columns:
            mode_pm = df_pricing['Payment Method'].mode()[0]
            df_pricing['Payment Method'] = df_pricing['Payment Method'].fillna(mode_pm)
            print(f"   Imputed missing 'Payment Method' with Mode: {mode_pm}")
    else:
        print("   No missing values detected in pricing subset.")

    # 4. Outlier Detection Approaches on Target (Booking Value)
    target_col = 'Booking Value' if 'Booking Value' in df_pricing.columns else 'fare_amount'
    dist_col = 'Ride Distance' if 'Ride Distance' in df_pricing.columns else 'trip_distance_km'
    
    print(f"\n4. Outlier Detection on Target Feature ('{target_col}'):")
    # (a) IQR Method
    q1 = df_pricing[target_col].quantile(0.25)
    q3 = df_pricing[target_col].quantile(0.75)
    iqr = q3 - q1
    lower_bound = max(0, q1 - 1.5 * iqr)
    upper_bound = q3 + 1.5 * iqr
    iqr_outliers = df_pricing[(df_pricing[target_col] < lower_bound) | (df_pricing[target_col] > upper_bound)]
    print(f"   [a] IQR Method: Found {len(iqr_outliers)} outliers (IQR bounds: [{lower_bound:.2f}, {upper_bound:.2f}])")

    # (b) Z-score Method
    z_scores = np.abs((df_pricing[target_col] - df_pricing[target_col].mean()) / df_pricing[target_col].std())
    z_outliers = df_pricing[z_scores > 3.0]
    print(f"   [b] Z-Score (>3.0) Method: Found {len(z_outliers)} extreme statistical outliers.")

    # (c) Isolation Forest (Multivariate Outlier Detection)
    iso_features = [dist_col, target_col]
    if 'Avg VTAT' in df_pricing.columns:
        iso_features.append('Avg VTAT')
    
    iso_sample = df_pricing[iso_features].dropna().sample(min(10000, len(df_pricing)), random_state=42)
    iso = IsolationForest(contamination=0.015, random_state=42)
    iso_preds = iso.fit_predict(iso_sample)
    print(f"   [c] Isolation Forest: Detected {(iso_preds == -1).sum()} multivariate anomaly points on sample.")

    # Cap extreme fare values at the 99.5th percentile to prevent model skewing by heavy outliers
    cap_val = df_pricing[target_col].quantile(0.995)
    df_pricing[target_col] = np.clip(df_pricing[target_col], df_pricing[target_col].min(), cap_val)
    print(f"   Applied capping at 99.5th percentile ({cap_val:.2f}) to stabilize variance.")

    # 5. Categorical Data Encoding
    print("\n5. Categorical Data Encoding:")
    nominal_cols = []
    for c in ['Vehicle Type', 'Payment Method']:
        if c in df_pricing.columns:
            nominal_cols.append(c)

    # One-Hot Encoding with drop_first=True to avoid dummy variable trap (multicollinearity)
    df_encoded = pd.get_dummies(df_pricing, columns=nominal_cols, drop_first=True)
    print(f"   One-Hot Encoded {nominal_cols} with drop_first=True.")

    # Save cleaned processed dataframe
    df_pricing.to_csv('cleaned_cab_data.csv', index=False)
    print("   Cleaned dataset saved to 'cleaned_cab_data.csv'")

    return df_pricing, df_encoded

def run_regression_models(df_encoded):
    print_header("SECTION II [B]: REGRESSION MODELING & PERFORMANCE METRICS")
    
    target_col = 'Booking Value' if 'Booking Value' in df_encoded.columns else 'fare_amount'
    dist_col = 'Ride Distance' if 'Ride Distance' in df_encoded.columns else 'trip_distance_km'

    # Candidate predictor features
    candidate_features = [
        dist_col, 'Avg VTAT', 'Avg CTAT', 'Driver Ratings', 'Customer Rating',
        'hour', 'is_weekend'
    ]
    # Add one-hot encoded dummy columns
    dummy_cols = [c for c in df_encoded.columns if c.startswith('Vehicle Type_') or c.startswith('Payment Method_')]
    
    selected_num = [c for c in candidate_features if c in df_encoded.columns]
    feature_cols = selected_num + dummy_cols
    
    print(f"Target Feature: '{target_col}'")
    print(f"Predictor Features ({len(feature_cols)}): {feature_cols}")

    # Drop any remaining NAs in modeling columns
    model_df = df_encoded[feature_cols + [target_col]].dropna()
    
    # Stratified/Random train test split (80% Train, 20% Test)
    # Using 30,000 samples for swift, robust training & evaluation
    if len(model_df) > 30000:
        sample_eval_df = model_df.sample(n=30000, random_state=42)
    else:
        sample_eval_df = model_df

    X = sample_eval_df[feature_cols].astype(float)
    y = sample_eval_df[target_col].astype(float)

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20, random_state=42)
    print(f"Dataset split: Training samples = {X_train.shape[0]}, Testing samples = {X_test.shape[0]}")

    # Feature Scaling: Standardization vs Normalization Demonstration
    print("\nFeature Scaling Demonstration:")
    scaler_std = StandardScaler()
    scaler_norm = MinMaxScaler()

    dist_sample = X_train[[dist_col]]
    scaled_std = scaler_std.fit_transform(dist_sample)
    scaled_norm = scaler_norm.fit_transform(dist_sample)
    print(f"   Original Distance Mean: {dist_sample.mean().values[0]:.2f}, Std: {dist_sample.std().values[0]:.2f}")
    print(f"   Standardized (Z-Score) Mean: {scaled_std.mean():.4f}, Std: {scaled_std.std():.4f} (Target: 0, 1)")
    print(f"   Normalized (Min-Max) Min: {scaled_norm.min():.4f}, Max: {scaled_norm.max():.4f} (Target: [0, 1])")

    # Fit Scaler on all features
    scaler_all = StandardScaler()
    X_train_scaled = scaler_all.fit_transform(X_train)
    X_test_scaled = scaler_all.transform(X_test)
    joblib.dump(scaler_all, 'models/scaler_standard.joblib')

    regression_results = []

    # 1. Simple Linear Regression (Distance -> Fare)
    slr_model = LinearRegression()
    slr_model.fit(X_train[[dist_col]], y_train)
    y_pred_slr = slr_model.predict(X_test[[dist_col]])

    mse_slr = mean_squared_error(y_test, y_pred_slr)
    rmse_slr = np.sqrt(mse_slr)
    mae_slr = mean_absolute_error(y_test, y_pred_slr)
    r2_slr = r2_score(y_test, y_pred_slr)

    regression_results.append({
        'Model': 'Simple Linear Regression (Distance)',
        'MSE': round(mse_slr, 2),
        'RMSE': round(rmse_slr, 2),
        'MAE': round(mae_slr, 2),
        'R2_Score': round(r2_slr, 4)
    })

    # 2. Multiple Linear Regression (All features scaled)
    mlr_model = LinearRegression()
    mlr_model.fit(X_train_scaled, y_train)
    y_pred_mlr = mlr_model.predict(X_test_scaled)

    mse_mlr = mean_squared_error(y_test, y_pred_mlr)
    rmse_mlr = np.sqrt(mse_mlr)
    mae_mlr = mean_absolute_error(y_test, y_pred_mlr)
    r2_mlr = r2_score(y_test, y_pred_mlr)

    regression_results.append({
        'Model': 'Multiple Linear Regression (All Features)',
        'MSE': round(mse_mlr, 2),
        'RMSE': round(rmse_mlr, 2),
        'MAE': round(mae_mlr, 2),
        'R2_Score': round(r2_mlr, 4)
    })
    joblib.dump(mlr_model, 'models/multiple_linear_regression.joblib')

    # 3. Polynomial Regression (Degree 2)
    poly_features = [dist_col, 'Avg VTAT', 'Avg CTAT', 'is_weekend']
    avail_poly_feats = [c for c in poly_features if c in X_train.columns]
    
    poly = PolynomialFeatures(degree=2, include_bias=False)
    X_train_poly = poly.fit_transform(X_train[avail_poly_feats])
    X_test_poly = poly.transform(X_test[avail_poly_feats])

    poly_model = Ridge(alpha=100.0)
    poly_model.fit(X_train_poly, y_train)
    y_pred_poly = poly_model.predict(X_test_poly)

    mse_poly = mean_squared_error(y_test, y_pred_poly)
    rmse_poly = np.sqrt(mse_poly)
    mae_poly = mean_absolute_error(y_test, y_pred_poly)
    r2_poly = r2_score(y_test, y_pred_poly)

    regression_results.append({
        'Model': 'Polynomial Regression (Degree 2 Interaction)',
        'MSE': round(mse_poly, 2),
        'RMSE': round(rmse_poly, 2),
        'MAE': round(mae_poly, 2),
        'R2_Score': round(r2_poly, 4)
    })
    joblib.dump(poly_model, 'models/polynomial_regression_deg2.joblib')
    joblib.dump(poly, 'models/poly_features_deg2.joblib')

    # 4. Random Forest Regressor (Non-linear Ensemble)
    rf_model = RandomForestRegressor(n_estimators=60, max_depth=10, random_state=42, n_jobs=-1)
    rf_model.fit(X_train, y_train)
    y_pred_rf = rf_model.predict(X_test)

    mse_rf = mean_squared_error(y_test, y_pred_rf)
    rmse_rf = np.sqrt(mse_rf)
    mae_rf = mean_absolute_error(y_test, y_pred_rf)
    r2_rf = r2_score(y_test, y_pred_rf)

    regression_results.append({
        'Model': 'Random Forest Regressor',
        'MSE': round(mse_rf, 2),
        'RMSE': round(rmse_rf, 2),
        'MAE': round(mae_rf, 2),
        'R2_Score': round(r2_rf, 4)
    })
    joblib.dump(rf_model, 'models/random_forest_regressor.joblib')

    # Display comparison table
    results_df = pd.DataFrame(regression_results)
    print("\nRegression Performance Metric Summary:")
    print(results_df.to_string(index=False))

    # Visualization of Regressions
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    fig.suptitle('Regression Performance & Residual Diagnostics', fontsize=14, fontweight='bold')
    
    # Plot 1: Simple Linear Regression fit line
    sample_vis_idx = np.random.choice(len(X_test), size=min(500, len(X_test)), replace=False)
    X_test_sub = X_test.iloc[sample_vis_idx]
    y_test_sub = y_test.iloc[sample_vis_idx]
    
    sns.scatterplot(x=X_test_sub[dist_col], y=y_test_sub, alpha=0.5, color='gray', ax=axes[0], label='Actual Test Fare')
    sorted_order = np.argsort(X_test_sub[dist_col])
    sub_pred_slr = slr_model.predict(X_test_sub[[dist_col]])
    axes[0].plot(X_test_sub[dist_col].iloc[sorted_order], sub_pred_slr[sorted_order], color='crimson', lw=2.5, label='SLR Fit Line')
    axes[0].set_title(f'Simple Linear Regression (R²={r2_slr:.4f})')
    axes[0].set_xlabel('Ride Distance (km)')
    axes[0].set_ylabel('Fare (₹)')
    axes[0].legend()
    
    # Plot 2: Actual vs Predicted (Multiple Linear Regression)
    axes[1].scatter(y_test.iloc[sample_vis_idx], y_pred_mlr[sample_vis_idx], alpha=0.5, color='teal')
    min_val, max_val = y_test.quantile(0.01), y_test.quantile(0.99)
    axes[1].plot([min_val, max_val], [min_val, max_val], 'r--', lw=2)
    axes[1].set_title(f'Actual vs Predicted MLR (R²={r2_mlr:.4f})')
    axes[1].set_xlabel('Actual Fare (₹)')
    axes[1].set_ylabel('Predicted Fare (₹)')
    
    # Plot 3: Residuals Distribution (Polynomial Regression)
    residuals_poly = y_test - y_pred_poly
    sns.histplot(residuals_poly, kde=True, color='purple', ax=axes[2], bins=40)
    axes[2].axvline(0, color='red', linestyle='--')
    axes[2].set_title('Residuals Error Distribution')
    axes[2].set_xlabel('Residual (Actual - Predicted Fare ₹)')
    
    plt.tight_layout()
    reg_plot_path = os.path.join('plots', 'regression_diagnostics.png')
    plt.savefig(reg_plot_path, dpi=200)
    plt.close()
    print(f" -> Saved: {reg_plot_path}")
    
    return results_df

if __name__ == '__main__':
    data_path = 'ncr_ride_bookings.csv'
    if not os.path.exists(data_path):
        data_path = 'cab_rides_dataset.csv'
    raw_df = pd.read_csv(data_path)
    df_clean, df_encoded = run_preprocessing_pipeline(raw_df)
    run_regression_models(df_encoded)
