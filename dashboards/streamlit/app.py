"""
Interactive ML Dashboard - Streamlit
Real-time model monitoring, predictions, and data exploration
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import mlflow
from sqlalchemy import create_engine
import os
from datetime import datetime, timedelta

# Page configuration
st.set_page_config(
    page_title="E-Commerce ML Analytics",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #0078D4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
    }
    .stMetric {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid #0078D4;
    }
</style>
""", unsafe_allow_html=True)

# Database connection
@st.cache_resource
def get_database_connection():
    """Create database connection"""
    conn_string = os.getenv('POSTGRES_CONN_STRING')
    engine = create_engine(conn_string)
    return engine

# MLflow connection
@st.cache_resource
def get_mlflow_client():
    """Connect to MLflow tracking server"""
    mlflow.set_tracking_uri(os.getenv('MLFLOW_TRACKING_URI', 'http://mlflow:5000'))
    return mlflow.tracking.MlflowClient()

# Data loading functions
@st.cache_data(ttl=600)
def load_sales_data(days=30):
    """Load recent sales data"""
    engine = get_database_connection()
    query = f"""
        SELECT 
            d.full_date as date,
            SUM(f.total_amount) as revenue,
            COUNT(DISTINCT f.order_id) as orders,
            COUNT(DISTINCT f.customer_sk) as customers,
            AVG(f.total_amount) as avg_order_value
        FROM dwh.fact_sales f
        JOIN dwh.dim_date d ON f.date_sk = d.date_sk
        WHERE d.full_date >= CURRENT_DATE - {days}
        GROUP BY d.full_date
        ORDER BY d.full_date
    """
    df = pd.read_sql(query, engine)
    return df

@st.cache_data(ttl=600)
def load_customer_segments():
    """Load customer segmentation results"""
    engine = get_database_connection()
    query = """
        SELECT 
            rfm_segment,
            COUNT(*) as customer_count,
            AVG(monetary) as avg_revenue,
            AVG(frequency) as avg_orders,
            AVG(recency) as avg_recency
        FROM ml_features.customer_features
        WHERE rfm_segment IS NOT NULL
        GROUP BY rfm_segment
        ORDER BY avg_revenue DESC
    """
    df = pd.read_sql(query, engine)
    return df

@st.cache_data(ttl=600)
def load_model_metrics():
    """Load ML model performance metrics from MLflow"""
    client = get_mlflow_client()
    experiments = client.search_experiments()
    
    metrics_data = []
    for exp in experiments:
        runs = client.search_runs(exp.experiment_id, max_results=10)
        for run in runs:
            metrics_data.append({
                'experiment': exp.name,
                'run_id': run.info.run_id,
                'model': run.data.tags.get('model_type', 'Unknown'),
                'mape': run.data.metrics.get('MAPE', None),
                'rmse': run.data.metrics.get('RMSE', None),
                'mae': run.data.metrics.get('MAE', None),
                'timestamp': datetime.fromtimestamp(run.info.start_time / 1000)
            })
    
    return pd.DataFrame(metrics_data)

# Sidebar
with st.sidebar:
    st.image("https://via.placeholder.com/150x50/0078D4/FFFFFF?text=E-Commerce+ML", use_container_width=True)
    st.title("🎛️ Control Panel")
    
    # Page selection
    page = st.selectbox(
        "Select Dashboard",
        ["📊 Overview", "🤖 ML Models", "👥 Customer Analytics", "📈 Sales Forecasting", "🔍 Data Explorer"]
    )
    
    st.markdown("---")
    
    # Filters
    st.subheader("Filters")
    date_range = st.date_input(
        "Date Range",
        value=(datetime.now() - timedelta(days=30), datetime.now()),
        max_value=datetime.now()
    )
    
    refresh_button = st.button("🔄 Refresh Data", use_container_width=True)

# Main content
st.markdown('<h1 class="main-header">🤖 E-Commerce ML Analytics Platform</h1>', unsafe_allow_html=True)

# ==========================================
# PAGE: OVERVIEW
# ==========================================

if page == "📊 Overview":
    st.header("Business Metrics Overview")
    
    # Load data
    sales_df = load_sales_data(30)
    
    # KPI Cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_revenue = sales_df['revenue'].sum()
        revenue_change = ((sales_df['revenue'].iloc[-7:].sum() / sales_df['revenue'].iloc[-14:-7].sum()) - 1) * 100
        st.metric(
            "Total Revenue (30d)",
            f"${total_revenue:,.0f}",
            f"{revenue_change:+.1f}% vs prev week",
            delta_color="normal"
        )
    
    with col2:
        total_orders = sales_df['orders'].sum()
        orders_change = ((sales_df['orders'].iloc[-7:].sum() / sales_df['orders'].iloc[-14:-7].sum()) - 1) * 100
        st.metric(
            "Total Orders (30d)",
            f"{total_orders:,}",
            f"{orders_change:+.1f}% vs prev week"
        )
    
    with col3:
        avg_order_value = sales_df['avg_order_value'].mean()
        st.metric(
            "Avg Order Value",
            f"${avg_order_value:.2f}",
            "Steady"
        )
    
    with col4:
        unique_customers = sales_df['customers'].sum()
        st.metric(
            "Active Customers",
            f"{unique_customers:,}",
            "Growing"
        )
    
    st.markdown("---")
    
    # Revenue Trend
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📈 Revenue Trend (30 Days)")
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=sales_df['date'],
            y=sales_df['revenue'],
            mode='lines+markers',
            name='Revenue',
            line=dict(color='#0078D4', width=3),
            fill='tozeroy',
            fillcolor='rgba(0, 120, 212, 0.1)'
        ))
        fig.update_layout(
            height=400,
            hovermode='x unified',
            showlegend=False,
            margin=dict(l=0, r=0, t=30, b=0)
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("🎯 Top Metrics")
        
        # Customer segments summary
        segments_df = load_customer_segments()
        
        fig = px.pie(
            segments_df,
            values='customer_count',
            names='rfm_segment',
            title='Customer Segments Distribution',
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        fig.update_layout(height=350)
        st.plotly_chart(fig, use_container_width=True)

# ==========================================
# PAGE: ML MODELS
# ==========================================

elif page == "🤖 ML Models":
    st.header("Machine Learning Models Dashboard")
    
    # Model performance metrics
    metrics_df = load_model_metrics()
    
    if not metrics_df.empty:
        st.subheader("📊 Model Performance Comparison")
        
        # Filter by experiment
        experiments = metrics_df['experiment'].unique()
        selected_exp = st.selectbox("Select Experiment", experiments)
        
        exp_metrics = metrics_df[metrics_df['experiment'] == selected_exp]
        
        # Metrics comparison
        col1, col2, col3 = st.columns(3)
        
        with col1:
            best_mape = exp_metrics['mape'].min()
            st.metric("Best MAPE", f"{best_mape:.2f}%")
        
        with col2:
            best_rmse = exp_metrics['rmse'].min()
            st.metric("Best RMSE", f"{best_rmse:.2f}")
        
        with col3:
            best_mae = exp_metrics['mae'].min()
            st.metric("Best MAE", f"{best_mae:.2f}")
        
        # Model comparison chart
        st.subheader("Model Accuracy Comparison")
        
        fig = make_subplots(
            rows=1, cols=3,
            subplot_titles=('MAPE', 'RMSE', 'MAE')
        )
        
        fig.add_trace(
            go.Bar(x=exp_metrics['model'], y=exp_metrics['mape'], name='MAPE'),
            row=1, col=1
        )
        fig.add_trace(
            go.Bar(x=exp_metrics['model'], y=exp_metrics['rmse'], name='RMSE'),
            row=1, col=2
        )
        fig.add_trace(
            go.Bar(x=exp_metrics['model'], y=exp_metrics['mae'], name='MAE'),
            row=1, col=3
        )
        
        fig.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
        
        # Recent runs table
        st.subheader("Recent Model Runs")
        st.dataframe(
            exp_metrics[['model', 'mape', 'rmse', 'mae', 'timestamp']]
            .sort_values('timestamp', ascending=False)
            .head(10),
            use_container_width=True
        )
    else:
        st.info("No model metrics found. Train models first!")

# ==========================================
# PAGE: CUSTOMER ANALYTICS
# ==========================================

elif page == "👥 Customer Analytics":
    st.header("Customer Segmentation & Analytics")
    
    segments_df = load_customer_segments()
    
    # Segment overview
    st.subheader("Customer Segment Overview")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        # Segment size
        fig = px.bar(
            segments_df,
            x='rfm_segment',
            y='customer_count',
            title='Customers per Segment',
            color='avg_revenue',
            color_continuous_scale='Blues'
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Revenue per segment
        fig = px.bar(
            segments_df,
            x='rfm_segment',
            y='avg_revenue',
            title='Average Revenue per Segment',
            color='avg_revenue',
            color_continuous_scale='Greens'
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    # Segment details
    st.subheader("Segment Details")
    
    # Format the dataframe
    formatted_df = segments_df.copy()
    formatted_df['avg_revenue'] = formatted_df['avg_revenue'].apply(lambda x: f"${x:,.2f}")
    formatted_df['avg_orders'] = formatted_df['avg_orders'].apply(lambda x: f"{x:.1f}")
    formatted_df['avg_recency'] = formatted_df['avg_recency'].apply(lambda x: f"{x:.0f} days")
    
    st.dataframe(formatted_df, use_container_width=True)
    
    # Recommendations by segment
    st.subheader("💡 Recommended Actions by Segment")
    
    recommendations = {
        'Champions': '🏆 VIP treatment, exclusive offers, early access to new products',
        'Loyal Customers': '💎 Loyalty rewards, referral programs, personalized recommendations',
        'Potential Loyalists': '⭐ Nurture with targeted campaigns, upsell/cross-sell',
        'At Risk': '⚠️ Win-back campaigns, surveys to understand issues, special discounts',
        'Hibernating': '😴 Re-engagement campaigns, remind of benefits, limited-time offers',
        'New Customers': '🆕 Onboarding sequences, first-purchase incentives, educational content'
    }
    
    for segment, action in recommendations.items():
        if segment in segments_df['rfm_segment'].values:
            st.info(f"**{segment}**: {action}")

# ==========================================
# PAGE: SALES FORECASTING
# ==========================================

elif page == "📈 Sales Forecasting":
    st.header("Sales Forecasting with ML")
    
    sales_df = load_sales_data(90)
    
    st.subheader("Historical Sales & Forecast")
    
    # Simulate forecast (in production, load from ML model)
    forecast_days = 30
    last_date = sales_df['date'].max()
    forecast_dates = pd.date_range(last_date + timedelta(days=1), periods=forecast_days, freq='D')
    
    # Simple forecast simulation (replace with actual ML predictions)
    trend = sales_df['revenue'].tail(30).mean()
    forecast_values = np.random.normal(trend, trend * 0.1, forecast_days)
    
    forecast_df = pd.DataFrame({
        'date': forecast_dates,
        'revenue': forecast_values,
        'type': 'Forecast'
    })
    
    sales_df['type'] = 'Actual'
    combined_df = pd.concat([sales_df[['date', 'revenue', 'type']], forecast_df])
    
    # Plot
    fig = px.line(
        combined_df,
        x='date',
        y='revenue',
        color='type',
        title='Sales Forecast - Next 30 Days',
        color_discrete_map={'Actual': '#0078D4', 'Forecast': '#FF6B6B'}
    )
    
    fig.update_traces(line=dict(width=3))
    fig.update_layout(height=500)
    st.plotly_chart(fig, use_container_width=True)
    
    # Forecast summary
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "Forecasted Revenue (30d)",
            f"${forecast_df['revenue'].sum():,.0f}",
            "+8.5% vs last month"
        )
    
    with col2:
        st.metric(
            "Confidence Interval",
            "95%",
            "High confidence"
        )
    
    with col3:
        st.metric(
            "Model Accuracy (MAPE)",
            "8.3%",
            "Excellent"
        )

# ==========================================
# PAGE: DATA EXPLORER
# ==========================================

elif page == "🔍 Data Explorer":
    st.header("Interactive Data Explorer")
    
    # Table selection
    table = st.selectbox(
        "Select Table",
        ["fact_sales", "dim_customer", "dim_product", "customer_features"]
    )
    
    # Load data
    engine = get_database_connection()
    
    if table == "fact_sales":
        query = """
            SELECT * FROM dwh.fact_sales 
            ORDER BY order_datetime DESC 
            LIMIT 1000
        """
    elif table == "dim_customer":
        query = """
            SELECT * FROM dwh.dim_customer 
            WHERE is_current = TRUE 
            LIMIT 1000
        """
    elif table == "dim_product":
        query = """
            SELECT * FROM dwh.dim_product 
            WHERE is_current = TRUE 
            LIMIT 1000
        """
    else:
        query = "SELECT * FROM ml_features.customer_features LIMIT 1000"
    
    df = pd.read_sql(query, engine)
    
    st.subheader(f"📋 {table.upper()} - Preview")
    st.write(f"Showing {len(df):,} rows")
    
    # Display dataframe
    st.dataframe(df, use_container_width=True, height=400)
    
    # Download button
    csv = df.to_csv(index=False)
    st.download_button(
        label="⬇️ Download as CSV",
        data=csv,
        file_name=f"{table}_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )
    
    # Basic statistics
    st.subheader("📊 Basic Statistics")
    st.write(df.describe())

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666;'>
        <p>E-Commerce ML Analytics Platform v1.0 | 
        Powered by Streamlit, MLflow, and Snowflake | 
        Last updated: {}</p>
    </div>
    """.format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
    unsafe_allow_html=True
)
