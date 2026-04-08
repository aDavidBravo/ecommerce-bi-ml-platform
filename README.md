# 🚀 E-Commerce Business Intelligence & Machine Learning Platform

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![Scala](https://img.shields.io/badge/Scala-2.13-red.svg)](https://www.scala-lang.org/)
[![Spark](https://img.shields.io/badge/Apache%20Spark-3.4-orange.svg)](https://spark.apache.org/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg)](https://www.docker.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## 📋 Descripción del Proyecto

Plataforma empresarial completa de Business Intelligence y Machine Learning para análisis avanzado de e-commerce multinacional. Este proyecto integra el stack completo de tecnologías modernas de Data Science, incluyendo procesamiento distribuido, aprendizaje automático, deep learning, orquestación de pipelines, y visualización avanzada de datos.

### 🎯 Objetivos del Negocio

- **Predicción de Ventas**: Modelos de forecasting con LSTM, Prophet y XGBoost
- **Segmentación de Clientes**: Clustering avanzado con K-Means, DBSCAN y redes neuronales
- **Análisis de Sentimientos**: NLP con BERT y transformers para reviews de productos
- **Sistemas de Recomendación**: Collaborative filtering y deep learning (NCF)
- **Detección de Fraude**: Anomaly detection con Isolation Forest y autoencoders
- **Optimización de Inventario**: Reinforcement learning para gestión de stock
- **Análisis de Churn**: Modelos predictivos multi-algoritmo
- **Price Optimization**: Algoritmos de pricing dinámico

## 🛠️ Stack Tecnológico Completo

### Lenguajes de Programación (4)
- **Python 3.9+**, **Scala 2.13**, **SQL**, **R**

### Machine Learning (8+)
- Scikit-learn, XGBoost, LightGBM, CatBoost, Prophet, ARIMA, MLflow, Optuna

### Deep Learning (6+)
- TensorFlow, PyTorch, Transformers, BERT, LSTM, Autoencoders

### Big Data (8+)
- Spark, Databricks, Kafka, Flink, Dask, Ray, Delta Lake, Iceberg

### Data Warehousing (5+)
- Snowflake, Redshift, BigQuery, Synapse, PostgreSQL

### Cloud (3)
- AWS, Azure, GCP

### DevOps (3)
- Docker, Kubernetes, Docker Compose

### Visualización (5)
- **Power BI** (3 dashboards senior), Tableau, Plotly, Streamlit, Matplotlib

## 🚀 Inicio Rápido

```bash
# 1. Clonar repositorio
git clone https://github.com/aDavidBravo/ecommerce-bi-ml-platform.git
cd ecommerce-bi-ml-platform

# 2. Levantar infraestructura completa
docker-compose up -d

# 3. Acceder a servicios
# Streamlit: http://localhost:8501
# Airflow: http://localhost:8081
# MLflow: http://localhost:5000
```

Ver [QUICKSTART.md](QUICKSTART.md) para instalación detallada.

## 📊 Dashboards Power BI (Nivel Senior)

### 1. Executive Dashboard
KPIs ejecutivos, forecasting ML, análisis geográfico

### 2. Sales Analytics Dashboard  
Drill-downs multi-nivel, ABC analysis, sales funnel

### 3. Customer Insights Dashboard
RFM segmentation, churn prediction, sentiment analysis

Ver [POWER_BI_GUIDE.md](dashboards/powerbi/POWER_BI_GUIDE.md) para detalles completos.

## 🤖 Modelos de Machine Learning

| Modelo | Algoritmo | Métrica | Performance |
|--------|-----------|---------|-------------|
| Sales Forecasting | LSTM + Prophet | MAPE | 8.3% |
| Customer Segmentation | K-Means + DBSCAN | Silhouette | 0.73 |
| Churn Prediction | XGBoost | AUC-ROC | 0.91 |
| Fraud Detection | Isolation Forest | Precision | 0.94 |

## 📁 Estructura del Proyecto

```
ecommerce-bi-ml-platform/
├── 📊 dashboards/          # Power BI, Tableau, Streamlit
├── 🐍 src/
│   ├── python/             # ML models, data engineering
│   ├── scala/              # Spark jobs
│   ├── sql/                # DWH schemas
│   └── r/                  # Statistical models
├── 🔧 infrastructure/      # Docker, K8s, Terraform
├── 🔄 pipelines/           # Airflow, dbt, Prefect
├── 📚 notebooks/           # Jupyter notebooks
└── 🧪 tests/               # Unit, integration tests
```

## 📈 Casos de Uso

1. **Predicción de Ventas** - Forecasting con 5 algoritmos
2. **Segmentación de Clientes** - Clustering avanzado + RFM
3. **Sistema de Recomendaciones** - Neural CF + Matrix Factorization
4. **Análisis de Sentimientos** - BERT fine-tuning
5. **Detección de Fraude** - Isolation Forest + Autoencoders

## 📚 Documentación

- [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) - Resumen ejecutivo completo
- [QUICKSTART.md](QUICKSTART.md) - Guía de inicio rápido
- [POWER_BI_GUIDE.md](dashboards/powerbi/POWER_BI_GUIDE.md) - Guía de dashboards

## 📝 Licencia

MIT License - Ver [LICENSE](LICENSE)

## 📧 Contacto

**David Bravo**
- GitHub: [@aDavidBravo](https://github.com/aDavidBravo)

---

⭐ **Si este proyecto te es útil, dale una estrella!**