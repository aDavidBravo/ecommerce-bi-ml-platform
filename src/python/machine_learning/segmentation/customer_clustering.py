"""
Customer Segmentation Module
Implementa clustering avanzado: K-Means, DBSCAN, Hierarchical, Gaussian Mixture, Autoencoders
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
import warnings
warnings.filterwarnings('ignore')

# Clustering algorithms
from sklearn.cluster import KMeans, DBSCAN, AgglomerativeClustering, OPTICS
from sklearn.mixture import GaussianMixture
from sklearn.preprocessing import StandardScaler, RobustScaler
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
import umap

# Metrics
from sklearn.metrics import silhouette_score, davies_bould in_score, calinski_harabasz_score

# Deep Learning
import tensorflow as tf
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, Dense, Dropout
from tensorflow.keras.optimizers import Adam

import torch
import torch.nn as nn
import torch.optim as optim

# Visualization
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go

# MLflow
import mlflow
import mlflow.sklearn

class CustomerSegmentation:
    """
    Sistema completo de segmentación de clientes con múltiples algoritmos
    """
    
    def __init__(self, data: pd.DataFrame):
        """
        Args:
            data: DataFrame con features de clientes
        """
        self.data = data.copy()
        self.scaled_data = None
        self.models = {}
        self.labels = {}
        self.metrics = {}
        self.scaler = None
        
    def preprocess_data(self, method: str = 'standard') -> np.ndarray:
        """
        Preprocesa y escala los datos
        
        Args:
            method: 'standard', 'robust', 'minmax'
        """
        numeric_cols = self.data.select_dtypes(include=[np.number]).columns
        
        if method == 'standard':
            self.scaler = StandardScaler()
        elif method == 'robust':
            self.scaler = RobustScaler()
        else:
            from sklearn.preprocessing import MinMaxScaler
            self.scaler = MinMaxScaler()
        
        self.scaled_data = self.scaler.fit_transform(self.data[numeric_cols])
        
        return self.scaled_data
    
    # ========================================
    # RFM ANALYSIS
    # ========================================
    
    def calculate_rfm(self, customer_id_col: str, date_col: str, 
                     amount_col: str, reference_date: Optional[pd.Timestamp] = None):
        """
        Calcula métricas RFM (Recency, Frequency, Monetary)
        """
        if reference_date is None:
            reference_date = self.data[date_col].max()
        
        rfm = self.data.groupby(customer_id_col).agg({
            date_col: lambda x: (reference_date - x.max()).days,  # Recency
            customer_id_col: 'count',  # Frequency
            amount_col: 'sum'  # Monetary
        })
        
        rfm.columns = ['Recency', 'Frequency', 'Monetary']
        
        # RFM Scores (1-5)
        rfm['R_Score'] = pd.qcut(rfm['Recency'], 5, labels=[5, 4, 3, 2, 1])
        rfm['F_Score'] = pd.qcut(rfm['Frequency'].rank(method='first'), 5, 
                                 labels=[1, 2, 3, 4, 5])
        rfm['M_Score'] = pd.qcut(rfm['Monetary'], 5, labels=[1, 2, 3, 4, 5])
        
        rfm['RFM_Score'] = (rfm['R_Score'].astype(str) + 
                           rfm['F_Score'].astype(str) + 
                           rfm['M_Score'].astype(str))
        
        # Segmentos
        def rfm_segment(row):
            if row['R_Score'] >= 4 and row['F_Score'] >= 4:
                return 'Champions'
            elif row['R_Score'] >= 3 and row['F_Score'] >= 3:
                return 'Loyal Customers'
            elif row['R_Score'] >= 4:
                return 'Potential Loyalists'
            elif row['F_Score'] >= 4:
                return 'Customers Needing Attention'
            elif row['M_Score'] >= 4:
                return 'Big Spenders'
            elif row['R_Score'] <= 2:
                return 'At Risk'
            elif row['R_Score'] <= 2 and row['F_Score'] <= 2:
                return 'Hibernating'
            else:
                return 'Others'
        
        rfm['Segment'] = rfm.apply(rfm_segment, axis=1)
        
        return rfm
    
    # ========================================
    # K-MEANS CLUSTERING
    # ========================================
    
    def train_kmeans(self, n_clusters: int = 5, **kwargs) -> Dict:
        """
        Entrena modelo K-Means
        """
        with mlflow.start_run(run_name="KMeans_Clustering"):
            mlflow.log_params({
                "algorithm": "KMeans",
                "n_clusters": n_clusters,
                **kwargs
            })
            
            if self.scaled_data is None:
                self.preprocess_data()
            
            # Entrenar modelo
            model = KMeans(n_clusters=n_clusters, random_state=42, **kwargs)
            labels = model.fit_predict(self.scaled_data)
            
            # Métricas
            silhouette = silhouette_score(self.scaled_data, labels)
            davies_bouldin = davies_bouldin_score(self.scaled_data, labels)
            calinski = calinski_harabasz_score(self.scaled_data, labels)
            
            mlflow.log_metrics({
                "silhouette_score": silhouette,
                "davies_bouldin_score": davies_bouldin,
                "calinski_harabasz_score": calinski
            })
            
            # Guardar modelo
            mlflow.sklearn.log_model(model, "kmeans_model")
            
            self.models['KMeans'] = model
            self.labels['KMeans'] = labels
            self.metrics['KMeans'] = {
                "silhouette": silhouette,
                "davies_bouldin": davies_bouldin,
                "calinski": calinski
            }
            
            return self.metrics['KMeans']
    
    def find_optimal_k(self, max_k: int = 10) -> int:
        """
        Encuentra el número óptimo de clusters usando el método del codo
        """
        if self.scaled_data is None:
            self.preprocess_data()
        
        inertias = []
        silhouettes = []
        
        K_range = range(2, max_k + 1)
        
        for k in K_range:
            kmeans = KMeans(n_clusters=k, random_state=42)
            kmeans.fit(self.scaled_data)
            
            inertias.append(kmeans.inertia_)
            silhouettes.append(silhouette_score(self.scaled_data, kmeans.labels_))
        
        # Plot
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
        
        ax1.plot(K_range, inertias, 'bo-')
        ax1.set_xlabel('Number of Clusters (k)', fontsize=12)
        ax1.set_ylabel('Inertia', fontsize=12)
        ax1.set_title('Elbow Method', fontsize=14, fontweight='bold')
        ax1.grid(True, alpha=0.3)
        
        ax2.plot(K_range, silhouettes, 'ro-')
        ax2.set_xlabel('Number of Clusters (k)', fontsize=12)
        ax2.set_ylabel('Silhouette Score', fontsize=12)
        ax2.set_title('Silhouette Score vs K', fontsize=14, fontweight='bold')
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        # Optimal k es donde silhouette es máximo
        optimal_k = K_range[np.argmax(silhouettes)]
        
        return optimal_k
    
    # ========================================
    # DBSCAN
    # ========================================
    
    def train_dbscan(self, eps: float = 0.5, min_samples: int = 5) -> Dict:
        """
        Entrena modelo DBSCAN (density-based clustering)
        """
        with mlflow.start_run(run_name="DBSCAN_Clustering"):
            mlflow.log_params({
                "algorithm": "DBSCAN",
                "eps": eps,
                "min_samples": min_samples
            })
            
            if self.scaled_data is None:
                self.preprocess_data()
            
            # Entrenar modelo
            model = DBSCAN(eps=eps, min_samples=min_samples)
            labels = model.fit_predict(self.scaled_data)
            
            # Número de clusters (excluyendo noise -1)
            n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
            n_noise = list(labels).count(-1)
            
            mlflow.log_metrics({
                "n_clusters": n_clusters,
                "n_noise_points": n_noise,
                "noise_percentage": n_noise / len(labels) * 100
            })
            
            # Métricas solo si hay más de 1 cluster
            if n_clusters > 1:
                # Filtrar noise points para métricas
                mask = labels != -1
                silhouette = silhouette_score(self.scaled_data[mask], labels[mask])
                
                mlflow.log_metric("silhouette_score", silhouette)
                
                self.metrics['DBSCAN'] = {
                    "n_clusters": n_clusters,
                    "silhouette": silhouette,
                    "noise_percentage": n_noise / len(labels) * 100
                }
            else:
                self.metrics['DBSCAN'] = {
                    "n_clusters": n_clusters,
                    "noise_percentage": n_noise / len(labels) * 100
                }
            
            self.models['DBSCAN'] = model
            self.labels['DBSCAN'] = labels
            
            return self.metrics['DBSCAN']
    
    # ========================================
    # HIERARCHICAL CLUSTERING
    # ========================================
    
    def train_hierarchical(self, n_clusters: int = 5, 
                          linkage: str = 'ward') -> Dict:
        """
        Entrena modelo de Clustering Jerárquico
        """
        with mlflow.start_run(run_name="Hierarchical_Clustering"):
            mlflow.log_params({
                "algorithm": "Hierarchical",
                "n_clusters": n_clusters,
                "linkage": linkage
            })
            
            if self.scaled_data is None:
                self.preprocess_data()
            
            # Entrenar modelo
            model = AgglomerativeClustering(n_clusters=n_clusters, linkage=linkage)
            labels = model.fit_predict(self.scaled_data)
            
            # Métricas
            silhouette = silhouette_score(self.scaled_data, labels)
            davies_bouldin = davies_bouldin_score(self.scaled_data, labels)
            
            mlflow.log_metrics({
                "silhouette_score": silhouette,
                "davies_bouldin_score": davies_bouldin
            })
            
            self.models['Hierarchical'] = model
            self.labels['Hierarchical'] = labels
            self.metrics['Hierarchical'] = {
                "silhouette": silhouette,
                "davies_bouldin": davies_bouldin
            }
            
            return self.metrics['Hierarchical']
    
    # ========================================
    # GAUSSIAN MIXTURE MODEL
    # ========================================
    
    def train_gmm(self, n_components: int = 5, **kwargs) -> Dict:
        """
        Entrena Gaussian Mixture Model
        """
        with mlflow.start_run(run_name="GMM_Clustering"):
            mlflow.log_params({
                "algorithm": "GaussianMixture",
                "n_components": n_components,
                **kwargs
            })
            
            if self.scaled_data is None:
                self.preprocess_data()
            
            # Entrenar modelo
            model = GaussianMixture(n_components=n_components, random_state=42, **kwargs)
            model.fit(self.scaled_data)
            labels = model.predict(self.scaled_data)
            
            # Métricas
            silhouette = silhouette_score(self.scaled_data, labels)
            bic = model.bic(self.scaled_data)
            aic = model.aic(self.scaled_data)
            
            mlflow.log_metrics({
                "silhouette_score": silhouette,
                "BIC": bic,
                "AIC": aic
            })
            
            mlflow.sklearn.log_model(model, "gmm_model")
            
            self.models['GMM'] = model
            self.labels['GMM'] = labels
            self.metrics['GMM'] = {
                "silhouette": silhouette,
                "BIC": bic,
                "AIC": aic
            }
            
            return self.metrics['GMM']
    
    # ========================================
    # AUTOENCODER CLUSTERING (Deep Learning)
    # ========================================
    
    def build_autoencoder(self, input_dim: int, encoding_dim: int = 10):
        """
        Construye autoencoder para reducción dimensional y clustering
        """
        # Encoder
        input_layer = Input(shape=(input_dim,))
        encoded = Dense(128, activation='relu')(input_layer)
        encoded = Dropout(0.2)(encoded)
        encoded = Dense(64, activation='relu')(encoded)
        encoded = Dropout(0.2)(encoded)
        encoded = Dense(encoding_dim, activation='relu')(encoded)
        
        # Decoder
        decoded = Dense(64, activation='relu')(encoded)
        decoded = Dropout(0.2)(decoded)
        decoded = Dense(128, activation='relu')(decoded)
        decoded = Dropout(0.2)(decoded)
        decoded = Dense(input_dim, activation='linear')(decoded)
        
        # Models
        autoencoder = Model(input_layer, decoded)
        encoder = Model(input_layer, encoded)
        
        autoencoder.compile(optimizer=Adam(0.001), loss='mse')
        
        return autoencoder, encoder
    
    def train_autoencoder_clustering(self, encoding_dim: int = 10, 
                                    n_clusters: int = 5, epochs: int = 100) -> Dict:
        """
        Clustering usando embeddings de autoencoder
        """
        with mlflow.start_run(run_name="Autoencoder_Clustering"):
            mlflow.log_params({
                "algorithm": "Autoencoder + KMeans",
                "encoding_dim": encoding_dim,
                "n_clusters": n_clusters,
                "epochs": epochs
            })
            
            if self.scaled_data is None:
                self.preprocess_data()
            
            input_dim = self.scaled_data.shape[1]
            
            # Construir y entrenar autoencoder
            autoencoder, encoder = self.build_autoencoder(input_dim, encoding_dim)
            
            history = autoencoder.fit(
                self.scaled_data, self.scaled_data,
                epochs=epochs,
                batch_size=32,
                shuffle=True,
                validation_split=0.2,
                verbose=0
            )
            
            # Obtener embeddings
            embeddings = encoder.predict(self.scaled_data, verbose=0)
            
            # Clustering en espacio latente
            kmeans = KMeans(n_clusters=n_clusters, random_state=42)
            labels = kmeans.fit_predict(embeddings)
            
            # Métricas
            silhouette = silhouette_score(embeddings, labels)
            reconstruction_error = history.history['val_loss'][-1]
            
            mlflow.log_metrics({
                "silhouette_score": silhouette,
                "reconstruction_error": reconstruction_error
            })
            
            mlflow.tensorflow.log_model(autoencoder, "autoencoder_model")
            mlflow.tensorflow.log_model(encoder, "encoder_model")
            
            self.models['Autoencoder'] = {'autoencoder': autoencoder, 
                                         'encoder': encoder, 
                                         'kmeans': kmeans}
            self.labels['Autoencoder'] = labels
            self.metrics['Autoencoder'] = {
                "silhouette": silhouette,
                "reconstruction_error": reconstruction_error
            }
            
            return self.metrics['Autoencoder']
    
    # ========================================
    # VISUALIZATION
    # ========================================
    
    def visualize_clusters(self, method: str = 'PCA', algorithm: str = 'KMeans'):
        """
        Visualiza clusters en 2D usando PCA, t-SNE o UMAP
        """
        if self.scaled_data is None:
            self.preprocess_data()
        
        if algorithm not in self.labels:
            raise ValueError(f"Algoritmo {algorithm} no ha sido entrenado todavía")
        
        labels = self.labels[algorithm]
        
        # Reducción dimensional
        if method == 'PCA':
            reducer = PCA(n_components=2, random_state=42)
            title = f'{algorithm} Clustering - PCA Projection'
        elif method == 'TSNE':
            reducer = TSNE(n_components=2, random_state=42, perplexity=30)
            title = f'{algorithm} Clustering - t-SNE Projection'
        else:  # UMAP
            reducer = umap.UMAP(n_components=2, random_state=42)
            title = f'{algorithm} Clustering - UMAP Projection'
        
        coords = reducer.fit_transform(self.scaled_data)
        
        # Plot con Plotly
        fig = px.scatter(
            x=coords[:, 0], y=coords[:, 1],
            color=labels.astype(str),
            title=title,
            labels={'x': f'{method} 1', 'y': f'{method} 2', 'color': 'Cluster'},
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        
        fig.update_traces(marker=dict(size=8, opacity=0.7))
        fig.update_layout(
            width=900, height=600,
            font=dict(size=12),
            showlegend=True
        )
        
        return fig
    
    def get_cluster_profiles(self, algorithm: str = 'KMeans') -> pd.DataFrame:
        """
        Obtiene perfil de cada cluster
        """
        if algorithm not in self.labels:
            raise ValueError(f"Algoritmo {algorithm} no entrenado")
        
        labels = self.labels[algorithm]
        data_with_labels = self.data.copy()
        data_with_labels['Cluster'] = labels
        
        # Estadísticas por cluster
        profiles = data_with_labels.groupby('Cluster').agg(['mean', 'median', 'std', 'count'])
        
        return profiles
    
    def compare_algorithms(self) -> pd.DataFrame:
        """
        Compara métricas de todos los algoritmos entrenados
        """
        comparison = []
        
        for algo, metrics in self.metrics.items():
            row = {'Algorithm': algo}
            row.update(metrics)
            comparison.append(row)
        
        df_comparison = pd.DataFrame(comparison)
        
        return df_comparison


# ========================================
# EJEMPLO DE USO
# ========================================

if __name__ == "__main__":
    # Generar datos de ejemplo
    np.random.seed(42)
    n_samples = 1000
    
    data = pd.DataFrame({
        'recency': np.random.exponential(30, n_samples),
        'frequency': np.random.poisson(5, n_samples),
        'monetary': np.random.gamma(2, 100, n_samples),
        'avg_order_value': np.random.normal(75, 25, n_samples),
        'tenure_days': np.random.uniform(1, 365, n_samples),
        'num_returns': np.random.poisson(1, n_samples),
        'engagement_score': np.random.beta(2, 5, n_samples) * 100
    })
    
    # Inicializar segmentador
    segmenter = CustomerSegmentation(data)
    
    # Encontrar K óptimo
    print("Finding optimal K...")
    optimal_k = segmenter.find_optimal_k(max_k=10)
    print(f"Optimal K: {optimal_k}")
    
    # Entrenar modelos
    print("\nTraining K-Means...")
    segmenter.train_kmeans(n_clusters=optimal_k)
    
    print("Training DBSCAN...")
    segmenter.train_dbscan(eps=0.8, min_samples=10)
    
    print("Training Hierarchical...")
    segmenter.train_hierarchical(n_clusters=optimal_k)
    
    print("Training GMM...")
    segmenter.train_gmm(n_components=optimal_k)
    
    print("Training Autoencoder...")
    segmenter.train_autoencoder_clustering(encoding_dim=10, n_clusters=optimal_k)
    
    # Comparar algoritmos
    print("\nAlgorithm Comparison:")
    comparison = segmenter.compare_algorithms()
    print(comparison)
    
    # Visualizar
    fig = segmenter.visualize_clusters(method='UMAP', algorithm='KMeans')
    fig.write_html('/tmp/clustering_visualization.html')
    print("\nVisualization saved!")
