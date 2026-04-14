#!/usr/bin/env python3
"""
Script para subir todos los archivos del proyecto a GitHub
"""
import os
import subprocess
import sys

def main():
    # Archivos a subir (todos excepto los scripts de upload)
    files_patterns = [
        ".gitignore",
        "LICENSE", 
        "QUICKSTART.md",
        "PROJECT_SUMMARY.md",
        ".env.example",
        "requirements.txt",
        "docker-compose.yml",
        "dashboards/powerbi/POWER_BI_GUIDE.md",
        "dashboards/streamlit/app.py",
        "infrastructure/docker/Dockerfile.*",
        "pipelines/airflow/dags/*.py",
        "src/python/machine_learning/**/*.py",
        "src/sql/ddl/*.sql"
    ]
    
    # Configuración
    repo = "ecommerce-bi-ml-platform"
    owner = "aDavidBravo"
    branch = "main"
    
    print("="*60)
    print("Subiendo proyecto completo a GitHub")
    print("="*60)
    print(f"Repositorio: {owner}/{repo}")
    print(f"Rama: {branch}")
    print()
    
    # Verificar que git está inicializado
    if not os.path.exists(".git"):
        print("Inicializando repositorio Git...")
        subprocess.run(["git", "init"], check=True)
        subprocess.run(["git", "branch", "-M", "main"], check=True)
    
    # Agregar remote si no existe
    try:
        subprocess.run(["git", "remote", "get-url", "origin"], 
                      capture_output=True, check=True)
    except subprocess.CalledProcessError:
        print("Agregando remote origin...")
        remote_url = f"https://github.com/{owner}/{repo}.git"
        subprocess.run(["git", "remote", "add", "origin", remote_url], check=True)
    
    # Add all files
    print("Agregando archivos...")
    subprocess.run(["git", "add", "-A"], check=True)
    
    # Commit
    commit_msg = """Complete E-Commerce BI/ML Platform

- Python ML modules (Forecasting, Clustering)
- Airflow DAG for ETL pipeline  
- Docker Compose infrastructure (15+ services)
- Data Warehouse SQL schemas
- Power BI documentation (3 dashboards)
- Streamlit interactive dashboard
- Complete requirements.txt
- Production-ready configuration

Stack: Python, Scala, SQL, Spark, TensorFlow, PyTorch, Docker, Airflow, Power BI
Technologies: 40+
Level: Senior/Expert Data Scientist"""
    
    try:
        subprocess.run(["git", "commit", "-m", commit_msg], check=True)
        print("✓ Commit creado")
    except subprocess.CalledProcessError:
        print("⚠ No hay cambios para commit (ya está actualizado)")
    
    # Push
    print("\nSubiendo a GitHub...")
    try:
        result = subprocess.run(["git", "push", "-u", "origin", "main"], 
                              capture_output=True, text=True, check=True)
        print("✓ Proyecto subido exitosamente!")
        print()
        print("="*60)
        print("¡COMPLETADO!")
        print("="*60)
        print(f"\nTu proyecto está en:")
        print(f"https://github.com/{owner}/{repo}")
        print()
    except subprocess.CalledProcessError as e:
        print("❌ Error al subir:", e.stderr)
        print("\nIntenta manualmente:")
        print(f"git push -u origin main")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
