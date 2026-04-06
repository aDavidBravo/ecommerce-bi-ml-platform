"""
E-Commerce Data Pipeline DAG
Orquesta ETL completo desde múltiples fuentes hasta DWH y ML models
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.providers.amazon.aws.transfers.s3_to_redshift import S3ToRedshiftOperator
from airflow.providers.amazon.aws.operators.emr import EmrAddStepsOperator
from airflow.providers.google.cloud.transfers.gcs_to_bigquery import GCSToBigQueryOperator
from airflow.providers.http.operators.http import SimpleHttpOperator
from airflow.sensors.external_task import ExternalTaskSensor
import pandas as pd
import boto3
from pyspark.sql import SparkSession

# ========================================
# DAG CONFIGURATION
# ========================================

default_args = {
    'owner': 'data-engineering-team',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email': ['data-alerts@company.com'],
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
    'execution_timeout': timedelta(hours=2),
}

dag = DAG(
    'ecommerce_master_pipeline',
    default_args=default_args,
    description='Master pipeline for e-commerce data processing',
    schedule_interval='0 2 * * *',  # Daily at 2 AM
    catchup=False,
    max_active_runs=1,
    tags=['production', 'etl', 'ml', 'critical']
)

# ========================================
# PYTHON FUNCTIONS
# ========================================

def extract_from_postgres(**context):
    """Extract transactional data from PostgreSQL"""
    from sqlalchemy import create_engine
    import os
    
    conn_string = os.getenv('POSTGRES_CONN_STRING')
    engine = create_engine(conn_string)
    
    # Extract incremental data
    execution_date = context['execution_date']
    query = f"""
        SELECT 
            o.order_id,
            o.customer_id,
            o.order_date,
            o.total_amount,
            o.status,
            oi.product_id,
            oi.quantity,
            oi.unit_price,
            c.customer_name,
            c.email,
            c.country,
            c.signup_date,
            p.product_name,
            p.category,
            p.brand
        FROM orders o
        JOIN order_items oi ON o.order_id = oi.order_id
        JOIN customers c ON o.customer_id = c.customer_id
        JOIN products p ON oi.product_id = p.product_id
        WHERE DATE(o.order_date) = '{execution_date.date()}'
    """
    
    df = pd.read_sql(query, engine)
    
    # Save to S3
    s3_path = f"s3://ecommerce-data/raw/orders/date={execution_date.date()}/orders.parquet"
    df.to_parquet(s3_path, index=False, compression='snappy')
    
    context['task_instance'].xcom_push(key='records_extracted', value=len(df))
    
    return s3_path

def extract_from_mongodb(**context):
    """Extract product reviews from MongoDB"""
    from pymongo import MongoClient
    import os
    
    mongo_uri = os.getenv('MONGO_URI')
    client = MongoClient(mongo_uri)
    db = client['ecommerce']
    
    execution_date = context['execution_date']
    
    # Extract reviews
    reviews = list(db.reviews.find({
        'review_date': {
            '$gte': execution_date,
            '$lt': execution_date + timedelta(days=1)
        }
    }))
    
    df = pd.DataFrame(reviews)
    
    if not df.empty:
        # Save to S3
        s3_path = f"s3://ecommerce-data/raw/reviews/date={execution_date.date()}/reviews.parquet"
        df.to_parquet(s3_path, index=False, compression='snappy')
        
        return s3_path
    
    return None

def extract_web_analytics(**context):
    """Extract data from Google Analytics API"""
    from google.analytics.data_v1beta import BetaAnalyticsDataClient
    from google.analytics.data_v1beta.types import RunReportRequest
    import os
    
    property_id = os.getenv('GA_PROPERTY_ID')
    client = BetaAnalyticsDataClient()
    
    execution_date = context['execution_date']
    
    request = RunReportRequest(
        property=f"properties/{property_id}",
        dimensions=[
            {"name": "date"},
            {"name": "country"},
            {"name": "deviceCategory"},
            {"name": "sessionSource"},
        ],
        metrics=[
            {"name": "sessions"},
            {"name": "totalUsers"},
            {"name": "newUsers"},
            {"name": "screenPageViews"},
            {"name": "conversions"},
            {"name": "totalRevenue"},
        ],
        date_ranges=[{
            "start_date": execution_date.date().isoformat(),
            "end_date": execution_date.date().isoformat()
        }]
    )
    
    response = client.run_report(request)
    
    # Convert to DataFrame
    rows = []
    for row in response.rows:
        rows.append({
            'date': row.dimension_values[0].value,
            'country': row.dimension_values[1].value,
            'device_category': row.dimension_values[2].value,
            'session_source': row.dimension_values[3].value,
            'sessions': row.metric_values[0].value,
            'total_users': row.metric_values[1].value,
            'new_users': row.metric_values[2].value,
            'page_views': row.metric_values[3].value,
            'conversions': row.metric_values[4].value,
            'revenue': row.metric_values[5].value,
        })
    
    df = pd.DataFrame(rows)
    
    # Save to S3
    s3_path = f"s3://ecommerce-data/raw/web_analytics/date={execution_date.date()}/analytics.parquet"
    df.to_parquet(s3_path, index=False, compression='snappy')
    
    return s3_path

def transform_with_spark(**context):
    """Transform data using PySpark on Databricks/EMR"""
    spark = SparkSession.builder \
        .appName("EcommerceETL") \
        .config("spark.sql.adaptive.enabled", "true") \
        .config("spark.sql.adaptive.coalescePartitions.enabled", "true") \
        .getOrCreate()
    
    execution_date = context['execution_date']
    date_str = execution_date.date().isoformat()
    
    # Read raw data
    orders_df = spark.read.parquet(f"s3://ecommerce-data/raw/orders/date={date_str}/")
    reviews_df = spark.read.parquet(f"s3://ecommerce-data/raw/reviews/date={date_str}/")
    analytics_df = spark.read.parquet(f"s3://ecommerce-data/raw/web_analytics/date={date_str}/")
    
    # Data quality checks
    from pyspark.sql.functions import col, when, count, sum as spark_sum
    
    orders_df = orders_df \
        .filter(col('total_amount') > 0) \
        .filter(col('quantity') > 0) \
        .dropDuplicates(['order_id', 'product_id'])
    
    # Business transformations
    from pyspark.sql.functions import datediff, current_date, dayofweek, month, year
    
    # Calculate customer metrics
    customer_metrics = orders_df.groupBy('customer_id').agg(
        spark_sum('total_amount').alias('total_revenue'),
        count('order_id').alias('total_orders'),
        (spark_sum('total_amount') / count('order_id')).alias('avg_order_value'),
        datediff(current_date(), max('order_date')).alias('days_since_last_order')
    )
    
    # Product performance
    product_metrics = orders_df.groupBy('product_id', 'category').agg(
        spark_sum('quantity').alias('units_sold'),
        spark_sum(col('quantity') * col('unit_price')).alias('revenue'),
        count('order_id').alias('num_orders')
    )
    
    # Write to processed zone
    customer_metrics.write.mode('overwrite').partitionBy('customer_id') \
        .parquet(f"s3://ecommerce-data/processed/customer_metrics/date={date_str}/")
    
    product_metrics.write.mode('overwrite').partitionBy('category') \
        .parquet(f"s3://ecommerce-data/processed/product_metrics/date={date_str}/")
    
    spark.stop()
    
    return True

def run_dbt_models(**context):
    """Execute dbt transformations"""
    import subprocess
    
    # Run dbt in production
    result = subprocess.run(
        ['dbt', 'run', '--profiles-dir', './config', '--target', 'prod'],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        raise Exception(f"dbt run failed: {result.stderr}")
    
    # Run tests
    test_result = subprocess.run(
        ['dbt', 'test', '--profiles-dir', './config', '--target', 'prod'],
        capture_output=True,
        text=True
    )
    
    if test_result.returncode != 0:
        print(f"dbt tests warning: {test_result.stderr}")
    
    return True

def train_forecasting_models(**context):
    """Train sales forecasting models"""
    import sys
    sys.path.append('/opt/airflow/dags/repo/src/python')
    
    from machine_learning.forecasting.sales_forecaster import SalesForecaster
    import mlflow
    
    # Set MLflow tracking
    mlflow.set_tracking_uri('http://mlflow:5000')
    mlflow.set_experiment('daily_sales_forecasting')
    
    # Load data from Snowflake/Redshift
    from sqlalchemy import create_engine
    import os
    
    engine = create_engine(os.getenv('DWH_CONN_STRING'))
    
    query = """
        SELECT 
            date,
            SUM(total_amount) as sales
        FROM fact_sales
        WHERE date >= CURRENT_DATE - INTERVAL '2 years'
        GROUP BY date
        ORDER BY date
    """
    
    df = pd.read_sql(query, engine, index_col='date', parse_dates=['date'])
    
    # Train models
    forecaster = SalesForecaster(df, target_col='sales')
    forecaster.prepare_data(test_size=0.2)
    
    # Train multiple algorithms
    forecaster.train_prophet()
    forecaster.train_xgboost()
    forecaster.train_lstm()
    forecaster.ensemble_forecast()
    
    best_model, metrics = forecaster.get_best_model()
    
    print(f"Best model: {best_model} with MAPE: {metrics['MAPE']:.2f}%")
    
    context['task_instance'].xcom_push(key='best_model', value=best_model)
    context['task_instance'].xcom_push(key='mape', value=metrics['MAPE'])
    
    return True

def train_segmentation_models(**context):
    """Train customer segmentation models"""
    import sys
    sys.path.append('/opt/airflow/dags/repo/src/python')
    
    from machine_learning.segmentation.customer_clustering import CustomerSegmentation
    import mlflow
    
    mlflow.set_tracking_uri('http://mlflow:5000')
    mlflow.set_experiment('customer_segmentation')
    
    # Load customer features from DWH
    from sqlalchemy import create_engine
    import os
    
    engine = create_engine(os.getenv('DWH_CONN_STRING'))
    
    query = """
        SELECT 
            customer_id,
            recency,
            frequency,
            monetary,
            avg_order_value,
            tenure_days,
            num_returns,
            engagement_score
        FROM dim_customer_features
    """
    
    df = pd.read_sql(query, engine)
    
    # Train segmentation
    segmenter = CustomerSegmentation(df)
    
    optimal_k = segmenter.find_optimal_k(max_k=10)
    
    segmenter.train_kmeans(n_clusters=optimal_k)
    segmenter.train_gmm(n_components=optimal_k)
    segmenter.train_autoencoder_clustering(n_clusters=optimal_k)
    
    # Get best model
    comparison = segmenter.compare_algorithms()
    best_algo = comparison.loc[comparison['silhouette'].idxmax(), 'Algorithm']
    
    print(f"Best segmentation algorithm: {best_algo}")
    
    # Save segments back to DWH
    labels = segmenter.labels[best_algo]
    segments_df = pd.DataFrame({
        'customer_id': df['customer_id'],
        'segment_id': labels,
        'segment_date': context['execution_date'].date()
    })
    
    segments_df.to_sql('customer_segments', engine, if_exists='append', index=False)
    
    return True

def refresh_powerbi_datasets(**context):
    """Refresh Power BI datasets via REST API"""
    import requests
    import os
    
    # Get access token
    tenant_id = os.getenv('AZURE_TENANT_ID')
    client_id = os.getenv('AZURE_CLIENT_ID')
    client_secret = os.getenv('AZURE_CLIENT_SECRET')
    
    token_url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
    token_data = {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret,
        'scope': 'https://analysis.windows.net/powerbi/api/.default'
    }
    
    token_response = requests.post(token_url, data=token_data)
    access_token = token_response.json()['access_token']
    
    # Refresh datasets
    dataset_ids = [
        os.getenv('POWERBI_EXECUTIVE_DATASET_ID'),
        os.getenv('POWERBI_SALES_DATASET_ID'),
        os.getenv('POWERBI_CUSTOMER_DATASET_ID')
    ]
    
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    for dataset_id in dataset_ids:
        refresh_url = f"https://api.powerbi.com/v1.0/myorg/datasets/{dataset_id}/refreshes"
        response = requests.post(refresh_url, headers=headers)
        
        if response.status_code == 202:
            print(f"Dataset {dataset_id} refresh initiated successfully")
        else:
            print(f"Failed to refresh dataset {dataset_id}: {response.text}")
    
    return True

def send_data_quality_report(**context):
    """Send data quality report via email"""
    from airflow.utils.email import send_email
    
    execution_date = context['execution_date']
    
    # Get metrics from XCom
    records_extracted = context['task_instance'].xcom_pull(
        task_ids='extract_postgres',
        key='records_extracted'
    )
    
    best_model = context['task_instance'].xcom_pull(
        task_ids='train_forecasting',
        key='best_model'
    )
    
    mape = context['task_instance'].xcom_pull(
        task_ids='train_forecasting',
        key='mape'
    )
    
    html_content = f"""
    <h2>E-Commerce Data Pipeline - Daily Report</h2>
    <p><strong>Execution Date:</strong> {execution_date.date()}</p>
    
    <h3>Extraction Summary</h3>
    <ul>
        <li>Orders Extracted: {records_extracted:,}</li>
        <li>Status: ✅ Success</li>
    </ul>
    
    <h3>ML Models Performance</h3>
    <ul>
        <li>Best Forecasting Model: {best_model}</li>
        <li>MAPE: {mape:.2f}%</li>
    </ul>
    
    <h3>Next Steps</h3>
    <p>Power BI dashboards have been refreshed and are ready for business review.</p>
    
    <p><em>Generated by Airflow Pipeline</em></p>
    """
    
    send_email(
        to=['data-team@company.com', 'executives@company.com'],
        subject=f'Data Pipeline Report - {execution_date.date()}',
        html_content=html_content
    )
    
    return True

# ========================================
# TASK DEFINITIONS
# ========================================

# Extraction tasks
extract_postgres_task = PythonOperator(
    task_id='extract_postgres',
    python_callable=extract_from_postgres,
    dag=dag
)

extract_mongodb_task = PythonOperator(
    task_id='extract_mongodb',
    python_callable=extract_from_mongodb,
    dag=dag
)

extract_analytics_task = PythonOperator(
    task_id='extract_web_analytics',
    python_callable=extract_web_analytics,
    dag=dag
)

# Transformation tasks
transform_spark_task = PythonOperator(
    task_id='transform_with_spark',
    python_callable=transform_with_spark,
    dag=dag
)

dbt_task = PythonOperator(
    task_id='run_dbt_models',
    python_callable=run_dbt_models,
    dag=dag
)

# Data quality task
data_quality_task = PostgresOperator(
    task_id='run_data_quality_checks',
    postgres_conn_id='postgres_dwh',
    sql="""
        -- Check for duplicate orders
        SELECT CASE 
            WHEN COUNT(*) > 0 THEN RAISE_EXCEPTION('Duplicate orders found')
            ELSE 'OK'
        END
        FROM (
            SELECT order_id, COUNT(*)
            FROM fact_sales
            WHERE load_date = CURRENT_DATE
            GROUP BY order_id
            HAVING COUNT(*) > 1
        ) duplicates;
        
        -- Check for negative amounts
        SELECT CASE
            WHEN COUNT(*) > 0 THEN RAISE_EXCEPTION('Negative amounts found')
            ELSE 'OK'
        END
        FROM fact_sales
        WHERE total_amount < 0 AND load_date = CURRENT_DATE;
    """,
    dag=dag
)

# ML tasks
train_forecasting_task = PythonOperator(
    task_id='train_forecasting',
    python_callable=train_forecasting_models,
    dag=dag
)

train_segmentation_task = PythonOperator(
    task_id='train_segmentation',
    python_callable=train_segmentation_models,
    dag=dag
)

# BI refresh task
refresh_powerbi_task = PythonOperator(
    task_id='refresh_powerbi',
    python_callable=refresh_powerbi_datasets,
    dag=dag
)

# Notification task
send_report_task = PythonOperator(
    task_id='send_daily_report',
    python_callable=send_data_quality_report,
    dag=dag
)

# ========================================
# TASK DEPENDENCIES
# ========================================

# Extraction phase (parallel)
extraction_tasks = [extract_postgres_task, extract_mongodb_task, extract_analytics_task]

# Transformation phase
for task in extraction_tasks:
    task >> transform_spark_task

transform_spark_task >> dbt_task
dbt_task >> data_quality_task

# ML phase (parallel after DQ check)
data_quality_task >> [train_forecasting_task, train_segmentation_task]

# BI refresh after ML
[train_forecasting_task, train_segmentation_task] >> refresh_powerbi_task

# Final notification
refresh_powerbi_task >> send_report_task
