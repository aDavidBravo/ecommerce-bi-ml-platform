# 📤 Instrucciones para Subir el Proyecto a GitHub

## Opción 1: Crear Repositorio desde GitHub Web (Recomendado)

### Paso 1: Crear Repositorio en GitHub.com

1. Ve a https://github.com/aDavidBravo
2. Click en el botón verde "New" (o "Nuevo repositorio")
3. Configuración del repositorio:
   - **Repository name**: `ecommerce-bi-ml-platform`
   - **Description**: 🚀 Enterprise BI & ML Platform for E-Commerce | Python, Scala, Spark, TensorFlow, PyTorch, Docker, Airflow, Power BI | 40+ Technologies
   - **Public** (seleccionado)
   - **NO** marcar "Add a README file"
   - **NO** marcar ".gitignore"  
   - **NO** seleccionar licencia
4. Click en "Create repository"

### Paso 2: Descargar y Descomprimir el Proyecto

```bash
# Descomprimir el archivo que descargaste
tar -xzf ecommerce-bi-ml-platform-v1.0.tar.gz
cd ecommerce-bi-ml-platform
```

### Paso 3: Conectar con GitHub y Subir

```bash
# Verificar que estás en el directorio del proyecto
pwd

# Agregar el remote de GitHub (reemplaza con tu URL real)
git remote add origin https://github.com/aDavidBravo/ecommerce-bi-ml-platform.git

# Verificar remote
git remote -v

# Push al repositorio
git push -u origin main
```

**¡Listo!** Tu proyecto debería estar en https://github.com/aDavidBravo/ecommerce-bi-ml-platform

---

## Opción 2: Usar GitHub CLI (si lo tienes instalado)

```bash
# Autenticarte (solo la primera vez)
gh auth login

# Crear repositorio directamente desde terminal
gh repo create ecommerce-bi-ml-platform --public --description "🚀 Enterprise BI & ML Platform for E-Commerce | Python, Scala, Spark, TensorFlow, PyTorch, Docker, Airflow, Power BI | 40+ Technologies"

# Push
git push -u origin main
```

---

## Opción 3: Subir Archivos Manualmente desde GitHub Web

Si tienes problemas con git, puedes subir los archivos uno por uno desde la interfaz web:

1. Ve a tu repositorio nuevo en GitHub
2. Click en "uploading an existing file"
3. Arrastra todos los archivos del proyecto
4. Commit changes

**Nota**: Esta opción es menos ideal para proyectos grandes, pero funciona.

---

## Verificar que Todo Está Bien

Una vez subido, verifica:

1. ✅ README.md se muestra correctamente
2. ✅ Todos los directorios están presentes
3. ✅ Los archivos .py, .sql, .yml están visibles
4. ✅ El .gitignore está funcionando (no deberías ver archivos .env o __pycache__)

---

## Personalizar el Repositorio

### Agregar Topics/Tags

En tu repositorio de GitHub:
1. Click en el engranaje ⚙️ junto a "About"
2. Agregar topics:
   - `machine-learning`
   - `data-science`
   - `python`
   - `tensorflow`
   - `pytorch`
   - `apache-spark`
   - `docker`
   - `power-bi`
   - `business-intelligence`
   - `data-engineering`
   - `mlops`
   - `databricks`

### Habilitar GitHub Pages (Opcional)

Si quieres documentación web:
1. Settings → Pages
2. Source: Deploy from branch
3. Branch: main, folder: /docs

---

## Solución de Problemas

### Error: "remote origin already exists"

```bash
git remote remove origin
git remote add origin https://github.com/aDavidBravo/ecommerce-bi-ml-platform.git
```

### Error: "Permission denied"

```bash
# Usar HTTPS con token
git remote set-url origin https://YOUR_TOKEN@github.com/aDavidBravo/ecommerce-bi-ml-platform.git

# O configurar SSH
ssh-keygen -t ed25519 -C "tu-email@example.com"
# Agregar la clave pública a GitHub Settings → SSH Keys
```

### Error: "Repository not found"

Verifica que el nombre del repositorio sea exactamente: `ecommerce-bi-ml-platform`

---

## Próximos Pasos

Una vez subido el proyecto:

1. ✅ Agregar screenshot del dashboard Streamlit al README
2. ✅ Configurar GitHub Actions para CI/CD (opcional)
3. ✅ Agregar badges de build status
4. ✅ Crear un GitHub Project board para tracking
5. ✅ Habilitar Discussions para la comunidad

---

## Comandos Útiles de Git

```bash
# Ver estado
git status

# Ver historial
git log --oneline

# Ver archivos ignorados
git ls-files --others --ignored --exclude-standard

# Agregar más archivos
git add .
git commit -m "Add new features"
git push

# Crear nueva rama
git checkout -b feature/new-model
git push -u origin feature/new-model
```

---

**¿Necesitas ayuda?** Abre un issue en el repositorio o contacta vía email.
