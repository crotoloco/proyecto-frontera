# Frontera Living - Centro de Control

## Resumen Ejecutivo

**Proyecto:** Aplicación web Flask para gestión de automatización de ventas e inventarios sin necesidad de acceso API a Odoo.

**Estado:** ~75% funcional. Backend completamente operativo; UI pulida pero con oportunidades de mejora.

**Tecnología:**
- **Backend:** Flask 3.1.3 + Python 3.10+
- **Base de datos:** SQLite (`centro_control/centro_control.db`)
- **Procesamiento de datos:** Pandas 2.3.3
- **Autenticación:** Flask-Login + Flask-WTF (CSRF)
- **Archivos soportados:** CSV, XLS, XLSX

**URL principal:** `http://127.0.0.1:5000/login`

---

## Estructura del Proyecto

```
frontera_living_python/
├── centro_control/                  # APLICACIÓN PRINCIPAL (Flask web)
│   ├── app.py                       # 550 líneas - Rutas y lógica principal
│   ├── db.py                        # 250 líneas - Capa de persistencia SQLite
│   ├── centro_control.db            # Base de datos (auto-creada)
│   ├── uploads/                     # Directorio de archivos subidos (temporal)
│   ├── templates/                   # HTML templates Jinja2
│   │   ├── login.html              # Formulario de autenticación
│   │   ├── index.html              # Upload + detección + preview
│   │   ├── history.html            # Lista de todas las cargas
│   │   ├── history_detail.html     # Detalle + logs + opciones reprocess/delete
│   │   ├── alerts.html             # Centro de alertas
│   │   ├── users.html              # Gestión de usuarios (admin only)
│   │   └── change_password.html    # Cambiar contraseña
│   ├── README.md
│   └── __init__.py
├── scripts/                         # SCRIPTS ORIGINALES (reutilizados)
│   ├── AUTOMATIZAR_TODO.py         # Procesa ventas → dashboard.html
│   ├── generar_inventario_html.py  # Procesa inventario → inventario.html
│   ├── automatizar_cada_15_minutos.py  # Scheduler CLI
│   ├── create_user.py              # Crear usuarios desde CLI
│   ├── generate_admin_hash.py      # Generar hash de contraseña
│   └── ... (otros scripts de análisis y monitoreo)
├── data/                            # Archivos CSV de entrada/exportados desde Odoo
│   ├── Orden de venta (sale.order).csv
│   ├── Producto (product.template).csv
│   └── ventas.json
├── reports/                         # Reportes generados
│   ├── analisis_ventas_completo.csv
│   ├── DATOS_ESTRUCTURADOS.json
│   ├── REPORTE_EJECUTIVO.txt
│   └── ...
├── dashboard.html                  # Dashboard de ventas (legacy, ahora servido por Flask)
├── inventario.html                 # Vista de inventario (legacy)
├── monitor.html                    # Monitor de estado (legacy)
├── requirements.txt                # Dependencias Python
├── .env                            # Variables de entorno (desarrollo)
├── .env.example                    # Plantilla .env
└── README.md                       # Documentación general

```

---

## Funcionalidades Implementadas

### 1. Autenticación (Login)
- Ruta: `/login` (GET/POST)
- Credenciales por defecto: `admin` / `admin`
- Integración con SQLite table `users`
- Soporte para hash pbkdf2 o plaintext (configurable)
- Logout: `/logout`
- CSRF protection habilitado

### 2. Subida y Detección de Archivos
- Ruta: `/` o `/centro_control` (GET/POST)
- Formatos: `.csv`, `.xls`, `.xlsx`
- Detección automática de tipo:
  - **VENTAS:** si contiene columnas `cliente`, `vendedor`, `total`, `estado` (3 de 4)
  - **INVENTARIO:** si contiene `nombre`, `cantidad a la mano`, `cantidad pronosticada` (2 de 3)
- Preview: primeras 5 filas en tabla HTML
- Validación: extensión, contenido, columnas requeridas
- Almacenamiento temporal en `centro_control/uploads/` con UUID
- Registro inmediato en tabla `upload_history`

### 3. Procesamiento y Ejecución
- Ruta: `/procesar` (POST)
- Llama a scripts existentes:
  - VENTAS → `scripts/AUTOMATIZAR_TODO.py`
  - INVENTARIO → `scripts/generar_inventario_html.py`
- Captura stdout/stderr/returncode en tabla `execution_log`
- Redacta credenciales de logs; trunca si > 10KB
- Registra alertas automáticas después de procesar
- Manejo de UTF-8 en Windows (PYTHONIOENCODING)

### 4. Historial de Cargas
- Ruta: `/centro_control/history` (GET, protegida)
- Tabla con: ID (linked), Fecha, Archivo, Tipo, Filas, Columnas, Errores
- Paginación: máx 200 registros por defecto
- Links a detalle de cada carga
- Muestra alertas no confirmadas asociadas

### 5. Detalle de Carga
- Ruta: `/centro_control/history/<id>` (GET, protegida)
- Metadatos: nombre, tipo, cantidad de registros/columnas, errores
- Info del archivo: tamaño, fecha última modificación
- Botón **Descargar** original (ruta segura, con log de auditoría)
- Botón **Reprocesar** (re-ejecuta script, crea nuevo log)
- Botón **Eliminar** (con confirmación; borra archivo, logs, alertas)
- Historial de ejecuciones: stdout/stderr/returncode por intento
- Auditoría de descargas: IP, User-Agent, timestamp

### 6. Centro de Alertas
- Ruta: `/centro_control/alerts` (GET, protegida)
- Tabla: ID, Upload, Tipo, Mensaje, Valor, Comparado Con, Timestamp
- Estados: `ack=0` (no leído), `ack=1` (confirmado)
- Tipos de alertas generadas automáticamente:
  - **Archivo inválido:** columnas faltantes o vacío
  - **Error de procesamiento:** returncode != 0
  - **Caída de ventas:** > 20% vs. período anterior
  - **Aumento excepcional:** > 50% vs. período anterior
  - **Concentración de clientes:** top cliente > 60% del total
  - **Productos sin stock:** cantidad <= 0

### 7. Gestión de Usuarios
- Ruta: `/centro_control/users` (GET, admin only)
- Crear usuarios: vía CLI `scripts/create_user.py` o panel web
- Roles: `is_admin = 1/0`
- Cambiar contraseña: `/centro_control/users/<username>/change-password`
- Eliminar usuario: admin only

### 8. Servicio de Archivos Legacy
- `/dashboard.html` → sirve dashboard de ventas (con protección login)
- `/inventario.html` → sitio inventario (sin protección actualmente)
- `/monitor.html` → monitor de estado
- `/reports/<filename>` → reportes generados

---

## Schema de Base de Datos SQLite

### Tabla: `upload_history`
| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | INTEGER PK | Auto-incremental |
| `nombre_original` | TEXT | Nombre del archivo subido |
| `nombre_guardado` | TEXT | UUID-based filename en uploads/ |
| `tipo` | TEXT | VENTAS / INVENTARIO / NULL |
| `filas` | INTEGER | Rows en el DataFrame |
| `columnas` | INTEGER | Cols en el DataFrame |
| `errores` | TEXT | CSV de errores de validación |
| `timestamp` | TEXT | ISO 8601 UTC |

### Tabla: `execution_log`
| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | INTEGER PK | Auto-incremental |
| `upload_id` | INTEGER FK | Referencia a upload_history |
| `stdout` | TEXT | Salida estándar (truncado a 10KB) |
| `stderr` | TEXT | Error estándar (redactado, truncado) |
| `returncode` | INTEGER | Exit code del subprocess |
| `timestamp` | TEXT | ISO 8601 UTC |

### Tabla: `users`
| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | INTEGER PK | Auto-incremental |
| `username` | TEXT UNIQUE | Login del usuario |
| `password_hash` | TEXT | pbkdf2 o plaintext |
| `is_admin` | INTEGER | 1 = admin, 0 = viewer |

### Tabla: `alerts`
| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | INTEGER PK | Auto-incremental |
| `upload_id` | INTEGER FK | Referencia a upload_history |
| `tipo_alerta` | TEXT | Caída de ventas, Error de procesamiento, etc. |
| `mensaje` | TEXT | Descripción humana |
| `valor` | TEXT | Métrica (ej: -25.5 para -25.5%) |
| `comparado_con` | TEXT | ID del upload anterior comparado |
| `timestamp` | TEXT | ISO 8601 UTC |
| `ack` | INTEGER | 0 = no leído, 1 = confirmado |

### Tabla: `download_log`
| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | INTEGER PK | Auto-incremental |
| `upload_id` | INTEGER FK | Referencia a upload_history |
| `filename` | TEXT | Nombre del archivo descargado |
| `client_ip` | TEXT | IP del cliente |
| `user_agent` | TEXT | Browser info |
| `timestamp` | TEXT | ISO 8601 UTC |

---

## Cómo Iniciar la Aplicación

### Prerequisitos
- Python 3.10+
- Virtual environment (`.venv/`) ya creado
- Dependencias instaladas (`pip install -r requirements.txt`)

### Pasos de Inicio

1. **Activar entorno virtual** (PowerShell):
   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```

2. **Iniciar servidor Flask**:
   ```powershell
   python centro_control\app.py
   ```
   
   Verá algo como:
   ```
   WARNING: No se estableció FLASK_SECRET_KEY; se usa valor por defecto. No usar en producción.
   WARNING: Se están usando credenciales por defecto (admin/admin). No usar en producción.
    * Running on http://127.0.0.1:5000
   Press CTRL+C to quit
   ```

3. **Abrir en navegador**:
   ```
   http://127.0.0.1:5000/login
   ```

4. **Credenciales iniciales**:
   - Usuario: `admin`
   - Contraseña: `admin`

### Crear un nuevo usuario (desde CLI)
```powershell
python scripts\create_user.py --username john --password secretpassword --admin
```

---

## Flujo de Trabajo Típico

1. **Login** → http://127.0.0.1:5000/login
2. **Subir archivo** → formulario en `/centro_control`
3. **Sistema detecta tipo** → VENTAS o INVENTARIO
4. **Preview de datos** → primeras 5 filas
5. **Procesar** → ejecuta script correspondiente
6. **Resultado** → dashboard.html o inventario.html actualizado
7. **Historial** → `/centro_control/history` (todos los uploads)
8. **Alertas** → `/centro_control/alerts` (anomalías detectadas)

---

## Rutas Protegidas vs. Públicas

| Ruta | Método | Protección | Descripción |
|------|--------|-----------|-------------|
| `/login` | GET/POST | ❌ Pública | Formulario de login |
| `/logout` | GET | ⚠️ Session | Cierre de sesión |
| `/` | GET/POST | ❌ Pública | Upload + preview |
| `/centro_control` | GET/POST | ❌ Pública | Alias de `/` |
| `/procesar` | POST | ❌ Pública | Procesar archivo |
| `/centro_control/history` | GET | ✅ Login | Historial de cargas |
| `/centro_control/history/<id>` | GET | ✅ Login | Detalle de carga |
| `/centro_control/history/<id>/delete` | POST | ✅ Login | Eliminar carga |
| `/centro_control/history/<id>/reprocess` | POST | ✅ Login | Reprocesar |
| `/centro_control/uploads/<filename>` | GET | ✅ Login | Descargar archivo |
| `/centro_control/alerts` | GET | ✅ Login | Ver alertas |
| `/centro_control/users` | GET | ✅ Admin | Gestión usuarios |
| `/dashboard.html` | GET | ✅ Login | Dashboard ventas |
| `/inventario.html` | GET | ❌ Pública | Inventario |
| `/monitor.html` | GET | ❌ Pública | Monitor |
| `/reports/<file>` | GET | ❌ Pública | Reportes |

---

## Problemas Conocidos y Limitaciones

### 🔴 Críticos
1. **Credenciales hardcodeadas:** Usuario/pass por defecto son `admin/admin`
   - **Fix:** Usar variables de entorno `ADMIN_USER`, `ADMIN_PASS`, `FLASK_SECRET_KEY`
   - **Ref:** app.py líneas 67-73

2. **Debug mode (debug=False actualmente):** Está apagado; bien.
   - **Issue:** Pero `FLASK_SECRET_KEY` aún está hardcodeada
   - **Fix:** Ver punto anterior

3. **Algunas rutas no tienen @require_login:**
   - `/` (upload) - accesible públicamente
   - `/procesar` - accesible públicamente
   - `/inventario.html` - accesible públicamente
   - **Riesgo:** Cualquiera puede subir y procesar archivos

### 🟡 Moderados
1. **Validación de ruta incompleta:** `/centro_control/uploads/<nombre>` tiene verificación de path traversal, pero podría ser más robusta
   - **Ref:** app.py línea ~560

2. **No hay rate limiting:** Una persona podría subir 1000 archivos en segundos
   - **Fix:** Implementar Flask-Limiter

3. **Logs guardados completos:** stdout/stderr se truncan a 10KB pero podrían contener datos sensibles
   - **Fix:** Redacción automática (ya parcialmente implementada)

4. **Comparación de períodos (alerts):** La lógica assume que "período anterior" = "último upload del mismo tipo"
   - **Issue:** No agrupa por rango de fechas real
   - **Fix:** Implementar agrupación por semana/mes

### 🟢 Menores
1. **Templates básicos:** Funcionales pero sin estilos refinados
   - **Fix:** Agregar Bootstrap o Tailwind

2. **No hay búsqueda en historial:** Solo ve últimos 200 registros
   - **Fix:** Agregar filtro por fecha/tipo

3. **Alertas solo de no-confirmadas:** No hay historial de alertas pasadas
   - **Fix:** Agregar vista de todas las alertas (ack=0 y ack=1)

---

## Variables de Entorno Recomendadas

Cree un archivo `.env` en la raíz del proyecto:

```bash
# Seguridad
FLASK_SECRET_KEY=<generate-random-string>
FLASK_DEBUG=False

# Autenticación (defecto: admin/admin)
ADMIN_USER=admin
ADMIN_PASS=C9_w0S6FKvJAJjGv

# Flask
FLASK_ENV=production
```

Para generar una clave segura:
```powershell
python -c "import secrets; print(secrets.token_hex(32))"
```

---

## Próximos Pasos Recomendados

### Fase 1: Seguridad (URGENTE - 2-3 horas)
- [ ] Mover credenciales a `.env`
- [ ] Implementar `@require_login` en rutas de upload/procesar
- [ ] Robustecer validación de rutas
- [ ] Agregar rate limiting (Flask-Limiter)
- [ ] Documentar deployment para producción

### Fase 2: Experiencia de Usuario (1-2 horas)
- [ ] Agregar estilos CSS (Bootstrap 5)
- [ ] Mejorar feedback visual (spinner, toast notifications)
- [ ] Búsqueda/filtrado en historial
- [ ] Exportar historial a CSV/Excel
- [ ] Modo oscuro (opcional)

### Fase 3: Funcionalidades Avanzadas (2-3 horas)
- [ ] Comparaciones período-a-período mejoradas (agrupación real)
- [ ] Gráficos de tendencias (Chart.js)
- [ ] Webhooks/email para alertas críticas
- [ ] Integración con Telegram o Slack
- [ ] Exportar alertas en formato ejecutivo (PDF)

### Fase 4: Producción (1-2 horas)
- [ ] Dockerfile para containerización
- [ ] Gunicorn/uWSGI + Nginx
- [ ] Backup automático de SQLite
- [ ] Logging centralizado (stdout → archivo)
- [ ] Monitoreo de disponibilidad (health check)
- [ ] HTTPS/SSL

---

## Testing Checklist

Antes de poner en producción, verificar:

- [ ] Login funciona con admin/admin
- [ ] Crear usuario desde CLI funciona
- [ ] Cambiar contraseña funciona
- [ ] Subir CSV de ventas → detecta VENTAS
- [ ] Subir CSV de inventario → detecta INVENTARIO
- [ ] Procesar ventas → genera dashboard.html actualizado
- [ ] Procesar inventario → genera inventario.html actualizado
- [ ] Historial muestra todas las cargas
- [ ] Reprocessar un upload regenera logs
- [ ] Eliminar upload borra archivo + DB records
- [ ] Alertas se generan para caída >20%
- [ ] Descargar archivo desde historial funciona
- [ ] Path traversal bloqueado (`../../../etc/passwd`)
- [ ] CSRF token presente en formularios
- [ ] Logout funciona
- [ ] Rutas protegidas redirigen a login si no autenticado

---

## Estructura de Código Clave

### app.py - Funciones principales

| Función | Líneas | Propósito |
|---------|--------|----------|
| `_load_db_module()` | 22-40 | Import robusto de db.py |
| `leer_archivo()` | ~160 | Lee CSV/XLS/XLSX con Pandas |
| `detectar_tipo()` | ~175 | Classifica VENTAS vs INVENTARIO |
| `validar_datos()` | ~190 | Verifica columnas requeridas |
| `validar_contenido()` | ~210 | Validaciones secundarias (numéricos, fechas) |
| `evaluate_alerts_for_upload()` | ~230-350 | Genera alertas automáticas |
| `index()` | ~370-430 | GET/POST upload + preview |
| `procesar()` | ~440-500 | Ejecuta subprocess, guarda logs |
| `history()` | ~510-530 | Lista histórico con alertas |
| `history_detail()` | ~540-590 | Detalle + archivos + auditoría |
| `uploaded_file()` | ~600-640 | Descarga segura con auditoría |
| `delete_upload_route()` | ~650-670 | Elimina upload + archivo |
| `reprocess_upload_route()` | ~680-740 | Reprocesa un archivo anterior |
| `login()` | ~750-800 | Autenticación Flask-Login |

### db.py - Funciones de persistencia

Todas las operaciones CRUD están aquí. Usan SQLite con `row_factory` para acceso dict-like.

**CRUD principales:**
- `insert_upload()`, `get_uploads()`, `get_upload_by_id()`
- `insert_execution_log()`, `get_execution_logs_for_upload()`
- `insert_alert()`, `get_unacknowledged_alerts()`, `acknowledge_alert()`
- `insert_download_log()`, `get_downloads_for_upload()`
- `create_user()`, `get_user_by_username()`, `update_user_password()`

---

## Notas Técnicas

### Encoding en Windows
El código maneja explícitamente UTF-8 en Windows:
```python
env.update({'PYTHONIOENCODING': 'utf-8', 'PYTHONUTF8': '1'})
```

Esto evita errores de encoding al ejecutar `AUTOMATIZAR_TODO.py` desde subprocess.

### Detección de Tipo (Heurística)
La función `detectar_tipo()` usa **intersección de conjuntos** de columnas normalizadas (lowercase, trimmed):
- **VENTAS:** Requiere ≥3 de {cliente, vendedor, total, estado}
- **INVENTARIO:** Requiere ≥2 de {nombre, cantidad a la mano, cantidad pronosticada}

Si ambas coinciden, prefiere VENTAS.

### Manejo de Errores
- Intentos de read/write a BD en try/except (no bloquean el flujo)
- Validación en 2 niveles: estructura (columnas) + contenido (tipos)
- Redacción de logs antes de guardar (evita exposición de credenciales)

### Security Considerations
- CSRF habilitado en todas las formas (Flask-WTF)
- Path traversal protegido en `/centro_control/uploads/<nombre>`
- Archivos subidos guardados con UUID (no con nombre original)
- Redacción de logs (password, passwd, secret)
- Login mediante hash PBKDF2 o plaintext (configurable)

---

## Links Útiles

- **Documentación Flask:** https://flask.palletsprojects.com/
- **Documentación Pandas:** https://pandas.pydata.org/
- **Documentación SQLite:** https://www.sqlite.org/cli.html
- **Documentación Flask-Login:** https://flask-login.readthedocs.io/
- **Documentación Flask-WTF:** https://flask-wtf.readthedocs.io/

---

## Contacto/Soporte

Si encontrás errores o tenés preguntas:

1. Revisar `logs/` para error logs
2. Activar debug: cambiar `app.config['DEBUG']` a True (solo desarrollo)
3. Verificar `.env` y credenciales
4. Consultar DB directamente: `python -c "import sqlite3; conn = sqlite3.connect('centro_control/centro_control.db'); print(conn.execute('SELECT * FROM upload_history').fetchall())"`

---

**Última actualización:** 2026-09-01  
**Versión:** 1.0 (Beta)  
**Estado de deployment:** Desarrollo local  
**Prioridad siguiente:** Seguridad (hardening) + UI (estilos)
