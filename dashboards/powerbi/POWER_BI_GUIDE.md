# 📊 Power BI Dashboards - Professional Implementation Guide

## Overview

Este proyecto incluye 3 dashboards de Power BI de nivel senior/pro diseñados para análisis ejecutivo, ventas y clientes. Cada dashboard utiliza técnicas avanzadas de DAX, modelado de datos optimizado, y best practices de visualización.

---

## 🎯 Dashboard 1: Executive Dashboard

### Propósito
Dashboard ejecutivo para C-level con KPIs críticos del negocio, tendencias financieras y análisis predictivo.

### Páginas del Dashboard

#### 1. **Overview Page**
- **KPI Cards:**
  - Revenue YTD vs Target (con % variance)
  - Profit Margin (con sparkline trend)
  - Active Customers (MoM growth %)
  - Average Order Value (YoY comparison)
  - Customer Lifetime Value
  - Churn Rate (con alertas por color)

- **Visualizaciones Principales:**
  - Revenue Waterfall Chart (Año actual vs anterior)
  - Profit Trend Line con forecast (Prophet ML integration)
  - Geographic Heat Map (Revenue by Country)
  - Top 10 Products Matrix (Revenue, Units, Margin %)

#### 2. **Financial Performance**
- Revenue vs Cost Breakdown (Sankey Diagram)
- Profit Margin Analysis by Category
- Cash Flow Projection (ML-powered)
- Budget vs Actual Variance Analysis
- Revenue Decomposition Tree

#### 3. **Strategic Metrics**
- Market Share Analysis
- Customer Acquisition Cost (CAC)
- Customer Lifetime Value (CLV) Distribution
- Cohort Analysis Matrix
- Net Promoter Score (NPS) Trend

### Medidas DAX Clave

```dax
-- Revenue YTD
Revenue YTD = 
CALCULATE(
    SUM(fact_sales[total_amount]),
    DATESYTD('dim_date'[full_date])
)

-- Revenue Previous Year
Revenue PY = 
CALCULATE(
    [Revenue YTD],
    DATEADD('dim_date'[full_date], -1, YEAR)
)

-- Revenue Growth %
Revenue Growth % = 
DIVIDE(
    [Revenue YTD] - [Revenue PY],
    [Revenue PY],
    0
)

-- Profit Margin %
Profit Margin % = 
DIVIDE(
    SUM(fact_sales[profit_amount]),
    SUM(fact_sales[total_amount]),
    0
)

-- Active Customers
Active Customers = 
CALCULATE(
    DISTINCTCOUNT(fact_sales[customer_sk]),
    fact_sales[order_datetime] >= TODAY() - 90
)

-- Customer Lifetime Value
Customer LTV = 
AVERAGEX(
    VALUES(dim_customer[customer_sk]),
    CALCULATE(SUM(fact_sales[total_amount]))
)

-- Churn Rate
Churn Rate = 
VAR CustomersLastPeriod = 
    CALCULATE(
        DISTINCTCOUNT(fact_sales[customer_sk]),
        DATEADD('dim_date'[full_date], -1, QUARTER)
    )
VAR CustomersThisPeriod = 
    DISTINCTCOUNT(fact_sales[customer_sk])
VAR ChurnedCustomers = CustomersLastPeriod - CustomersThisPeriod
RETURN
    DIVIDE(ChurnedCustomers, CustomersLastPeriod, 0)

-- Forecast Revenue (using Python visual with Prophet)
Forecast_Revenue = 
PYTHON(
    'from prophet import Prophet
     import pandas as pd
     
     df = dataset[["date", "revenue"]].rename(columns={"date": "ds", "revenue": "y"})
     model = Prophet(yearly_seasonality=True, weekly_seasonality=True)
     model.fit(df)
     
     future = model.make_future_dataframe(periods=90)
     forecast = model.predict(future)
     
     result = forecast[["ds", "yhat", "yhat_lower", "yhat_upper"]]'
)
```

### Características Avanzadas
- **Drill-through:** De cualquier KPI a análisis detallado
- **Bookmarks:** Vistas guardadas para diferentes stakeholders
- **What-if Parameters:** Simulación de escenarios
- **Conditional Formatting:** Alertas automáticas por umbrales
- **Row-Level Security (RLS):** Por región/país
- **Incremental Refresh:** Optimización de performance
- **Composite Models:** Mezcla DirectQuery + Import

---

## 💰 Dashboard 2: Sales Analytics Dashboard

### Propósito
Análisis profundo de ventas para sales managers, con drill-downs geográficos, análisis de productos y performance de vendedores.

### Páginas del Dashboard

#### 1. **Sales Overview**
- **Matrices y Grids:**
  - Sales by Product Category (Treemap)
  - Revenue by Region (Filled Map con drill-through)
  - Top Performing Products (Table con conditional formatting)
  - Bottom 10 Products (Alertas automáticas)

- **Time Intelligence:**
  - Sales Trend (Line Chart con anomaly detection)
  - Seasonality Analysis (Decomposition)
  - YoY / MoM / WoW Comparison
  - Moving Averages (7, 30, 90 days)

#### 2. **Geographic Analysis**
- Multi-level Geographic Drill-down:
  - Continent → Country → State → City
- Sales Density Heat Map
- Shipping Performance by Location
- Regional Quota Attainment

#### 3. **Product Performance**
- **ABC Analysis:**
  - A Products (80% revenue)
  - B Products (15% revenue)
  - C Products (5% revenue)

- **Product Lifecycle Matrix:**
  - Stars, Cash Cows, Question Marks, Dogs

- **Cross-sell / Upsell Analysis:**
  - Market Basket Analysis results
  - Product Affinity Matrix

#### 4. **Sales Funnel**
- Lead → Opportunity → Quote → Won/Lost
- Conversion Rates by Stage
- Average Deal Size by Stage
- Sales Cycle Duration

### Medidas DAX Clave

```dax
-- Sales MoM Growth
Sales MoM % = 
VAR CurrentMonth = [Total Sales]
VAR PreviousMonth = 
    CALCULATE(
        [Total Sales],
        DATEADD('dim_date'[full_date], -1, MONTH)
    )
RETURN
    DIVIDE(CurrentMonth - PreviousMonth, PreviousMonth, 0)

-- Sales by Category %
Category % of Total = 
DIVIDE(
    SUM(fact_sales[total_amount]),
    CALCULATE(
        SUM(fact_sales[total_amount]),
        ALL(dim_product[category])
    ),
    0
)

-- ABC Classification
ABC Class = 
VAR ProductRank = 
    RANKX(
        ALL(dim_product[product_id]),
        [Total Sales],
        ,
        DESC,
        DENSE
    )
VAR TotalProducts = COUNTROWS(ALL(dim_product[product_id]))
VAR ClassA = TotalProducts * 0.2
VAR ClassB = TotalProducts * 0.3
RETURN
    SWITCH(
        TRUE(),
        ProductRank <= ClassA, "A",
        ProductRank <= ClassA + ClassB, "B",
        "C"
    )

-- Anomaly Detection
Is Anomaly = 
VAR CurrentSales = [Total Sales]
VAR AvgSales = AVERAGEX(
    DATESINPERIOD('dim_date'[full_date], MAX('dim_date'[full_date]), -90, DAY),
    [Total Sales]
)
VAR StdDev = STDEVX.P(
    DATESINPERIOD('dim_date'[full_date], MAX('dim_date'[full_date]), -90, DAY),
    [Total Sales]
)
VAR UpperBound = AvgSales + (2 * StdDev)
VAR LowerBound = AvgSales - (2 * StdDev)
RETURN
    IF(CurrentSales > UpperBound || CurrentSales < LowerBound, 1, 0)

-- Market Basket Analysis (Apriori Algorithm result)
Product Affinity Score = 
CALCULATE(
    COUNTROWS(fact_sales),
    FILTER(
        fact_sales,
        fact_sales[product_sk] IN VALUES(dim_product[product_sk])
    )
) / COUNTROWS(fact_sales)

-- Sales Forecast with Confidence Interval
Sales Forecast Upper = 
[Sales Forecast] + (1.96 * [Forecast Std Error])

Sales Forecast Lower = 
[Sales Forecast] - (1.96 * [Forecast Std Error])
```

### Características Avanzadas
- **Field Parameters:** Cambio dinámico de métricas
- **Smart Narratives:** Insights automáticos con NLP
- **Decomposition Tree:** Análisis de drivers de ventas
- **Key Influencers Visual:** ¿Qué impacta las ventas?
- **Q&A Natural Language:** Consultas en lenguaje natural
- **Mobile Layout:** Diseño responsivo para tablets/móviles

---

## 👥 Dashboard 3: Customer Insights Dashboard

### Propósito
Análisis 360° de clientes para marketing y customer success teams, con segmentación ML y análisis predictivo.

### Páginas del Dashboard

#### 1. **Customer Overview**
- **KPIs:**
  - Total Customers (con segmentación)
  - New Customers This Month
  - Churned Customers
  - Customer Retention Rate
  - Net Promoter Score (NPS)

- **Visualizaciones:**
  - Customer Acquisition Trend
  - Customer Value Pyramid
  - Geographic Distribution
  - Customer Age Distribution

#### 2. **RFM Segmentation**
- **RFM Matrix:**
  - Champions (R5-F5-M5)
  - Loyal Customers (R4-F4-M4)
  - Potential Loyalists
  - At Risk
  - Hibernating
  - Lost Customers

- **Segment Profiles:**
  - Average metrics per segment
  - Recommended actions per segment
  - Segment migration flow (Sankey)

#### 3. **Customer Journey**
- Touchpoint Analysis
- Channel Attribution Model
- Customer Lifecycle Stage
- Engagement Score Trend
- Campaign Response Analysis

#### 4. **Predictive Analytics**
- **Churn Prediction:**
  - Churn Probability Score (ML model)
  - At-Risk Customer List
  - Churn Drivers Analysis

- **CLV Prediction:**
  - Predicted Lifetime Value
  - High-Value Customer Identification
  - Investment Priority Matrix

- **Next Best Action:**
  - Recommended product per customer
  - Optimal contact time
  - Channel preference

#### 5. **Sentiment Analysis**
- Review Sentiment Distribution
- Sentiment Trend Over Time
- Word Cloud of Reviews
- Net Sentiment Score by Product

### Medidas DAX Clave

```dax
-- RFM Score Calculation
Recency Score = 
VAR CustomerLastOrder = 
    MAX(fact_sales[order_datetime])
VAR DaysSinceLastOrder = 
    DATEDIFF(CustomerLastOrder, TODAY(), DAY)
RETURN
    SWITCH(
        TRUE(),
        DaysSinceLastOrder <= 30, 5,
        DaysSinceLastOrder <= 60, 4,
        DaysSinceLastOrder <= 90, 3,
        DaysSinceLastOrder <= 180, 2,
        1
    )

Frequency Score = 
VAR OrderCount = 
    COUNTROWS(fact_sales)
RETURN
    SWITCH(
        TRUE(),
        OrderCount >= 20, 5,
        OrderCount >= 10, 4,
        OrderCount >= 5, 3,
        OrderCount >= 2, 2,
        1
    )

Monetary Score = 
VAR TotalSpent = 
    SUM(fact_sales[total_amount])
RETURN
    SWITCH(
        TRUE(),
        TotalSpent >= 5000, 5,
        TotalSpent >= 2000, 4,
        TotalSpent >= 1000, 3,
        TotalSpent >= 500, 2,
        1
    )

RFM Segment = 
VAR R = [Recency Score]
VAR F = [Frequency Score]
VAR M = [Monetary Score]
RETURN
    SWITCH(
        TRUE(),
        R >= 4 && F >= 4 && M >= 4, "Champions",
        R >= 3 && F >= 3 && M >= 3, "Loyal Customers",
        R >= 4 && F <= 2, "New Customers",
        R >= 3 && F >= 3 && M <= 2, "Potential Loyalists",
        R <= 2 && F >= 3 && M >= 3, "At Risk",
        R <= 2 && F <= 2 && M >= 3, "Can't Lose Them",
        R <= 2 && F <= 2 && M <= 2, "Hibernating",
        "Others"
    )

-- Customer Retention Rate
Retention Rate = 
VAR CustomersLastPeriod = 
    CALCULATE(
        DISTINCTCOUNT(fact_sales[customer_sk]),
        DATEADD('dim_date'[full_date], -1, MONTH)
    )
VAR CustomersThisPeriod = 
    DISTINCTCOUNT(fact_sales[customer_sk])
VAR RetainedCustomers = 
    CALCULATE(
        DISTINCTCOUNT(fact_sales[customer_sk]),
        FILTER(
            ALL(fact_sales),
            CONTAINS(
                CALCULATETABLE(
                    VALUES(fact_sales[customer_sk]),
                    DATEADD('dim_date'[full_date], -1, MONTH)
                ),
                fact_sales[customer_sk],
                fact_sales[customer_sk]
            )
        )
    )
RETURN
    DIVIDE(RetainedCustomers, CustomersLastPeriod, 0)

-- Churn Probability (from ML model in Python)
Churn Probability = 
PYTHON(
    'import pandas as pd
     from sklearn.ensemble import RandomForestClassifier
     import pickle
     
     # Load pre-trained model
     with open("/models/churn_model.pkl", "rb") as f:
         model = pickle.load(f)
     
     # Predict
     X = dataset[["recency", "frequency", "monetary", "tenure_days"]]
     predictions = model.predict_proba(X)[:, 1]
     
     result = pd.DataFrame({"churn_prob": predictions})'
)

-- Customer Lifetime Value (Predicted)
Predicted CLV = 
VAR AvgOrderValue = [Avg Order Value]
VAR PurchaseFrequency = [Frequency Score]
VAR CustomerLifespan = 3  -- Years
RETURN
    AvgOrderValue * PurchaseFrequency * 12 * CustomerLifespan

-- Net Promoter Score
NPS = 
VAR Promoters = 
    CALCULATE(
        COUNTROWS(fact_customer_reviews),
        fact_customer_reviews[rating] >= 9
    )
VAR Detractors = 
    CALCULATE(
        COUNTROWS(fact_customer_reviews),
        fact_customer_reviews[rating] <= 6
    )
VAR TotalResponses = COUNTROWS(fact_customer_reviews)
RETURN
    DIVIDE(Promoters - Detractors, TotalResponses, 0) * 100

-- Sentiment Score (from NLP model)
Sentiment Score = 
CALCULATE(
    AVERAGE(fact_customer_reviews[sentiment_score])
)
```

### Características Avanzadas
- **Python/R Visuals:** ML model predictions inline
- **AI Insights:** Automated insights from Azure
- **Dynamic Personas:** Customer profiles que cambian con filtros
- **Cohort Tables:** Análisis de cohortes interactivo
- **Email Reports:** Automated exports para customer success
- **Embedded Analytics:** Iframe para portal de clientes

---

## 🚀 Implementation Steps

### 1. Data Source Setup

```powerquery
// Connection to Snowflake DWH
let
    Source = Snowflake.Databases(
        "your-account.snowflakecomputing.com",
        "ECOMMERCE_DWH",
        [Role="DATA_ANALYST"]
    ),
    Database = Source{[Name="ECOMMERCE_DWH"]}[Data],
    Schema = Database{[Name="DWH"]}[Data]
in
    Schema
```

### 2. Data Model Configuration

**Relaciones:**
- fact_sales → dim_customer (many-to-one)
- fact_sales → dim_product (many-to-one)
- fact_sales → dim_date (many-to-one)
- fact_sales → dim_geography (many-to-one)

**Optimizaciones:**
- Bi-directional filters solo donde sea necesario
- DirectQuery para tablas grandes (>100M filas)
- Aggregations para performance
- Calculated columns → Measures (preferir measures)

### 3. Performance Optimization

- **Query Folding:** Verificar que queries se ejecuten en source
- **Incremental Refresh:** Configurar para fact tables
- **Composite Models:** DirectQuery + Import mix
- **Aggregations:** Pre-calcular métricas comunes
- **Variables en DAX:** Usar VAR para reutilizar cálculos

### 4. Security Implementation

```dax
// Row-Level Security por región
[Region] = USERNAME()

// Manager can see all
[Region] = "All" || USERNAME() = "manager@company.com"
```

---

## 📦 Archivos Incluidos

```
dashboards/powerbi/
├── executive_dashboard.pbix         # Dashboard Ejecutivo
├── sales_analytics.pbix             # Dashboard de Ventas
├── customer_insights.pbix           # Dashboard de Clientes
├── shared_datasets/
│   ├── ecommerce_semantic_model.pbix
│   └── ml_predictions.pbix
├── templates/
│   ├── corporate_theme.json
│   └── custom_visuals/
└── documentation/
    ├── POWER_BI_GUIDE.md (este archivo)
    ├── DAX_measures.txt
    └── data_model_diagram.png
```

---

## 🎨 Design Guidelines

### Color Palette
- **Primary:** #0078D4 (Azure Blue)
- **Secondary:** #107C10 (Success Green)
- **Warning:** #FFB900 (Gold)
- **Danger:** #E81123 (Red)
- **Neutral:** #605E5C (Gray)

### Typography
- **Headers:** Segoe UI Bold, 24pt
- **Subheaders:** Segoe UI Semibold, 16pt
- **Body:** Segoe UI Regular, 11pt
- **KPIs:** Segoe UI Bold, 32pt

### Visual Best Practices
- Maximum 6-8 visuals per page
- Consistent spacing (16px grid)
- White space for breathing room
- Mobile-first design thinking
- Accessible color contrasts (WCAG AA)

---

## 📈 Maintenance & Updates

### Refresh Schedule
- **Incremental:** Every 4 hours (fact tables)
- **Full:** Daily at 2 AM (dimension tables)
- **On-demand:** Available via API

### Version Control
- Store .pbix files in Git LFS
- Document changes in CHANGELOG.md
- Tag releases (v1.0, v1.1, etc.)

### Monitoring
- Track refresh failures
- Monitor query performance (> 30s)
- Review DAX query plans monthly
- Audit RLS effectiveness

---

## 🤝 Support & Contact

Para soporte técnico sobre estos dashboards:
- Email: bi-team@company.com
- Slack: #powerbi-support
- Documentation: https://docs.company.com/powerbi

---

**Última Actualización:** 2024
**Versión:** 1.0.0
**Autor:** Data Engineering & BI Team
