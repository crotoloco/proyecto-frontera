# GUÍA RÁPIDA - FRONTERA LIVING CENTER DE CONTROL

## ⚡ Inicio en 30 segundos

```powershell
# 1. Activar entorno
.\.venv\Scripts\Activate.ps1

# 2. Instalar deps (si no está)
pip install -r requirements.txt

# 3. Iniciar app
python centro_control\app.py

# 4. Abrir navegador
Start-Process "http://127.0.0.1:5000/login"

# 5. Login
# Usuario: admin
# Pass: admin
```

---

## 📍 URLs Principales

| URL | Descripción |
|-----|-------------|
| `http://127.0.0.1:5000/login` | Login |
| `http://127.0.0.1:5000/` | Upload + Preview |
| `http://127.0.0.1:5000/centro_control/history` | Historial de cargas |
| `http://127.0.0.1:5000/centro_control/alerts` | Alertas |
| `http://127.0.0.1:5000/centro_control/users` | Gestión usuarios (admin) |
| `http://127.0.0.1:5000/dashboard.html` | Dashboard de ventas |
| `http://127.0.0.1:5000/inventario.html` | Inventario |

---

## 🔧 Archivos Clave

| Archivo | Líneas | Qué Hace |
|---------|--------|----------|
| `centro_control/app.py` | 550 | Rutas Flask + lógica |
| `centro_control/db.py` | 250 | Base de datos SQLite |
| `centro_control/templates/*.html` | - | Templates HTML |
| `scripts/AUTOMATIZAR_TODO.py` | - | Procesa ventas |
| `scripts/generar_inventario_html.py` | - | Procesa inventario |
| `.env` | - | Variables de entorno (crear) |
| `requirements.txt` | - | Dependencias |

---

## 🚀 Workflow Típico

1. **Login** → `http://127.0.0.1:5000/login`
2. **Subir CSV** → Formulario en `/`
3. **Sistema detecta tipo** → VENTAS o INVENTARIO
4. **Ver preview** → Primeras 5 filas
5. **Procesar** → Ejecuta script
6. **Historial** → `/centro_control/history`
7. **Alertas** → `/centro_control/alerts`

---

## ⚠️ Problemas Comunes

### "No logro conectar"
```powershell
# Verifica que el entorno está activado
.venv\Scripts\Activate.ps1

# Verifica que las dependencias están instaladas
pip install -r requirements.txt

# Intenta iniciar de nuevo
python centro_control\app.py
```

### "ModuleNotFoundError"
```powershell
# Ejecuta DESDE la carpeta raíz del proyecto
cd C:\Users\USUARIO\Downloads\frontera_living_python
python centro_control\app.py

# NO desde dentro de centro_control/
```

### "Permission denied" en Windows
```powershell
# Permite scripts en PowerShell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

---

## 📝 Tareas Básicas

### Crear nuevo usuario
```powershell
python scripts\create_user.py --username juan --password secreto --admin
```

### Cambiar contraseña de admin
1. Login con admin/admin
2. Ir a `/centro_control/users`
3. Buscar "admin" y cambiar

### Limpiar archivos subidos
```powershell
Remove-Item centro_control/uploads/* -Force
```

### Resetear DB completamente
```powershell
Remove-Item centro_control/centro_control.db -Force
# Se recreará vacía al iniciar la app
```

---

## 🔐 Seguridad (IMPORTANTE)

⚠️ **Cambiar ANTES de producción:**

1. **Crear `.env`:**
   ```bash
   FLASK_SECRET_KEY=<generar-aleatorio>
   ADMIN_USER=admin
   ADMIN_PASS=<contraseña-fuerte>
   FLASK_DEBUG=False
   ```

2. **Generar clave aleatoria:**
   ```powershell
   python -c "import secrets; print(secrets.token_hex(32))"
   ```

3. **Agregar `@require_login` a rutas de upload** (en app.py)

4. **Crear `.gitignore`:** 
   ```
   centro_control/centro_control.db
   centro_control/uploads/
   .env
   ```

---

## 📊 DB SQLite

Ver contenido de la base de datos:
```powershell
sqlite3 centro_control/centro_control.db

# Comandos útiles:
SELECT * FROM upload_history;
SELECT * FROM execution_log;
SELECT * FROM alerts;
SELECT * FROM users;
.quit
```

---

## 🧪 Verificar que está todo bien

```powershell
# 1. Syntax OK
python -m py_compile centro_control\app.py

# 2. Imports OK
python -c "from centro_control import app; print('OK')"

# 3. Inicia sin errors
python centro_control\app.py
# Espera a ver: * Running on http://127.0.0.1:5000

# 4. Login funciona
# Abre http://127.0.0.1:5000/login

# 5. Upload funciona
# Sube un CSV de prueba
```

---

## 📞 Contacto/Help

Si algo no funciona:

1. **Revisar logs:** `python centro_control\app.py` (ver output)
2. **Ver traceback completo:** Copiar error y buscar en Google
3. **Revisar DB:** `sqlite3 centro_control/centro_control.db`
4. **Documentación:**
   - `PROYECTO_HANDOFF.md` - Documentación completa
   - `PROMPT_CONTINUACION.md` - Tareas a implementar
   - `centro_control/app.py` - Código comentado

---

**Versión:** 1.0 Beta  
**Fecha:** 2026-09-01  
**Estado:** Development (local)
