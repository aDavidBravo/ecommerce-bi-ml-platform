# ==========================================
# Script Automático PowerShell para GitHub
# E-Commerce BI/ML Platform
# ==========================================

# Colores
$Green = "Green"
$Blue = "Cyan"
$Yellow = "Yellow"
$Red = "Red"

Write-Host "==========================================" -ForegroundColor $Blue
Write-Host "🚀 E-Commerce BI/ML Platform" -ForegroundColor $Green
Write-Host "Subida Automática a GitHub" -ForegroundColor $Green
Write-Host "==========================================" -ForegroundColor $Blue
Write-Host ""

# Variables
$RepoName = "ecommerce-bi-ml-platform"
$GitHubUser = "aDavidBravo"
$RepoDesc = "🚀 Enterprise BI & ML Platform for E-Commerce | Python, Scala, Spark, TensorFlow, PyTorch, Docker, Airflow, Power BI | 40+ Technologies"

# Verificar que estamos en el directorio correcto
if (-not (Test-Path "README.md") -or -not (Test-Path "docker-compose.yml")) {
    Write-Host "❌ Error: No estamos en el directorio del proyecto" -ForegroundColor $Red
    Write-Host "Por favor navega al directorio ecommerce-bi-ml-platform" -ForegroundColor $Yellow
    exit 1
}

Write-Host "1. Verificando Git..." -ForegroundColor $Blue
if (Test-Path ".git") {
    Write-Host "✓ Repositorio Git encontrado" -ForegroundColor $Green
} else {
    Write-Host "⚠️  Inicializando repositorio Git..." -ForegroundColor $Yellow
    git init
    git branch -M main
    Write-Host "✓ Repositorio Git inicializado" -ForegroundColor $Green
}

Write-Host ""
Write-Host "2. Agregando archivos..." -ForegroundColor $Blue
git add -A
Write-Host "✓ Archivos agregados" -ForegroundColor $Green

Write-Host ""
Write-Host "3. Creando commit..." -ForegroundColor $Blue
$commitMessage = @"
Initial commit: E-Commerce BI/ML Platform

Complete Business Intelligence and Machine Learning platform with:
- 40+ technologies integrated (Python, Scala, SQL, R)
- Machine Learning: Scikit-learn, XGBoost, TensorFlow, PyTorch
- Big Data: Spark, Databricks, Kafka, Flink
- DWH: Snowflake, Redshift, BigQuery
- Cloud: AWS, Azure, GCP
- DevOps: Docker, Kubernetes, Airflow
- Visualization: Power BI (3 dashboards), Tableau, Streamlit

Components:
- Python ML modules (Forecasting with 5 algorithms, Customer Segmentation)
- Complete Airflow DAG for ETL pipeline
- Docker Compose with 15+ services
- Data Warehouse SQL schemas
- Interactive Streamlit dashboard
- Production-ready configuration

Stack: Python 3.9+, Scala 2.13, Apache Spark 3.4, TensorFlow 2.x, PyTorch 2.x
Level: Senior/Expert Data Scientist
Technologies: 40+
Lines of Code: 5000+
"@

try {
    git commit -m $commitMessage 2>$null
    Write-Host "✓ Commit creado" -ForegroundColor $Green
} catch {
    Write-Host "ℹ️  Ya existe un commit" -ForegroundColor $Yellow
}

Write-Host ""
Write-Host "4. Verificando GitHub CLI..." -ForegroundColor $Blue

# Verificar si gh está instalado
$ghInstalled = $null -ne (Get-Command gh -ErrorAction SilentlyContinue)

if ($ghInstalled) {
    Write-Host "✓ GitHub CLI encontrado" -ForegroundColor $Green
    Write-Host ""
    Write-Host "5. Creando repositorio en GitHub..." -ForegroundColor $Blue
    
    # Verificar autenticación
    $authStatus = gh auth status 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "⚠️  No estás autenticado en GitHub CLI" -ForegroundColor $Yellow
        Write-Host "Ejecutando: gh auth login" -ForegroundColor $Yellow
        gh auth login
    }
    
    # Crear repositorio
    try {
        gh repo create $RepoName --public --description $RepoDesc --source=. --remote=origin --push
        Write-Host ""
        Write-Host "==========================================" -ForegroundColor $Green
        Write-Host "✅ ¡COMPLETADO!" -ForegroundColor $Green
        Write-Host "==========================================" -ForegroundColor $Green
        Write-Host ""
        Write-Host "Tu proyecto está en:" -ForegroundColor $Blue
        Write-Host "https://github.com/$GitHubUser/$RepoName" -ForegroundColor $Green
        Write-Host ""
    } catch {
        Write-Host "⚠️  El repositorio ya existe o hubo un error" -ForegroundColor $Yellow
        Write-Host "Intentando push manual..." -ForegroundColor $Yellow
        
        git remote remove origin 2>$null
        git remote add origin "https://github.com/$GitHubUser/$RepoName.git"
        git push -u origin main
    }
    
} else {
    Write-Host "⚠️  GitHub CLI no está instalado" -ForegroundColor $Yellow
    Write-Host ""
    Write-Host "=========================================="  -ForegroundColor $Yellow
    Write-Host "OPCIÓN 1: Instalar GitHub CLI (Recomendado)" -ForegroundColor $Yellow
    Write-Host "=========================================="  -ForegroundColor $Yellow
    Write-Host ""
    Write-Host "1. Descarga GitHub CLI desde:" -ForegroundColor $Blue
    Write-Host "   https://cli.github.com/" -ForegroundColor $Green
    Write-Host ""
    Write-Host "2. Instala y reinicia PowerShell" -ForegroundColor $Blue
    Write-Host ""
    Write-Host "3. Ejecuta este script nuevamente" -ForegroundColor $Blue
    Write-Host ""
    Write-Host "=========================================="  -ForegroundColor $Yellow
    Write-Host "OPCIÓN 2: Subida Manual" -ForegroundColor $Yellow
    Write-Host "=========================================="  -ForegroundColor $Yellow
    Write-Host ""
    Write-Host "1. Ir a: https://github.com/$GitHubUser" -ForegroundColor $Blue
    Write-Host "2. Click en 'New repository'" -ForegroundColor $Blue
    Write-Host "3. Nombre: $RepoName" -ForegroundColor $Yellow
    Write-Host "4. Descripción:" -ForegroundColor $Blue
    Write-Host "   $RepoDesc" -ForegroundColor $Green
    Write-Host "5. Seleccionar: Public" -ForegroundColor $Blue
    Write-Host "6. NO marcar 'Add README'" -ForegroundColor $Red
    Write-Host "7. Click 'Create repository'" -ForegroundColor $Blue
    Write-Host ""
    Write-Host "8. Luego ejecuta:" -ForegroundColor $Blue
    Write-Host "   git remote add origin https://github.com/$GitHubUser/$RepoName.git" -ForegroundColor $Green
    Write-Host "   git push -u origin main" -ForegroundColor $Green
    Write-Host ""
}

Write-Host ""
Write-Host "=========================================="  -ForegroundColor $Blue
Write-Host "Configuración Adicional Recomendada" -ForegroundColor $Blue
Write-Host "=========================================="  -ForegroundColor $Blue
Write-Host ""
Write-Host "En tu repositorio de GitHub:" -ForegroundColor $Yellow
Write-Host ""
Write-Host "1. Agregar Topics/Tags:" -ForegroundColor $Blue
Write-Host "   machine-learning, data-science, python, tensorflow" -ForegroundColor $Green
Write-Host "   pytorch, apache-spark, docker, power-bi, databricks" -ForegroundColor $Green
Write-Host "   business-intelligence, data-engineering, mlops" -ForegroundColor $Green
Write-Host ""
Write-Host "2. Habilitar GitHub Pages (opcional)" -ForegroundColor $Blue
Write-Host "3. Configurar protección de rama main" -ForegroundColor $Blue
Write-Host "4. Habilitar Discussions para la comunidad" -ForegroundColor $Blue
Write-Host ""
Write-Host "✅ Script completado!" -ForegroundColor $Green
Write-Host ""
