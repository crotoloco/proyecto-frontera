# PROMPT PARA CONTINUACIÓN DEL PROYECTO

> **Para:** Otro dev / Visual Studio instance  
> **Proyecto:** Frontera Living - Centro de Control  
> **Estado actual:** 75% funcional, listo para hardening + mejoras

---

## 🎯 Objetivo General

Hacer que "Frontera Living - Centro de Control" sea una **aplicación web production-ready** que permita a empleados de la compañía:

1. Subir archivos CSV/XLSX exportados desde Odoo (sin API)
2. Procesar automáticamente (detectar si es ventas o inventario)
3. Generar dashboards y reportes
4. Ver historial de cargas y alertas
5. Todo desde un navegador, sin necesidad de CLI

**Situación actual:** El backend está 95% hecho. La UI está funcional pero necesita:
- Seguridad endurecida (credenciales, auth en rutas)
- UI mejorada (estilos, responsividad)
- Funcionalidades avanzadas (alertas, comparaciones)

---

## 📋 Quickstart

### 1. Preparación
```powershell
cd C:\Users\USUARIO\Downloads\frontera_living_python
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 2. Iniciar la app
```powershell
python centro_control\app.py
```

### 3. Abrir en navegador
```
http://127.0.0.1:5000/login
```

Credenciales: `admin` / `admin`

### 4. Probar flujo básico
1. Navega a `/centro_control` (upload form)
2. Sube un CSV de ventas o inventario
3. Sistema detecta tipo automáticamente
4. Haz clic en "Procesar"
5. Espera a que se generen los reportes
6. Ve a `/centro_control/history` para ver el historial

---

## 🔴 Tareas URGENTES (Antes de producción)

### Tarea 1: Seguridad Básica (45 min)

**Archivos a editar:**
- `centro_control/app.py` (líneas 67-73)
- `.env` (crear desde `.env.example`)

**Pasos:**

1. Genera una clave secreta:
   ```powershell
   python -c "import secrets; print(secrets.token_hex(32))"
   ```

2. Crea `.env` en la raíz:
   ```bash
   FLASK_SECRET_KEY=<tu-clave-generada>
   ADMIN_USER=admin
   ADMIN_PASS=<contraseña-segura>
   FLASK_DEBUG=False
   FLASK_ENV=production
   ```

3. Modifica `app.py` para leer `.env`:
   ```python
   from dotenv import load_dotenv
   load_dotenv()
   
   app.config['SECRET_KEY'] = getenv('FLASK_SECRET_KEY')
   app.config['ADMIN_USER'] = getenv('ADMIN_USER', 'admin')
   app.config['ADMIN_PASS'] = getenv('ADMIN_PASS', 'admin')
   ```

4. Borra los warnings de credenciales por defecto (líneas 70-72)

**Verificación:**
```powershell
python centro_control\app.py
# No debe mostrar warnings sobre credenciales por defecto
```

---

### Tarea 2: Proteger Rutas (30 min)

**Archivos a editar:**
- `centro_control/app.py` (rutas `index()`, `procesar()`)

**Cambios:**

Agrega `@require_login` a estas rutas:
```python
@app.route('/', methods=['GET', 'POST'])
@require_login  # ← AGREGAR ESTA LÍNEA
def index():
    ...

@app.post('/procesar')
@require_login  # ← AGREGAR ESTA LÍNEA
def procesar():
    ...
```

**Por qué:** Actualmente cualquiera puede subir y procesar archivos sin autenticarse.

**Testing:**
1. Intenta acceder a `http://127.0.0.1:5000/` sin estar logueado
2. Debe redirigirse a `/login`
3. Después de loguear, debe permitir upload

---

### Tarea 3: Gitignore Correcto (10 min)

**Archivo:** `.gitignore`

Agrega:
```
centro_control/centro_control.db
centro_control/uploads/
*.db
.env
__pycache__/
.venv/
.vs/
venv/
*.pyc
*.pyo
```

**Por qué:** Evita que se suban:
- Base de datos con datos sensibles
- Archivos subidos (temporary)
- Credenciales en `.env`

---

## 🟡 Tareas ALTAS PRIORIDAD (1-2 semanas)

### Tarea 4: Mejorar UI (2-3 horas)

**Archivos a editar:**
- `centro_control/templates/index.html`
- `centro_control/templates/history.html`
- `centro_control/templates/history_detail.html`
- `centro_control/templates/login.html`

**Cambios recomendados:**

1. Agregar Bootstrap 5 CDN:
   ```html
   <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
   <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
   ```

2. Crear un `base.html` para heredar estructura común

3. Mejorar formulario de upload con:
   - Drag & drop
   - Validación client-side
   - Spinner mientras procesa
   - Toast notifications para errores

4. Tabla de historial:
   - Filtros por fecha, tipo, estado
   - Búsqueda por nombre
   - Ordenamiento por columnas

**Testing:**
- Verificar en mobile (responsive)
- Verificar en navegadores (Chrome, Firefox, Edge)

---

### Tarea 5: Alertas Mejoradas (1-2 horas)

**Archivos a editar:**
- `centro_control/app.py` (función `evaluate_alerts_for_upload()`)
- `centro_control/templates/alerts.html`

**Cambios:**

1. Mejorar heurística de "período anterior":
   - Agrupar por semana/mes en lugar de por último upload
   - Comparar contra promedio histórico

2. Agregar tipos de alertas nuevas:
   - Cambio de precio (si hay columna)
   - Nuevos clientes
   - Clientes que desaparecieron

3. UI: Alertas con badges de severidad:
   - 🔴 CRÍTICA (drop >50%)
   - 🟡 ADVERTENCIA (drop 20-50%)
   - 🟢 INFO (cambios menores)

**Testing:**
```powershell
# Subir archivo 1, obtener total = 1000
# Subir archivo 2, obtener total = 700 (drop de 30%)
# Debe generar alerta de "Caída de ventas"
```

---

### Tarea 6: Dashboard Ejecutivo (2-3 horas)

**Archivos a crear:**
- `centro_control/templates/dashboard.html` (NUEVA - NO confundir con `/dashboard.html` legacy)

**Contenido:**

Una página con:
- Último upload (archivo, tipo, fecha, estado)
- Última alerta crítica
- Estadísticas: Total uploads, Success rate, Errores recientes
- Links rápidos a: upload, historial, alertas
- Timeline de últimas 5 ejecuciones

```html
@app.route('/centro_control/dashboard')
@require_login
def centro_control_dashboard():
    # Obtener datos del DB
    last_upload = db.get_uploads(1)[0] if db.get_uploads(1) else None
    alerts = db.get_unacknowledged_alerts(1)
    stats = {
        'total_uploads': len(db.get_uploads(9999)),
        'total_errors': ...,
        'last_7_days': ...,
    }
    return render_template('dashboard.html', last_upload=last_upload, alerts=alerts, stats=stats)
```

---

## 🟢 Tareas MEDIAS (Cuando tengas tiempo)

### Tarea 7: Exportar Historial a CSV

Agregar botón en `/centro_control/history` que exporte todos los uploads con sus metadatos a CSV.

### Tarea 8: Gráficos de Tendencias

Usar Chart.js para mostrar:
- Total de ventas por día/semana
- Cantidad de productos en stock
- Tasa de error por procesamiento

### Tarea 9: Historial de Alertas Completo

Agregar ruta `/centro_control/alerts/history` que muestre:
- Todas las alertas (ack=0 y ack=1)
- Filtro por tipo, severidad, fecha
- Exportar a PDF

---

## 🧪 Testing Checklist (Antes de cualquier push)

```powershell
# 1. Syntax
python -m py_compile centro_control\app.py
python -m py_compile centro_control\db.py

# 2. Imports
python -c "from centro_control import app, db; print('OK')"

# 3. Start server
python centro_control\app.py
# Verifica que no haya WARNINGS sobre credenciales por defecto

# 4. Login
# Intenta: http://127.0.0.1:5000/login (debe funcionar)

# 5. Upload + Process
# Sube test_ventas.csv → Debe detectar VENTAS
# Sube test_inventario.csv → Debe detectar INVENTARIO

# 6. History
# Verifica que ambos uploads aparezcan en /centro_control/history

# 7. Auth
# Intenta logout
# Intenta acceder a /centro_control/history sin login
# Debe redirigir a /login

# 8. Alerts
# Sube archivo con ventas totales = 1000
# Sube archivo con ventas totales = 600 (drop 40%)
# Debe generar alerta en /centro_control/alerts
```

---

## 📂 Estructura de Carpetas (Referencia)

```
frontera_living_python/
├── centro_control/           # ← APLICACIÓN PRINCIPAL
│   ├── app.py               # 550 líneas - Rutas Flask
│   ├── db.py                # 250 líneas - SQLite layer
│   ├── centro_control.db    # (auto-creado)
│   ├── uploads/             # Archivos subidos (temporal)
│   └── templates/           # HTML templates
├── scripts/                 # Scripts originales (REUTILIZAR)
│   ├── AUTOMATIZAR_TODO.py
│   ├── generar_inventario_html.py
│   └── ...
├── data/                    # CSVs de entrada
├── reports/                 # Reportes generados
├── .env                     # Variables de entorno (NO commitear)
├── .env.example             # Template (sí commitear)
├── requirements.txt         # Dependencias
├── PROYECTO_HANDOFF.md      # Este archivo
└── dashboard.html           # Legacy (servido por Flask ahora)
```

---

## 🔧 Variables Importantes en app.py

| Variable | Línea | Propósito |
|----------|-------|----------|
| `UPLOAD_DIR` | 51 | Carpeta de archivos subidos |
| `app.config['SECRET_KEY']` | 67 | Clave secreta (debe ser env var) |
| `app.config['ADMIN_USER']` | 70 | Usuario por defecto |
| `app.config['ADMIN_PASS']` | 71 | Contraseña por defecto |
| `ALLOWED_EXTENSIONS` | 50 | Formatos permitidos (.csv, .xls, .xlsx) |
| `MAX_CONTENT_LENGTH` | 68 | Tamaño máximo de upload (25MB) |

---

## 🐛 Debugging Tips

### "No se puede conectar a la DB"
```powershell
# Verifica que el archivo existe y es accesible
ls -la centro_control/centro_control.db
# Si no existe, Flask lo creará automáticamente en el primer run
```

### "ModuleNotFoundError: No module named 'centro_control'"
```powershell
# Ejecuta desde la carpeta raíz (frontera_living_python)
cd C:\Users\USUARIO\Downloads\frontera_living_python
python centro_control\app.py  # Correcto

# NO hagas esto desde dentro de centro_control/:
cd centro_control
python app.py  # ❌ Incorrecto
```

### "CSRF token missing"
```python
# Verifica que el template incluya:
<form method="POST">
    {{ csrf_token() }}
    ...
</form>
```

### "encoding errors en Windows"
```python
# Esto ya está implementado en procesar():
env.update({'PYTHONIOENCODING': 'utf-8', 'PYTHONUTF8': '1'})
```

---

## 📞 Rutas API Completas

### Autenticación
- `GET/POST /login` - Formulario + validación
- `GET /logout` - Cierre de sesión

### Upload & Processing
- `GET/POST /` - Subir archivo + preview
- `GET/POST /centro_control` - Alias
- `POST /procesar` - Ejecutar script

### Historial
- `GET /centro_control/history` - Lista de uploads
- `GET /centro_control/history/<id>` - Detalle + logs
- `POST /centro_control/history/<id>/delete` - Eliminar
- `POST /centro_control/history/<id>/reprocess` - Reprocesar
- `GET /centro_control/uploads/<filename>` - Descargar

### Alertas & Admin
- `GET /centro_control/alerts` - Centro de alertas
- `GET /centro_control/users` - Gestión de usuarios
- `GET /centro_control/dashboard` - Dashboard ejecutivo (nueva)

### Legacy (Archivos estáticos)
- `GET /dashboard.html` - Ventas (con protección login)
- `GET /inventario.html` - Inventario
- `GET /monitor.html` - Monitor
- `GET /reports/<file>` - Reportes

---

## 💡 Tips & Trucos

### Crear usuario desde CLI
```powershell
python scripts\create_user.py --username juan --password secreto123 --admin
```

### Generar hash de contraseña PBKDF2
```powershell
python -c "from werkzeug.security import generate_password_hash; print(generate_password_hash('micontraseña'))"
```

### Ver contenido de DB en terminal
```powershell
sqlite3 centro_control/centro_control.db
> SELECT * FROM upload_history;
> SELECT * FROM alerts;
> .quit
```

### Limpiar uploads temporales
```powershell
Remove-Item centro_control/uploads/* -Force
```

### Resetear DB completamente
```powershell
Remove-Item centro_control/centro_control.db -Force
# La próxima vez que inicie app.py, se recreará vacía
```

---

## 📊 Dependencias Principales

| Paquete | Versión | Uso |
|---------|---------|-----|
| Flask | >=3.0,<4.0 | Web framework |
| Pandas | >=2.0,<3.0 | Lectura/análisis de CSV/Excel |
| Flask-WTF | >=1.1.1 | Protección CSRF |
| Flask-Login | >=0.6.0 | Autenticación |
| python-dotenv | >=1.0,<2.0 | Variables de entorno |
| openpyxl | >=3.1,<4.0 | Lectura XLSX |
| xlrd | >=2.0.1,<3.0 | Lectura XLS |

Instalar:
```powershell
pip install -r requirements.txt
```

---

## 🎓 Flujo de Datos

```
CSV/XLSX del usuario
        ↓
   [Subir en /]
        ↓
   Guardar en uploads/ con UUID
        ↓
   Leer con Pandas
        ↓
   Detectar tipo (VENTAS/INVENTARIO)
        ↓
   Validar: columnas + contenido
        ↓
   Registrar en upload_history (DB)
        ↓
   [Procesar] → ejecutar AUTOMATIZAR_TODO.py o generar_inventario_html.py
        ↓
   Capturar stdout/stderr → execution_log (DB)
        ↓
   Evaluar alertas → alerts (DB)
        ↓
   Actualizar dashboard.html o inventario.html
        ↓
   [Ver historial] → /centro_control/history
        ↓
   [Ver alertas] → /centro_control/alerts
```

---

## ✅ Conclusión

**Estado actual:** La app está 75% funcional y lista para hardening.

**Siguiente acción recomendada:**

1. Completa las tareas **URGENTES** (Seguridad + Auth)
2. Luego las tareas **ALTAS** (UI + Alertas)
3. Finalmente las tareas **MEDIAS** (Dashboard + Reportes)

**Cada tarea debe incluir:**
- Código implementado
- Testing verificado
- Commit a Git con mensaje claro

**Tiempo estimado:**
- Urgentes: 1 hora
- Altas: 4-5 horas
- Medias: 3-4 horas
- Total: ~9 horas para producción ready

---

**¿Dudas o problemas? Revisá:**
1. [PROYECTO_HANDOFF.md](PROYECTO_HANDOFF.md) - Documentación técnica completa
2. `centro_control/app.py` - Código comentado
3. `centro_control/db.py` - Schema y funciones

¡Éxito! 🚀
