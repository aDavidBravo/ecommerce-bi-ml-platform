# 🚀 Guía de Inicio Rápido - E-Commerce BI/ML Platform

## Instalación en 5 Minutos

### Opción 1: Docker (Recomendado)

```bash
# 1. Clonar repositorio
git clone https://github.com/aDavidBravo/ecommerce-bi-ml-platform.git
cd ecommerce-bi-ml-platform

# 2. Configurar variables de entorno
cp .env.example .env
# Editar .env con tus credenciales

# 3. Levantar toda la infraestructura
docker-compose up -d

# 4. Verificar servicios
docker-compose ps

# 5. Acceder a servicios
# - Airflow: http://localhost:8081 (admin/admin)
# - Jupyter: http://localhost:8888
# - MLflow: http://localhost:5000
# - Streamlit: http://localhost:8501
# - Grafana: http://localhost:3000
```

### Opción 2: Instalación Local

```bash
# 1. Crear entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Configurar base de datos
python scripts/init_database.py

# 4. Ejecutar Streamlit dashboard
streamlit run dashboards/streamlit/app.py
```

## Servicios Disponibles

| Servicio | Puerto | URL | Credenciales |
|----------|--------|-----|--------------|
| Airflow Web UI | 8081 | http://localhost:8081 | admin/admin |
| Jupyter Lab | 8888 | http://localhost:8888 | (sin token) |
| MLflow UI | 5000 | http://localhost:5000 | - |
| Streamlit Dashboard | 8501 | http://localhost:8501 | - |
| Prometheus | 9090 | http://localhost:9090 | - |
| Grafana | 3000 | http://localhost:3000 | admin/admin |
| Metabase | 3001 | http://localhost:3001 | - |
| PostgreSQL | 5432 | localhost:5432 | dataengineer/changeme |
| MongoDB | 27017 | localhost:27017 | admin/changeme |
| Redis | 6379 | localhost:6379 | - |
| Spark Master UI | 8080 | http://localhost:8080 | - |
| Kafka | 9092 | localhost:9092 | - |

## Primeros Pasos

### 1. Cargar Datos de Ejemplo

```bash
python scripts/load_sample_data.py
```

### 2. Ejecutar Pipeline de Datos

Desde Airflow UI:
1. Ir a http://localhost:8081
2. Activar el DAG `ecommerce_master_pipeline`
3. Trigger manualmente o esperar ejecución programada

### 3. Entrenar Modelos ML

```bash
# Forecasting
python src/python/machine_learning/forecasting/sales_forecaster.py

# Segmentación
python src/python/machine_learning/segmentation/customer_clustering.py
```

### 4. Ver Dashboards

- **Streamlit**: http://localhost:8501
- **MLflow**: http://localhost:5000
- **Power BI**: Abrir archivos .pbix en `dashboards/powerbi/`

## Próximos Pasos

1. ✅ Instalar y levantar servicios
2. ✅ Cargar datos de ejemplo
3. ✅ Ejecutar pipeline ETL
4. ✅ Entrenar modelos ML
5. ✅ Explorar dashboards
6. 🔜 Conectar a tus datos reales
7. 🔜 Customizar modelos para tu negocio
8. 🔜 Desplegar a producción

---

**¡Feliz análisis! 🎉**
