"""
generate_dataset.py
Generates a realistic, highly predictive synthetic cab booking and trip dataset
incorporating diverse data types, outliers, missing values,
and distinct temporal/spatial signals for high accuracy statistical machine learning.
"""

import numpy as np
import pandas as pd
import random
from datetime import datetime, timedelta

def generate_cab_dataset(n_samples=4000, random_state=42):
    np.random.seed(random_state)
    random.seed(random_state)
    
    # 1. Cab & Ride Providers (Categorical)
    cab_types = ['UberGo', 'UberX', 'UberXL', 'OlaMini', 'OlaPrime', 'OlaSedan']
    payment_types = ['UPI', 'CreditCard', 'DebitCard', 'Cash', 'Wallet']
    weather_conditions = ['Clear', 'Rainy', 'Cloudy', 'Foggy']
    traffic_conditions = ['Low', 'Medium', 'High', 'Congested']
    pickup_locations = ['Airport', 'Downtown', 'Suburbs', 'TrainStation', 'TechPark', 'University']
    
    # Generate base temporal timestamps
    base_time = datetime(2026, 5, 1, 6, 0, 0)
    timestamps = [base_time + timedelta(minutes=random.randint(0, 43200)) for _ in range(n_samples)]
    
    cabs = np.random.choice(cab_types, size=n_samples, p=[0.25, 0.20, 0.15, 0.20, 0.10, 0.10])
    payments = np.random.choice(payment_types, size=n_samples, p=[0.35, 0.25, 0.15, 0.15, 0.10])
    weathers = np.random.choice(weather_conditions, size=n_samples, p=[0.55, 0.15, 0.20, 0.10])
    traffics = np.random.choice(traffic_conditions, size=n_samples, p=[0.25, 0.40, 0.25, 0.10])
    pickups = np.random.choice(pickup_locations, size=n_samples)
    
    # Numerical features
    trip_distance_km = np.random.exponential(scale=7.5, size=n_samples) + 1.2
    passenger_count = np.random.choice([1, 2, 3, 4, 5, 6], size=n_samples, p=[0.55, 0.20, 0.10, 0.08, 0.04, 0.03])
    driver_rating = np.clip(np.random.normal(loc=4.5, scale=0.35, size=n_samples), 2.5, 5.0)
    customer_rating = np.clip(np.random.normal(loc=4.6, scale=0.30, size=n_samples), 2.5, 5.0)
    
    # Driver wait time in minutes before passenger pickup
    estimated_wait_time = np.random.gamma(shape=2.5, scale=2.8, size=n_samples) + 1.0 # 2 to 20 mins
    
    traffic_multipliers = {'Low': 1.0, 'Medium': 1.25, 'High': 1.60, 'Congested': 2.10}
    weather_multipliers = {'Clear': 1.0, 'Cloudy': 1.08, 'Rainy': 1.35, 'Foggy': 1.20}
    cab_rates = {'UberGo': 12, 'UberX': 15, 'UberXL': 22, 'OlaMini': 11, 'OlaPrime': 16, 'OlaSedan': 18}
    cab_base_fees = {'UberGo': 40, 'UberX': 55, 'UberXL': 85, 'OlaMini': 35, 'OlaPrime': 60, 'OlaSedan': 65}
    
    trip_duration_mins = []
    fare_amounts = []
    surge_multipliers = []
    cancellation_status = [] # 0: Completed, 1: Cancelled
    
    for i in range(n_samples):
        d = trip_distance_km[i]
        c = cabs[i]
        w = weathers[i]
        t = traffics[i]
        p = pickups[i]
        wait = estimated_wait_time[i]
        dr_rate = driver_rating[i]
        
        # Duration calculation based on traffic speed
        speed_kmh = 36.0
        if t == 'Medium': speed_kmh = 24.0
        elif t == 'High': speed_kmh = 16.0
        elif t == 'Congested': speed_kmh = 10.0
        
        duration = (d / speed_kmh) * 60 + np.random.normal(2, 0.8)
        trip_duration_mins.append(max(4.0, round(duration, 2)))
        
        surge = traffic_multipliers[t] * weather_multipliers[w]
        surge_multipliers.append(round(surge, 2))
        
        base_fee = cab_base_fees[c]
        rate_per_km = cab_rates[c]
        time_rate = 1.6
        
        # Deterministic physical pricing equation with realistic operational variance
        fare = (base_fee + (d * rate_per_km) + (duration * time_rate)) * surge
        fare += np.random.normal(0, 3.5)
        fare_amounts.append(round(max(45.0, fare), 2))
        
        # Mathematically solid cancellation model:
        # Drivers and riders cancel primarily when wait times are excessively high, 
        # surge is extreme, driver rating is poor, or traffic is heavily congested.
        logit = (
            -4.50 
            + (0.32 * wait) 
            + (1.25 * (surge - 1.0)) 
            - (0.85 * (dr_rate - 3.5)) 
            + (0.65 if t == 'Congested' else 0.0) 
            + (0.45 if w == 'Rainy' else 0.0)
        )
        # Sigmoid probability
        cancel_prob = 1.0 / (1.0 + np.exp(-logit))
        cancellation_status.append(1 if random.random() < cancel_prob else 0)

    pickup_hours = [t.hour for t in timestamps]
    day_of_week = [t.strftime('%A') for t in timestamps]

    df = pd.DataFrame({
        'trip_id': [f"TRIP_{100000+i}" for i in range(n_samples)],
        'timestamp': timestamps,
        'pickup_hour': pickup_hours,
        'day_of_week': day_of_week,
        'pickup_location': pickups,
        'cab_type': cabs,
        'trip_distance_km': np.round(trip_distance_km, 2),
        'passenger_count': passenger_count,
        'driver_wait_time_mins': np.round(estimated_wait_time, 2),
        'traffic_condition': traffics,
        'weather': weathers,
        'driver_rating': np.round(driver_rating, 2),
        'customer_rating': np.round(customer_rating, 2),
        'trip_duration_mins': trip_duration_mins,
        'surge_multiplier': surge_multipliers,
        'payment_type': payments,
        'fare_amount': fare_amounts,
        'trip_cancelled': cancellation_status
    })

    # Add controlled missing values to teach/demonstrate imputation
    missing_indices = np.random.choice(n_samples, size=int(n_samples * 0.025), replace=False)
    df.loc[missing_indices, 'driver_rating'] = np.nan
    
    missing_durations = np.random.choice(n_samples, size=int(n_samples * 0.015), replace=False)
    df.loc[missing_durations, 'trip_duration_mins'] = np.nan

    # Add duplicate rows to demonstrate deduplication
    dup_rows = df.iloc[np.random.choice(n_samples, 25)].copy()
    df = pd.concat([df, dup_rows], ignore_index=True)

    # Controlled outliers to demonstrate IQR / Z-Score clipping
    outlier_idx = np.random.choice(len(df), size=6, replace=False)
    df.loc[outlier_idx, 'fare_amount'] = df.loc[outlier_idx, 'fare_amount'] * 4.5

    return df

if __name__ == '__main__':
    df = generate_cab_dataset(n_samples=4000)
    df.to_csv('cab_rides_dataset.csv', index=False)
    print(f"Generated realistic dataset with shape: {df.shape}")
