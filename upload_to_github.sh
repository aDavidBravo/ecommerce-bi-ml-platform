#!/bin/bash

# ==========================================
# Script Autom\u00e1tico para Subir Proyecto a GitHub
# E-Commerce BI/ML Platform
# ==========================================

set -e  # Exit on error

echo "=========================================="
echo "\ud83d\ude80 E-Commerce BI/ML Platform"
echo "Subida Autom\u00e1tica a GitHub"
echo "=========================================="
echo ""

# Colores para output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Variables
REPO_NAME="ecommerce-bi-ml-platform"
GITHUB_USER="aDavidBravo"
REPO_DESC="\ud83d\ude80 Enterprise BI & ML Platform for E-Commerce | Python, Scala, Spark, TensorFlow, PyTorch, Docker, Airflow, Power BI | 40+ Technologies"

# Verificar que estamos en el directorio correcto
if [ ! -f "README.md" ] || [ ! -f "docker-compose.yml" ]; then
    echo -e "${RED}\u274c Error: No estamos en el directorio del proyecto${NC}"
    echo "Por favor cd al directorio ecommerce-bi-ml-platform"
    exit 1
fi

echo -e "${BLUE}1. Verificando repositorio Git...${NC}"
if [ -d ".git" ]; then
    echo -e "${GREEN}\u2713 Repositorio Git encontrado${NC}"
else
    echo -e "${YELLOW}\u26a0\ufe0f  Inicializando repositorio Git...${NC}"
    git init
    git branch -M main
    echo -e "${GREEN}\u2713 Repositorio Git inicializado${NC}"
fi

echo ""
echo -e "${BLUE}2. Agregando archivos...${NC}"
git add -A
echo -e "${GREEN}\u2713 Archivos agregados${NC}"

echo ""
echo -e "${BLUE}3. Creando commit...${NC}"
git commit -m "Initial commit: E-Commerce BI/ML Platform

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
Lines of Code: 5000+" || echo "Ya existe un commit"

echo -e "${GREEN}\u2713 Commit creado${NC}"

echo ""
echo -e "${BLUE}4. Configurando remote de GitHub...${NC}"

# Eliminar remote si existe
git remote remove origin 2>/dev/null || true

# Agregar nuevo remote
git remote add origin https://github.com/${GITHUB_USER}/${REPO_NAME}.git
echo -e "${GREEN}\u2713 Remote configurado: https://github.com/${GITHUB_USER}/${REPO_NAME}.git${NC}"

echo ""
echo -e "${YELLOW}=========================================="
echo "\u26a0\ufe0f  PASO MANUAL REQUERIDO"
echo "==========================================${NC}"
echo ""
echo "Antes de continuar, necesitas:"
echo ""
echo -e "${BLUE}1. Ir a https://github.com/${GITHUB_USER}${NC}"
echo -e "${BLUE}2. Click en 'New repository' (bot\u00f3n verde)${NC}"
echo -e "${BLUE}3. Repository name: ${YELLOW}${REPO_NAME}${NC}"
echo -e "${BLUE}4. Description: ${NC}"
echo -e "   ${REPO_DESC}"
echo -e "${BLUE}5. Seleccionar: ${YELLOW}Public${NC}"
echo -e "${BLUE}6. ${RED}NO${NC} marcar 'Add a README file'${NC}"
echo -e "${BLUE}7. ${RED}NO${NC} agregar .gitignore${NC}"
echo -e "${BLUE}8. ${RED}NO${NC} agregar licencia${NC}"
echo -e "${BLUE}9. Click 'Create repository'${NC}"
echo ""
echo -e "${YELLOW}Una vez creado el repositorio, presiona ENTER para continuar...${NC}"
read -r

echo ""
echo -e "${BLUE}5. Subiendo a GitHub...${NC}"

# Intentar push
if git push -u origin main; then
    echo -e "${GREEN}\u2713 \u00a1Proyecto subido exitosamente!${NC}"
    echo ""
    echo -e "${GREEN}=========================================="
    echo "\u2705 \u00a1COMPLETADO!"
    echo "==========================================${NC}"
    echo ""
    echo -e "${BLUE}Tu proyecto est\u00e1 en:${NC}"
    echo -e "${GREEN}https://github.com/${GITHUB_USER}/${REPO_NAME}${NC}"
    echo ""
    echo -e "${YELLOW}Pr\u00f3ximos pasos recomendados:${NC}"
    echo -e "1. Agregar topics/tags en GitHub"
    echo -e "2. Configurar GitHub Pages (opcional)"
    echo -e "3. Agregar screenshots al README"
    echo -e "4. Habilitar GitHub Actions para CI/CD"
    echo ""
else
    echo ""
    echo -e "${RED}\u274c Error al subir a GitHub${NC}"
    echo ""
    echo -e "${YELLOW}Posibles soluciones:${NC}"
    echo ""
    echo -e "${BLUE}1. Verificar que creaste el repositorio en GitHub${NC}"
    echo -e "${BLUE}2. Si ya existe un repositorio con contenido:${NC}"
    echo "   git pull origin main --rebase"
    echo "   git push -u origin main"
    echo ""
    echo -e "${BLUE}3. Si tienes problemas de autenticaci\u00f3n:${NC}"
    echo "   Configura un Personal Access Token:"
    echo "   https://github.com/settings/tokens"
    echo "   Luego usa:"
    echo "   git remote set-url origin https://YOUR_TOKEN@github.com/${GITHUB_USER}/${REPO_NAME}.git"
    echo "   git push -u origin main"
    echo ""
    exit 1
fi

echo ""
echo -e "${BLUE}=========================================="
echo "Configuraci\u00f3n Adicional Recomendada"
echo "==========================================${NC}"
echo ""
echo -e "${YELLOW}En tu repositorio de GitHub:${NC}"
echo ""
echo -e "${BLUE}1. Agregar Topics (Etiquetas):${NC}"
echo "   - Click en el engranaje \u2699\ufe0f junto a 'About'"
echo "   - Agregar topics:"
echo "     machine-learning, data-science, python, tensorflow"
echo "     pytorch, apache-spark, docker, power-bi, databricks"
echo "     business-intelligence, data-engineering, mlops"
echo ""
echo -e "${BLUE}2. Configurar Descripci\u00f3n:${NC}"
echo "   - Click en 'Edit' junto al nombre del repositorio"
echo "   - Agregar website (si tienes)"
echo ""
echo -e "${BLUE}3. Proteger la rama main:${NC}"
echo "   - Settings \u2192 Branches \u2192 Branch protection rules"
echo "   - Require pull request reviews"
echo ""
echo -e "${BLUE}4. Habilitar Discussions:${NC}"
echo "   - Settings \u2192 Features \u2192 Discussions"
echo ""

echo ""
echo -e "${GREEN}\u2705 \u00a1Script completado!${NC}"
echo ""
