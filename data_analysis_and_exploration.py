"""
data_analysis_and_exploration.py
PART 1:
- Statistical Machine Learning Concepts & Types of Learning (Supervised, Unsupervised, Reinforcement)
- Applications of ML in Cab Prediction
- Understanding Data: Quantitative vs Qualitative, Structured vs Semi-structured vs Unstructured
- Sources of Data, Feature Variables
- Statistical Theory & Measures: Mean, Median, Mode, Std Dev, Range, Variance
- Exploratory Data Analysis (EDA) using Matplotlib and Seaborn
"""

import os
import matplotlib
matplotlib.use('Agg')  # non-interactive headless backend
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

# Ensure plots directory exists
os.makedirs('plots', exist_ok=True)
sns.set_theme(style="whitegrid", palette="muted")
plt.rcParams.update({'font.sans-serif': 'DejaVu Sans', 'font.size': 10})

def display_section_header(title):
    print("\n" + "="*80)
    print(f" {title} ")
    print("="*80)

def section_1_theory_and_concepts():
    display_section_header("1. STATISTICAL MACHINE LEARNING THEORY & LEARNING PARADIGMS")
    print("""
    [A] TYPES OF LEARNING:
    1. Supervised Learning:
       - Learning a predictive mapping f: X -> Y from labeled ground-truth observations.
       - Cab System Example:
         * Regression: Predicting cab Booking Value / Fare (₹) from distance, timing, and vehicle class.
         * Classification: Predicting booking cancellation risk (Cancelled vs Completed).
    2. Unsupervised Learning:
       - Discovering inherent latent structures, clusters, or patterns in unlabeled feature spaces {X}.
       - Cab System Example:
         * Clustering: Segmenting trip characteristics (e.g., short-hop vs commuter vs airport trips).
         * Dimensionality Reduction: PCA / LDA compressing multi-dimensional ride metrics into orthogonal components.
    3. Reinforcement Learning (RL):
       - Agent interacts with a dynamic ride-hailing environment, learning policies pi(s) -> a to maximize long-term rewards.
       - Cab System Example:
         * Dynamic fleet rebalancing, localized surge pricing adjustments, and optimal driver dispatching.

    [B] UNDERSTANDING DATA TAXONOMIES:
    1. Quantitative Data (Numerical):
       - Continuous: Ride Distance (km), Booking Value (₹), Avg VTAT (mins), Avg CTAT (mins).
       - Discrete: Driver Ratings, Customer Ratings (3.0 - 5.0 stars).
    2. Qualitative Data (Categorical):
       - Nominal: Vehicle Type ('Auto', 'Go Mini', 'Premier Sedan', 'Uber XL', 'Bike'), Payment Method ('UPI', 'Cash', 'Uber Wallet').
       - Ordinal: Ratings scale, Day of Week sequence.
    3. Data Structures:
       - Structured Data: Tabular ride transaction logs (ncr_ride_bookings.csv).
       - Semi-Structured Data: Real-time JSON telemetry packets and API payloads.
       - Unstructured Data: Customer feedback reviews, driver-passenger chat transcripts.
    4. Sources of Data in Cab Systems:
       - In-vehicle telematics & smartphone GPS sensors.
       - Mobile booking application event streams.
       - Traffic speed feeds, weather radar integrations, and payment gateways.
    """)

def section_1_statistical_measures(df):
    display_section_header("2. STATISTICAL THEORY & DESCRIPTIVE MEASURES")
    
    # Identify available numeric columns
    candidate_cols = ['Booking Value', 'Ride Distance', 'Avg VTAT', 'Avg CTAT', 'Driver Ratings', 'Customer Rating']
    numerical_cols = [c for c in candidate_cols if c in df.columns]
    
    stats_dict = []
    for col in numerical_cols:
        clean_series = pd.to_numeric(df[col], errors='coerce').dropna()
        if len(clean_series) == 0:
            continue
        n = len(clean_series)
        mean_val = np.mean(clean_series)
        median_val = np.median(clean_series)
        mode_res = stats.mode(np.round(clean_series, 1), keepdims=True)
        mode_val = mode_res.mode[0] if len(mode_res.mode) > 0 else np.nan
        var_val = np.var(clean_series, ddof=1)
        std_val = np.std(clean_series, ddof=1)
        range_val = np.ptp(clean_series)
        skew_val = stats.skew(clean_series)
        kurt_val = stats.kurtosis(clean_series)
        
        stats_dict.append({
            'Feature': col,
            'Count': n,
            'Mean': round(mean_val, 2),
            'Median': round(median_val, 2),
            'Mode': round(mode_val, 2),
            'Variance': round(var_val, 2),
            'Std_Dev': round(std_val, 2),
            'Range': round(range_val, 2),
            'Skewness': round(skew_val, 2),
            'Kurtosis': round(kurt_val, 2)
        })
    
    stats_summary_df = pd.DataFrame(stats_dict)
    print(stats_summary_df.to_string(index=False))
    return stats_summary_df

def section_1_exploratory_data_analysis(df):
    display_section_header("3. EXPLORATORY DATA ANALYSIS (EDA) & VISUALIZATION")
    print("Generating comprehensive statistical plots using Matplotlib and Seaborn...")

    # Filter completed or rides with valid distance & fare for price analysis
    valid_rides = df.dropna(subset=['Booking Value', 'Ride Distance']).copy()
    if len(valid_rides) > 25000:
        plot_sample = valid_rides.sample(n=25000, random_state=42)
    else:
        plot_sample = valid_rides

    # Figure 1: Univariate Distributions & Frequency
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('EDA 1: Univariate Feature Distributions & Operational Frequencies', fontsize=15, fontweight='bold')
    
    # Ride Distance
    sns.histplot(plot_sample['Ride Distance'].dropna(), kde=True, ax=axes[0, 0], color='royalblue', bins=30)
    axes[0, 0].set_title('Ride Distance Distribution (km)')
    axes[0, 0].set_xlabel('Distance (km)')

    # Booking Value (Fare)
    sns.histplot(plot_sample['Booking Value'].dropna(), kde=True, ax=axes[0, 1], color='forestgreen', bins=35)
    axes[0, 1].set_title('Booking Value / Fare Distribution (₹)')
    axes[0, 1].set_xlabel('Fare (₹)')

    # Booking Status Breakdown across full dataset
    status_counts = df['Booking Status'].value_counts()
    axes[1, 0].pie(status_counts, labels=status_counts.index, autopct='%1.1f%%',
                   colors=['#10B981', '#EF4444', '#F59E0B', '#3B82F6', '#8B5CF6'], startangle=140)
    axes[1, 0].set_title('Ride Booking Status Proportions')

    # Vehicle Category Booking Volume
    sns.countplot(data=df, x='Vehicle Type', ax=axes[1, 1], palette='Set2',
                  order=df['Vehicle Type'].value_counts().index)
    axes[1, 1].set_title('Bookings by Vehicle Category')
    axes[1, 1].tick_params(axis='x', rotation=30)
    
    plt.tight_layout()
    plot1_path = os.path.join('plots', 'eda_1_distributions.png')
    plt.savefig(plot1_path, dpi=200)
    plt.close()
    print(f" -> Saved: {plot1_path}")

    # Figure 2: Multivariate Relationships & Fare Patterns
    fig, axes = plt.subplots(2, 2, figsize=(15, 11))
    fig.suptitle('EDA 2: Multivariate Relationships & Booking Value Drivers', fontsize=15, fontweight='bold')

    # Distance vs Fare Scatter
    sns.scatterplot(data=plot_sample.sample(min(3000, len(plot_sample)), random_state=42),
                    x='Ride Distance', y='Booking Value', hue='Vehicle Type', alpha=0.6, ax=axes[0, 0])
    axes[0, 0].set_title('Booking Value vs Ride Distance by Vehicle Type')
    axes[0, 0].set_ylabel('Booking Value (₹)')
    axes[0, 0].legend(loc='upper right', fontsize=8)

    # Boxplot of Fare across Vehicle Types
    sns.boxplot(data=plot_sample, x='Vehicle Type', y='Booking Value', ax=axes[0, 1], palette='Set3',
                order=df['Vehicle Type'].value_counts().index)
    axes[0, 1].set_title('Booking Value Distribution Across Vehicle Types')
    axes[0, 1].set_ylabel('Booking Value (₹)')
    axes[0, 1].tick_params(axis='x', rotation=30)

    # Booking Value across Payment Methods
    if 'Payment Method' in plot_sample.columns:
        valid_pm = plot_sample.dropna(subset=['Payment Method'])
        sns.barplot(data=valid_pm, x='Payment Method', y='Booking Value', ax=axes[1, 0], palette='Blues_d')
        axes[1, 0].set_title('Average Booking Value by Payment Method')
        axes[1, 0].tick_params(axis='x', rotation=20)
    else:
        axes[1, 0].text(0.5, 0.5, 'Payment Method Data Not Available', ha='center', va='center')

    # Correlation Matrix Heatmap
    num_cols = ['Booking Value', 'Ride Distance', 'Avg VTAT', 'Avg CTAT', 'Driver Ratings', 'Customer Rating']
    avail_num_cols = [c for c in num_cols if c in plot_sample.columns]
    corr = plot_sample[avail_num_cols].corr()
    sns.heatmap(corr, annot=True, fmt=".3f", cmap='coolwarm', ax=axes[1, 1], cbar=True, square=True)
    axes[1, 1].set_title('Correlation Heatmap of Numerical Features')

    plt.tight_layout()
    plot2_path = os.path.join('plots', 'eda_2_multivariate.png')
    plt.savefig(plot2_path, dpi=200)
    plt.close()
    print(f" -> Saved: {plot2_path}")

    print("EDA Visualizations generated successfully.")

if __name__ == '__main__':
    data_path = 'ncr_ride_bookings.csv'
    if not os.path.exists(data_path):
        data_path = 'cab_rides_dataset.csv'
    df = pd.read_csv(data_path)
    section_1_theory_and_concepts()
    section_1_statistical_measures(df)
    section_1_exploratory_data_analysis(df)
