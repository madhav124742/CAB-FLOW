"""
main.py
Cab Prediction System - Master Pipeline Orchestrator
Executes data loading, statistical analysis, preprocessing, model training,
and visualization routines for the Cab Prediction System.
"""

import sys
import time
import os
import pandas as pd

import data_analysis_and_exploration
import data_cleaning_and_price_prediction
import ride_cancellation_prediction
import ride_grouping_and_patterns

def banner():
    print("""
    ========================================================================
    |                                                                      |
    |                 CAB PREDICTION SYSTEM PIPELINE                       |
    |       Real Dataset Preprocessing, ML Training & Analytics            |
    |                                                                      |
    ========================================================================
    """)

def main():
    start_time = time.time()
    banner()
    
    # Prioritize user's own real-world dataset
    if os.path.exists('ncr_ride_bookings.csv'):
        csv_path = 'ncr_ride_bookings.csv'
        print(f"[Dataset] Using user dataset: '{csv_path}'")
        df = pd.read_csv(csv_path)
    elif os.path.exists('cab_rides_dataset.csv'):
        csv_path = 'cab_rides_dataset.csv'
        print(f"[Dataset] Using dataset: '{csv_path}'")
        df = pd.read_csv(csv_path)
    else:
        print("[Dataset] Generating synthetic fallback dataset...")
        import generate_dataset
        df = generate_dataset.generate_cab_dataset(n_samples=2500)
        df.to_csv('cab_rides_dataset.csv', index=False)

    print(f"Loaded dataset with shape {df.shape} and columns:\n{list(df.columns)}\n")

    print(">>> 1. Processing Data Foundations & EDA...")
    data_analysis_and_exploration.section_1_statistical_measures(df)
    data_analysis_and_exploration.section_1_exploratory_data_analysis(df)
    
    print("\n>>> 2. Executing Pre-Processing & Fare Regression...")
    df_clean, df_encoded = data_cleaning_and_price_prediction.run_preprocessing_pipeline(df)
    data_cleaning_and_price_prediction.run_regression_models(df_encoded)
    
    print("\n>>> 3. Training Ride Cancellation Risk Classifiers...")
    ride_cancellation_prediction.run_classification_pipeline()
    
    print("\n>>> 4. Running Spatial Clustering & Dimensionality Analysis...")
    ride_grouping_and_patterns.run_clustering_and_dim_reduction()
    
    elapsed = time.time() - start_time
    print(f"\n========================================================================")
    print(f" [SUCCESS] Cab Prediction System pipeline completed in {elapsed:.2f}s!")
    print(f" Visualizations saved to: ./plots/")
    print(f" Trained models saved to: ./models/")
    print(f"========================================================================\n")

if __name__ == '__main__':
    main()
