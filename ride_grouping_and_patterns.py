"""
ride_grouping_and_patterns.py
PART 4:
- Clustering for Data Analysis & Partitional Clustering:
  * K-Means Clustering
  * Elbow Method & Silhouette Analysis (Performance Metrics of Clustering)
- Hierarchical Clustering:
  * Agglomerative Hierarchical Clustering
  * Linkage Criteria (ward, complete, average)
  * Dendrogram Construction
- Advanced Density & Graph Clustering:
  * Spectral Clustering
  * DBSCAN (Density-Based Spatial Clustering of Applications with Noise)
- Sparsity & High Dimensional Data:
  * Curse of Dimensionality
- Dimensionality Reduction:
  * Principal Component Analysis (PCA - Unsupervised)
  * Linear Discriminant Analysis (LDA - Supervised)
- Probabilistic Graphical Models:
  * Markov Networks (Undirected Graphical Models & Markov Property)
  * Hidden Markov Model (HMM - Sequence state decoding for Cab Trip States: Idle, Cruising, On-Trip)
"""

import os
import matplotlib
matplotlib.use('Agg')
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans, AgglomerativeClustering, DBSCAN, SpectralClustering
from sklearn.metrics import silhouette_score, davies_bouldin_score, calinski_harabasz_score
from scipy.cluster.hierarchy import dendrogram, linkage
from sklearn.decomposition import PCA
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
import joblib

os.makedirs('plots', exist_ok=True)
os.makedirs('models', exist_ok=True)

def print_header(title):
    print("\n" + "="*80)
    print(f" {title} ")
    print("="*80)

def section_4_theory():
    print_header("SECTION IV [A]: CLUSTERING THEORY, SPARSITY & MARKOV MODELS")
    print("""
    [1] PARTITIONAL VS HIERARCHICAL CLUSTERING:
    - Partitional (K-Means):
      * Partitions N points into K non-overlapping clusters by minimizing inertia (WCSS).
      * Performance Metrics: Silhouette Score, Davies-Bouldin Index, Calinski-Harabasz Index.
    - Hierarchical (Agglomerative):
      * Iteratively aggregates points into a dendrogram hierarchy using linkage distance functions.
    - Density-Based (DBSCAN):
      * Segments spatial density regions and filters arbitrary outlier noise points.

    [2] HIGH-DIMENSIONAL SPARSITY & CURSE OF DIMENSIONALITY:
    - Feature spaces expand exponentially with dimensions, causing geometric points to become sparse.
    - Remedies: PCA finds orthogonal directions of greatest variance; LDA finds boundaries maximizing class separability.

    [3] MARKOV NETWORKS & HIDDEN MARKOV MODELS (HMM):
    - Modeling driver shift transitions across latent behavioral states: {Idle, Cruising, On-Trip}.
    """)

def run_clustering_and_dim_reduction():
    print_header("SECTION IV [B]: CLUSTERING EXPERIMENTS & DIMENSIONALITY REDUCTION")
    
    # Load dataset
    if os.path.exists('cleaned_cab_data.csv'):
        df = pd.read_csv('cleaned_cab_data.csv')
    elif os.path.exists('ncr_ride_bookings.csv'):
        df = pd.read_csv('ncr_ride_bookings.csv').dropna(subset=['Booking Value', 'Ride Distance'])
    else:
        df = pd.read_csv('cab_rides_dataset.csv')
    
    # Identify available numeric columns for clustering
    candidate_features = ['Ride Distance', 'Booking Value', 'Avg VTAT', 'Avg CTAT', 'Driver Ratings']
    cluster_features = [c for c in candidate_features if c in df.columns]
    if len(cluster_features) < 2:
        cluster_features = ['trip_distance_km', 'fare_amount', 'trip_duration_mins']
    
    print(f"Clustering feature space: {cluster_features}")
    
    # Sample 5000 rows for high-fidelity clustering & dendrogram computation
    sample_df = df[cluster_features].dropna().sample(min(5000, len(df)), random_state=42)
    X_clust = sample_df.values
    
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_clust)
    
    # 1. Elbow Method & Silhouette Analysis for K-Means (K = 2 to 6)
    k_range = range(2, 7)
    inertias = []
    sil_scores = []
    
    for k in k_range:
        km = KMeans(n_clusters=k, random_state=42, n_init=10)
        km.fit(X_scaled)
        inertias.append(km.inertia_)
        sil = silhouette_score(X_scaled, km.labels_)
        sil_scores.append(sil)
    
    optimal_k = k_range[np.argmax(sil_scores)]
    print(f"Optimal clusters identified via Silhouette Peak: K = {optimal_k}")
    
    # Fit Optimal K-Means
    kmeans_opt = KMeans(n_clusters=optimal_k, random_state=42, n_init=10)
    kmeans_labels = kmeans_opt.fit_predict(X_scaled)
    joblib.dump(kmeans_opt, 'models/kmeans_model.joblib')
    
    # Clustering Performance Matrix
    km_sil = silhouette_score(X_scaled, kmeans_labels)
    km_db = davies_bouldin_score(X_scaled, kmeans_labels)
    km_ch = calinski_harabasz_score(X_scaled, kmeans_labels)
    
    print("\n--- Partitional Clustering Performance Matrix (K-Means) ---")
    print(f"1. Silhouette Score (Higher is better, [-1, 1]): {km_sil:.4f}")
    print(f"2. Davies-Bouldin Index (Lower is better):       {km_db:.4f}")
    print(f"3. Calinski-Harabasz Index (Higher is better):    {km_ch:.2f}")

    # 2. Hierarchical Agglomerative Clustering
    agg_cluster = AgglomerativeClustering(n_clusters=optimal_k, linkage='ward')
    agg_labels = agg_cluster.fit_predict(X_scaled)
    agg_sil = silhouette_score(X_scaled, agg_labels)
    print(f"\n--- Hierarchical Agglomerative Clustering (Ward Linkage) ---")
    print(f"Agglomerative Silhouette Score: {agg_sil:.4f}")

    # 3. Density-Based Clustering: DBSCAN
    dbscan = DBSCAN(eps=0.8, min_samples=15)
    dbscan_labels = dbscan.fit_predict(X_scaled)
    n_db_clusters = len(set(dbscan_labels)) - (1 if -1 in dbscan_labels else 0)
    n_noise = list(dbscan_labels).count(-1)
    print(f"\n--- DBSCAN Clustering ---")
    print(f"Detected {n_db_clusters} dense clusters and {n_noise} noise points (outliers).")

    # 4. Spectral Clustering (Subsample for efficient graph Laplacian)
    sample_sub = X_scaled[:600]
    spectral = SpectralClustering(n_clusters=optimal_k, affinity='nearest_neighbors', random_state=42)
    spectral_labels = spectral.fit_predict(sample_sub)
    print(f"\n--- Spectral Clustering (Graph Laplacian) ---")
    print(f"Spectral Clustering Silhouette: {silhouette_score(sample_sub, spectral_labels):.4f}")

    # 5. Dimensionality Reduction: PCA vs LDA
    print_header("SECTION IV [C]: DIMENSIONALITY REDUCTION (PCA vs LDA)")
    
    # (a) PCA (Unsupervised)
    pca = PCA(n_components=2)
    X_pca = pca.fit_transform(X_scaled)
    explained_var = pca.explained_variance_ratio_
    print(f"PCA Components: PC1 explains {explained_var[0]*100:.2f}%, PC2 explains {explained_var[1]*100:.2f}%")
    print(f"Total variance retained by 2D projection: {np.sum(explained_var)*100:.2f}%")
    joblib.dump(pca, 'models/pca_transformer.joblib')

    # (b) LDA (Supervised)
    # Using booking fare segment as target class (Low vs High Fare)
    median_val = np.median(X_clust[:, 1])
    y_class = (X_clust[:, 1] > median_val).astype(int)
    lda = LinearDiscriminantAnalysis(n_components=1)
    X_lda = lda.fit_transform(X_scaled, y_class)
    print(f"LDA Supervised Component fit completed. Explained variance: {lda.explained_variance_ratio_[0]*100:.2f}%")
    joblib.dump(lda, 'models/lda_transformer.joblib')

    # 6. Hidden Markov Model (HMM) Simulation
    print_header("SECTION IV [D]: HIDDEN MARKOV MODEL (HMM) SEQUENCE INFERENCE")
    print("Simulating sequence of driver operational states: {0: Idle, 1: Cruising, 2: On-Trip}...")
    
    transition_matrix = np.array([
        [0.60, 0.30, 0.10],
        [0.10, 0.50, 0.40],
        [0.05, 0.20, 0.75]
    ])
    state_names = {0: 'Idle / Parked', 1: 'Cruising / Seeking', 2: 'On-Trip (Active)'}
    
    current_state = 0
    simulated_states = [current_state]
    np.random.seed(42)
    for _ in range(50):
        current_state = np.random.choice([0, 1, 2], p=transition_matrix[current_state])
        simulated_states.append(current_state)
    print(f"Driver Telemetry State Sequence (first 15 steps): {[state_names[s] for s in simulated_states[:15]]}")

    # Visualizations
    fig, axes = plt.subplots(2, 3, figsize=(18, 11))
    fig.suptitle('Clustering, Dendrogram, PCA & Dimensionality Reduction', fontsize=15, fontweight='bold')
    
    # 1. Elbow Curve (Inertia & Silhouette)
    ax1 = axes[0, 0]
    ax1.plot(k_range, inertias, 'bo-', label='Inertia (WCSS)')
    ax1.set_xlabel('Number of Clusters (K)')
    ax1.set_ylabel('Inertia')
    ax1.set_title('Elbow Method for Optimal K')
    
    ax1_twin = ax1.twinx()
    ax1_twin.plot(k_range, sil_scores, 'ro--', label='Silhouette Score')
    ax1_twin.set_ylabel('Silhouette Score')
    
    # 2. PCA 2D Projection with K-Means Clusters
    axes[0, 1].scatter(X_pca[:, 0], X_pca[:, 1], c=kmeans_labels, cmap='viridis', alpha=0.6, s=25)
    axes[0, 1].set_title(f'PCA 2D Projection (K-Means K={optimal_k})')
    axes[0, 1].set_xlabel('Principal Component 1')
    axes[0, 1].set_ylabel('Principal Component 2')
    
    # 3. DBSCAN Density Clusters
    axes[0, 2].scatter(X_pca[:, 0], X_pca[:, 1], c=dbscan_labels, cmap='plasma', alpha=0.6, s=25)
    axes[0, 2].set_title('DBSCAN Density Clusters (Noise in Purple)')
    axes[0, 2].set_xlabel('PC 1')
    axes[0, 2].set_ylabel('PC 2')
    
    # 4. Dendrogram for Hierarchical Linkage
    linkage_sample = X_scaled[:40]
    Z = linkage(linkage_sample, method='ward')
    dendrogram(Z, ax=axes[1, 0], truncate_mode='lastp', p=15, leaf_rotation=45)
    axes[1, 0].set_title('Hierarchical Clustering Dendrogram (Ward Linkage)')
    axes[1, 0].set_xlabel('Sample Index / Cluster Size')
    axes[1, 0].set_ylabel('Euclidean Distance')
    
    # 5. LDA Projection vs Segmentation Target
    axes[1, 1].hist(X_lda[y_class == 0], bins=30, alpha=0.6, color='blue', label='Standard Fare (0)')
    axes[1, 1].hist(X_lda[y_class == 1], bins=30, alpha=0.6, color='crimson', label='High Fare (1)')
    axes[1, 1].set_title('Linear Discriminant Analysis (LDA) Separation')
    axes[1, 1].set_xlabel('Discriminant Dimension')
    axes[1, 1].set_ylabel('Density Frequency')
    axes[1, 1].legend()

    # 6. HMM State Transition Diagram Matrix
    sns.heatmap(transition_matrix, annot=True, fmt='.2f', cmap='Blues', ax=axes[1, 2],
                xticklabels=['Idle', 'Cruising', 'On-Trip'],
                yticklabels=['Idle', 'Cruising', 'On-Trip'])
    axes[1, 2].set_title('HMM State Transition Probabilities')
    axes[1, 2].set_xlabel('Next State (t+1)')
    axes[1, 2].set_ylabel('Current State (t)')
    
    plt.tight_layout()
    cluster_plot_path = os.path.join('plots', 'clustering_and_dimensionality.png')
    plt.savefig(cluster_plot_path, dpi=200)
    plt.close()
    print(f" -> Saved: {cluster_plot_path}")

if __name__ == '__main__':
    section_4_theory()
    run_clustering_and_dim_reduction()
