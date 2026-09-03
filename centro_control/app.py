from __future__ import annotations

from pathlib import Path
import subprocess
import sys
import importlib.util
from uuid import uuid4
from functools import wraps
from os import getenv

import pandas as pd
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, session, send_from_directory, redirect, url_for, Response, send_file
from werkzeug.security import check_password_hash
from flask_wtf import CSRFProtect
from flask_wtf.csrf import generate_csrf
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from datetime import datetime

def _load_db_module():
    """Cargar el módulo db de forma robusta tanto si se ejecuta como paquete
    (python -m centro_control.app) como si se ejecuta directamente
    (python centro_control/app.py).
    """
    try:
        # Preferir import como paquete si está disponible
        from . import db as _db  # type: ignore
        return _db
    except Exception:
        # Importar por ruta de archivo cuando se ejecuta como script
        db_path = Path(__file__).resolve().parent / 'db.py'
        spec = importlib.util.spec_from_file_location('centro_control.db', str(db_path))
        module = importlib.util.module_from_spec(spec)
        sys.modules['centro_control.db'] = module
        spec.loader.exec_module(module)  # type: ignore
        return module


db = _load_db_module()

# ensure users table exists
try:
    db.init_user_table()
except Exception:
    # ignore if DB not ready
    pass

PROJECT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_DIR / 'data'
ALLOWED_EXTENSIONS = {'.csv', '.xls', '.xlsx'}
UPLOAD_DIR = PROJECT_DIR / 'centro_control' / 'uploads'
UPLOAD_DIR.mkdir(exist_ok=True)


def get_project_python_executable() -> str:
    """Devuelve el Python del entorno virtual del proyecto cuando exista.
    Esto evita que la app llame al intérprete del sistema sin dependencias.
    """
    candidates = [
        PROJECT_DIR / '.venv' / 'Scripts' / 'python.exe',
        PROJECT_DIR / 'venv' / 'Scripts' / 'python.exe',
        Path(sys.executable),
    ]
    for candidate in candidates:
        if candidate and candidate.exists():
            return str(candidate)
    return sys.executable


# Inicializar base de datos local (SQLite)
db.init_db()

app = Flask(__name__, template_folder='templates')
# SECRET KEY: prefer variable de entorno para evitar hardcodear secretos
app.config['SECRET_KEY'] = getenv('FLASK_SECRET_KEY', 'frontera-control-local')
if getenv('FLASK_SECRET_KEY') is None:
    print('WARNING: No se estableció FLASK_SECRET_KEY; se usa valor por defecto. No usar en producción.')
app.config['MAX_CONTENT_LENGTH'] = 25 * 1024 * 1024

# Credenciales básicas (pueden sobreescribirse con variables de entorno)
app.config['ADMIN_USER'] = getenv('ADMIN_USER', 'admin')
app.config['ADMIN_PASS'] = getenv('ADMIN_PASS', 'admin')
# Advertencia clara si se usan credenciales por defecto (solo para desarrollo)
if app.config['ADMIN_USER'] == 'admin' and app.config['ADMIN_PASS'] == 'admin':
    print('WARNING: Se están usando credenciales por defecto (admin/admin). No usar en producción.')

# Inicializar CSRF y Login
csrf = CSRFProtect()
csrf.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


class User(UserMixin):
    def __init__(self, username: str):
        self.id = username


@login_manager.user_loader
def load_user(user_id: str):
    try:
        row = db.get_user_by_username(user_id)
        if row:
            return User(row['username'])
        # fallback to env admin
        if user_id == app.config.get('ADMIN_USER'):
            return User(user_id)
    except Exception:
        pass
    return None


@app.context_processor
def inject_csrf():
    # expose csrf_token() to templates
    return {'csrf_token': lambda: generate_csrf()}


@app.context_processor
def inject_user():
    return {'logged_in': session.get('user')}


def require_login(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            if not current_user.is_authenticated:
                return redirect(url_for('login', next=request.path))

            uid = current_user.get_id()
            if not uid:
                return redirect(url_for('login', next=request.path))

            try:
                row = db.get_user_by_username(uid)
                if row:
                    return func(*args, **kwargs)
            except Exception:
                pass

            if uid == app.config.get('ADMIN_USER'):
                return func(*args, **kwargs)

            return redirect(url_for('login', next=request.path))
        except Exception:
            return redirect(url_for('login', next=request.path))

    return wrapper


def require_admin(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Allow bypass in development
        try:
            if getenv('DISABLE_AUTH') == '1':
                return func(*args, **kwargs)
        except Exception:
            pass
        try:
            uid = current_user.get_id()
            if not uid:
                return redirect(url_for('login', next=request.path))
            # check users table
            try:
                row = db.get_user_by_username(uid)
                if row and row['is_admin']:
                    return func(*args, **kwargs)
            except Exception:
                pass
            # fallback to env admin user
            if uid == app.config.get('ADMIN_USER'):
                return func(*args, **kwargs)
            return ('Acceso denegado', 403)
        except Exception:
            return ('Acceso denegado', 403)

    return wrapper


def leer_archivo(file_storage, extension: str | None = None) -> pd.DataFrame:
    if extension is None:
        extension = Path(file_storage.filename or '').suffix.lower()
    if extension == '.xlsx':
        return pd.read_excel(file_storage)
    if extension == '.xls':
        return pd.read_excel(file_storage)
    # por defecto intentar leer CSV; pandas detecta encoding en muchos casos
    return pd.read_csv(file_storage, encoding='utf-8-sig')


def detectar_tipo(columnas: list[str]) -> str | None:
    normalizadas = {str(columna).strip().lower() for columna in columnas}
    ventas = {'cliente', 'vendedor', 'total', 'estado'}
    inventario = {'nombre', 'cantidad a la mano', 'cantidad pronosticada'}
    if len(ventas & normalizadas) >= 3:
        return 'VENTAS'
    if len(inventario & normalizadas) >= 2:
        return 'INVENTARIO'
    return None


def validar_datos(datos: pd.DataFrame, tipo: str | None) -> list[str]:
    # validar esquema mínimo y presencia de registros
    if not tipo:
        return ['No se pudo determinar si el archivo es de ventas o inventario.']
    required = {
        'VENTAS': {'cliente', 'vendedor', 'total', 'estado'},
        'INVENTARIO': {'nombre', 'cantidad a la mano', 'cantidad pronosticada'},
    }[tipo]
    columnas = {str(columna).strip().lower() for columna in datos.columns}
    faltantes = sorted(required - columnas)
    errores: list[str] = []
    if faltantes:
        errores.append(f'Faltan columnas necesarias: {", ".join(faltantes)}')
    if datos.empty:
        errores.append('El archivo no contiene registros.')
    return errores


def validar_contenido(datos: pd.DataFrame, tipo: str | None) -> list[str]:
    """Validaciones adicionales no bloqueantes: tipos numéricos, fechas, duplicados, campos vacíos."""
    advertencias: list[str] = []
    if datos is None or datos.empty:
        return advertencias


def _safe_read_csv(path: Path) -> pd.DataFrame | None:
    try:
        if path.suffix.lower() in {'.xls', '.xlsx'}:
            return pd.read_excel(path)
        return pd.read_csv(path, encoding='utf-8-sig')
    except Exception:
        return None


def evaluate_alerts_for_upload(upload_id: int) -> None:
    """Genera alertas simples basadas en reglas comparativas y de contenido.
    Reglas implementadas:
    - Archivo inválido (columnas faltantes / vacío)
    - Error de procesamiento (execution_log con returncode != 0)
    - Caída de ventas significativa >20% respecto al período anterior
    - Aumento excepcional de ventas >50%
    - Concentración excesiva de clientes (top cliente >60% del total)
    - Productos sin stock en inventario (cantidad a la mano <= 0)
    """
    try:
        upload = db.get_upload_by_id(upload_id)
        if not upload:
            return
        tipo = upload['tipo']
        existing_alerts = db.get_alerts_for_upload(upload_id)

        def create_alert(tipo_alerta: str, mensaje: str, valor=None, comparado_con=None, timestamp=None) -> None:
            if any(a['tipo_alerta'] == tipo_alerta and a['mensaje'] == mensaje for a in existing_alerts):
                return
            db.insert_alert(
                upload_id=upload_id,
                tipo_alerta=tipo_alerta,
                mensaje=mensaje,
                valor=valor,
                comparado_con=comparado_con,
                timestamp=timestamp or datetime.utcnow().isoformat(),
            )
            existing_alerts.append({'tipo_alerta': tipo_alerta, 'mensaje': mensaje})

        # alertar si el upload ya contiene errores graves
        if upload['errores']:
            errores_text = str(upload['errores'])
            if 'Faltan columnas' in errores_text or 'no contiene registros' in errores_text.lower():
                create_alert('Archivo inválido', errores_text)

        # revisar logs de ejecución
        logs = db.get_execution_logs_for_upload(upload_id)
        if logs and logs[0]['returncode'] != 0:
            create_alert(
                'Error de procesamiento',
                logs[0]['stderr'] or 'Error sin detalle',
                valor=str(logs[0]['returncode']),
                timestamp=logs[0]['timestamp'] or datetime.utcnow().isoformat(),
            )

        # reglas que requieren leer archivos
        # ventas: comparación con último upload de tipo VENTAS previo
        if tipo == 'VENTAS':
            # obtener archivo actual
            current_path = UPLOAD_DIR / upload['nombre_guardado']
            cur_df = _safe_read_csv(current_path)
            if cur_df is None:
                return
            # localizar columna total
            cols_low = {str(c).strip().lower(): c for c in cur_df.columns}
            total_col = None
            for cand in ('total', 'amount_total', 'importe'):
                if cand in cols_low:
                    total_col = cols_low[cand]
                    break
            if total_col is None:
                # no se puede comparar si no hay total
                pass
            else:
                cur_total = pd.to_numeric(cur_df[total_col], errors='coerce').sum(skipna=True)
                # buscar prev upload
                prev = None
                for r in db.get_uploads(200):
                    if r['id'] != upload_id and r['tipo'] == 'VENTAS':
                        prev = r
                        break
                if prev:
                    prev_path = UPLOAD_DIR / prev['nombre_guardado']
                    prev_df = _safe_read_csv(prev_path)
                    if prev_df is not None and total_col in {str(c).strip().lower() for c in prev_df.columns}:
                        # try to find corresponding column in prev
                        prev_cols_low = {str(c).strip().lower(): c for c in prev_df.columns}
                        prev_total_col = prev_cols_low.get(total_col) or next((prev_cols_low.get(k) for k in ('total','amount_total','importe') if k in prev_cols_low), None)
                        if prev_total_col:
                            prev_total = pd.to_numeric(prev_df[prev_total_col], errors='coerce').sum(skipna=True)
                            if prev_total > 0:
                                change = (cur_total - prev_total) / prev_total
                                if change <= -0.2:
                                    create_alert('Caída de ventas', f'Ventas cayeron {round(change*100,1)}% respecto al período anterior', valor=str(round(change*100,1)), comparado_con=str(prev['id']))
                                if change >= 0.5:
                                    create_alert('Aumento excepcional', f'Ventas aumentaron {round(change*100,1)}% respecto al período anterior', valor=str(round(change*100,1)), comparado_con=str(prev['id']))
                # concentración clientes
                client_col = None
                for cand in ('cliente','partner','customer'):
                    if cand in cols_low:
                        client_col = cols_low[cand]
                        break
                if client_col and cur_total and cur_total != 0:
                    grp = cur_df.groupby(client_col)[total_col].sum(numeric_only=True)
                    if not grp.empty:
                        top_share = grp.max() / grp.sum()
                        if top_share >= 0.6:
                            create_alert('Concentración de clientes', f'Cliente top representa {round(top_share*100,1)}% del total', valor=str(round(top_share*100,1)))

        if tipo == 'INVENTARIO':
            current_path = UPLOAD_DIR / upload['nombre_guardado']
            cur_df = _safe_read_csv(current_path)
            if cur_df is None:
                return
            cols_low = {str(c).strip().lower(): c for c in cur_df.columns}
            qty_col = None
            for cand in ('cantidad a la mano','qty_available','cantidad'):
                if cand in cols_low:
                    qty_col = cols_low[cand]
                    break
            if qty_col:
                non_stock = pd.to_numeric(cur_df[qty_col], errors='coerce') <= 0
                if non_stock.any():
                    cnt = int(non_stock.sum())
                    create_alert('Productos sin stock', f'{cnt} productos con stock <= 0', valor=str(cnt))
    except Exception:
        # nunca levantar excepciones desde evaluación de alertas
        return
    cols = {str(c).strip().lower(): c for c in datos.columns}
    # verificar numericos para ventas
    if tipo == 'VENTAS':
        # total
        for key in ('total', 'amount_total',):
            if key in cols:
                col = cols[key]
                non_numeric = pd.to_numeric(datos[col], errors='coerce').isna() & datos[col].notna()
                if non_numeric.any():
                    advertencias.append(f'Hay valores no numéricos en la columna "{col}".')
                break
        # fechas
        for cand in ('fecha de creación', 'fecha', 'date', 'create_date'):
            if cand in cols:
                col = cols[cand]
                parsed = pd.to_datetime(datos[col], errors='coerce')
                if parsed.isna().any():
                    advertencias.append(f'Hay fechas inválidas en la columna "{col}".')
                break
    if tipo == 'INVENTARIO':
        for key in ('cantidad a la mano', 'qty_available', 'cantidad'):
            if key in cols:
                col = cols[key]
                non_numeric = pd.to_numeric(datos[col], errors='coerce').isna() & datos[col].notna()
                if non_numeric.any():
                    advertencias.append(f'Hay valores no numéricos en la columna "{col}".')
                break
        for key in ('cantidad pronosticada', 'virtual_available'):
            if key in cols:
                col = cols[key]
                non_numeric = pd.to_numeric(datos[col], errors='coerce').isna() & datos[col].notna()
                if non_numeric.any():
                    advertencias.append(f'Hay valores no numéricos en la columna "{col}".')
                break
    # duplicados
    dupes = datos.duplicated()
    if dupes.any():
        advertencias.append(f'Existen {dupes.sum()} filas duplicadas exactas.')
    # campos importantes vacíos
    for req in ('cliente', 'nombre', 'vendedor'):
        if req in cols:
            col = cols[req]
            empties = datos[col].isna() | (datos[col].astype(str).str.strip() == '')
            if empties.any():
                advertencias.append(f'Hay {empties.sum()} filas con "{col}" vacío.')
    return advertencias


@app.route('/', methods=['GET', 'POST'])
@app.route('/centro_control', methods=['GET', 'POST'])
@app.route('/centro_control/', methods=['GET', 'POST'])
def index():
    resultado = None
    error = None
    if request.method == 'POST':
        archivo = request.files.get('archivo')
        extension = Path(archivo.filename or '').suffix.lower() if archivo else ''
        if not archivo or not archivo.filename:
            error = 'Seleccioná un archivo CSV o Excel.'
        elif extension not in ALLOWED_EXTENSIONS:
            error = 'El formato debe ser CSV, XLS o XLSX.'
        else:
            try:
                datos = leer_archivo(archivo)
                tipo = detectar_tipo(list(datos.columns))
                errores = validar_datos(datos, tipo)
                advertencias = validar_contenido(datos, tipo)
                guardado = f'{uuid4().hex}_{secure_filename(archivo.filename)}'
                archivo.stream.seek(0)
                archivo.save(UPLOAD_DIR / guardado)
                session['archivo_guardado'] = guardado
                try:
                    # registrar en historial (guardar también advertencias como WARN)
                    merged = []
                    if errores:
                        merged.extend(errores)
                    if advertencias:
                        merged.extend([f'WARN: {a}' for a in advertencias])
                    errores_text = ', '.join(merged) if merged else ''
                    db.insert_upload(
                        nombre_original=archivo.filename,
                        nombre_guardado=guardado,
                        tipo=tipo,
                        filas=len(datos),
                        columnas=len(datos.columns),
                        errores=errores_text,
                        timestamp=datetime.utcnow().isoformat(),
                    )
                except Exception:
                    # no bloquear la subida si falla el registro en la DB
                    pass
                resultado = {
                    'nombre': archivo.filename,
                    'tipo': tipo,
                    'filas': len(datos),
                    'columnas': len(datos.columns),
                    'errores': errores,
                    'guardado': guardado,
                    'nombres_columnas': [str(columna) for columna in datos.columns],
                    'vista_previa': datos.head(5).to_html(
                        classes='preview-table', index=False, border=0
                    ),
                }
            except Exception as exc:
                error = f'No se pudo leer el archivo: {exc}'
    return render_template('index.html', resultado=resultado, error=error)


@app.post('/procesar')
def procesar():
    nombre = secure_filename(
        request.form.get('archivo_guardado') or session.get('archivo_guardado', '')
    )
    archivo = UPLOAD_DIR / nombre
    if not nombre or not archivo.exists():
        return render_template('index.html', error='El archivo temporal ya no está disponible.'), 400
    try:
        datos = leer_archivo(archivo, extension=archivo.suffix.lower())
        tipo = detectar_tipo(list(datos.columns))
        errores = validar_datos(datos, tipo)
        advertencias = validar_contenido(datos, tipo)
        if errores:
            return render_template('index.html', error=' '.join(errores)), 400
        if tipo == 'VENTAS':
            destino = DATA_DIR / 'Orden de venta (sale.order).csv'
            datos.to_csv(destino, index=False, encoding='utf-8-sig')
            python_executable = get_project_python_executable()
            comando = [python_executable, str(PROJECT_DIR / 'scripts' / 'AUTOMATIZAR_TODO.py')]
        else:
            python_executable = get_project_python_executable()
            comando = [python_executable, str(PROJECT_DIR / 'scripts' / 'generar_inventario_html.py'), str(archivo)]
        # ejecutar el proceso asegurando salida en UTF-8 para evitar errores de encoding en Windows
        env = dict(**{} if 'PYTHONIOENCODING' not in __import__('os').environ else __import__('os').environ)
        env.update({'PYTHONIOENCODING': 'utf-8', 'PYTHONUTF8': '1'})
        resultado = subprocess.run(comando, cwd=str(PROJECT_DIR), capture_output=True, text=True, check=False, env=env)
        # evitar guardar logs excesivos o datos sensibles: truncar y redactar
        def _redact_and_truncate(s: str | None, limit: int = 10000) -> str:
            if not s:
                return ''
            lowered = s.lower()
            # redactar líneas que parezcan contener credenciales
            lines = []
            for line in s.splitlines():
                if 'password' in line.lower() or 'passwd' in line.lower() or 'secret' in line.lower():
                    lines.append('[REDACTED]')
                else:
                    lines.append(line)
            joined = '\n'.join(lines)
            if len(joined) > limit:
                return joined[:limit] + '\n...[truncated]'
            return joined

        safe_stdout = _redact_and_truncate(resultado.stdout)
        safe_stderr = _redact_and_truncate(resultado.stderr)
        try:
            upload_row = db.get_upload_by_guardado(nombre)
            upload_id = upload_row['id'] if upload_row is not None else None
            db.insert_execution_log(
                upload_id=upload_id,
                stdout=safe_stdout,
                stderr=safe_stderr,
                returncode=resultado.returncode,
                timestamp=datetime.utcnow().isoformat(),
            )
            # evaluar alertas basadas en este upload y logs
            try:
                if upload_id is not None:
                    evaluate_alerts_for_upload(upload_id)
            except Exception:
                pass
        except Exception:
            pass
        if resultado.returncode != 0:
            return render_template('index.html', error=f'El procesamiento falló: {safe_stderr[-500:]}'), 500
        # Mantener las vistas generadas como pantalla final del procesamiento.
        upload_row = db.get_upload_by_guardado(nombre)
        if tipo == 'VENTAS':
            return redirect(url_for('dashboard'))
        if tipo == 'INVENTARIO':
            return redirect(url_for('inventario'))
        if upload_row is not None:
            return render_template('index.html', procesado=tipo, upload_id=upload_row['id'], advertencias=advertencias)
        # si hay advertencias, mostrarlas pero dejar procesar
        if advertencias:
            return render_template('index.html', procesado=tipo, advertencias=advertencias)
        return render_template('index.html', procesado=tipo)
    except Exception as exc:
        return render_template('index.html', error=f'No se pudo procesar: {exc}'), 500


@app.route('/centro_control/history')
@require_login
def history():
    try:
        uploads = db.get_uploads(200)
    except Exception:
        uploads = []
    # obtener alertas no reconocidas para mostrar en la vista de historial
    try:
        alerts = db.get_unacknowledged_alerts(200)
    except Exception:
        alerts = []
    # contar descargas por upload para mostrar en la tabla
    try:
        downloads_map = {}
        for u in uploads:
            try:
                downloads_map[u['id']] = len(db.get_downloads_for_upload(u['id']))
            except Exception:
                downloads_map[u['id']] = 0
    except Exception:
        downloads_map = {}
    return render_template('history.html', uploads=uploads, alerts=alerts, downloads_map=downloads_map)


@app.route('/centro_control/history/<int:upload_id>')
@require_login
def history_detail(upload_id: int):
    try:
        upload = db.get_upload_by_id(upload_id)
        logs = db.get_execution_logs_for_upload(upload_id) if upload else []
    except Exception:
        upload = None
        logs = []
    if not upload:
        return render_template('history.html', uploads=db.get_uploads(200))

    # información del fichero en disco
    file_info = {'exists': False, 'size': None, 'mtime': None}
    try:
        fp = UPLOAD_DIR / upload['nombre_guardado']
        if fp.exists():
            file_info['exists'] = True
            file_info['size'] = fp.stat().st_size
            file_info['mtime'] = fp.stat().st_mtime
    except Exception:
        pass

    def _human_size(n: int | None) -> str:
        if not n:
            return '-'
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if n < 1024.0:
                return f"{n:.1f} {unit}"
            n /= 1024.0
        return f"{n:.1f} PB"

    if file_info['size'] is not None:
        file_info['size_hr'] = _human_size(file_info['size'])
    else:
        file_info['size_hr'] = '-'
    if file_info['mtime']:
        from datetime import datetime as _dt

        file_info['mtime_dt'] = _dt.utcfromtimestamp(file_info['mtime']).isoformat() + ' UTC'
    else:
        file_info['mtime_dt'] = '-'

    # obtener registros de descarga (auditoría)
    try:
        downloads = db.get_downloads_for_upload(upload_id)
    except Exception:
        downloads = []

    try:
        alerts = db.get_alerts_for_upload(upload_id)
    except Exception:
        alerts = []

    latest_log = logs[0] if logs else None
    processing_ok = latest_log is not None and latest_log['returncode'] == 0

    return render_template(
        'history_detail.html',
        upload=upload,
        logs=logs,
        alerts=alerts,
        latest_log=latest_log,
        processing_ok=processing_ok,
        file_info=file_info,
        downloads=downloads,
    )


@app.get('/centro_control/informe/<int:upload_id>')
@require_login
def processing_report(upload_id: int):
    return history_detail(upload_id)


@app.get('/centro_control/uploads/<path:nombre>')
@require_login
def uploaded_file(nombre: str):
    # servir archivos subidos de forma segura
    try:
        requested = (UPLOAD_DIR / nombre).resolve()
        if not str(requested).startswith(str(UPLOAD_DIR.resolve())):
            return ('Ruta inválida', 400)
        if not requested.exists():
            return ('No encontrado', 404)
        # Intentar sugerir el nombre original del archivo al descargar
        suggested_name = None
        try:
            upload_row = db.get_upload_by_guardado(nombre)
            suggested_name = upload_row['nombre_original'] if upload_row is not None else None
        except Exception:
            suggested_name = None
            # Registrar auditoría de descarga (no bloquear la entrega si falla)
            try:
                upload_row = db.get_upload_by_guardado(nombre)
                upload_id = upload_row['id'] if upload_row is not None else None
                client_ip = request.remote_addr
                user_agent = request.headers.get('User-Agent')
                db.insert_download_log(
                    upload_id=upload_id,
                    filename=suggested_name or nombre,
                    client_ip=client_ip,
                    user_agent=user_agent,
                    timestamp=datetime.utcnow().isoformat(),
                )
            except Exception:
                # no bloquear la entrega por errores en la auditoría
                pass
            # Forzar descarga como attachment para evitar que el navegador renderice el archivo
            try:
                # Flask >= 2.0
                return send_from_directory(UPLOAD_DIR, nombre, as_attachment=True, download_name=suggested_name or nombre)
            except TypeError:
                # Compatibilidad con versiones antiguas de Flask
                return send_from_directory(UPLOAD_DIR, nombre, as_attachment=True, attachment_filename=suggested_name or nombre)
    except Exception:
        return ('Error al servir el archivo', 500)


@app.post('/centro_control/history/<int:upload_id>/delete')
@require_login
def delete_upload_route(upload_id: int):
    try:
        upload = db.get_upload_by_id(upload_id)
        if upload:
            # borrar archivo físico
            try:
                file_path = UPLOAD_DIR / upload['nombre_guardado']
                if file_path.exists():
                    file_path.unlink()
            except Exception:
                pass
            # borrar logs y registro
            try:
                db.delete_execution_logs_for_upload(upload_id)
            except Exception:
                pass
            try:
                db.delete_upload(upload_id)
            except Exception:
                pass
    except Exception:
        pass
    return redirect(url_for('history'))


@app.post('/centro_control/history/<int:upload_id>/reprocess')
@require_login
def reprocess_upload_route(upload_id: int):
    try:
        upload = db.get_upload_by_id(upload_id)
        if not upload:
            return redirect(url_for('history'))
        archivo = UPLOAD_DIR / upload['nombre_guardado']
        if not archivo.exists():
            return redirect(url_for('history'))
        # leer y validar
        datos = leer_archivo(archivo, extension=archivo.suffix.lower())
        tipo = detectar_tipo(list(datos.columns))
        errores = validar_datos(datos, tipo)
        if errores:
            # registrar intento fallido
            db.insert_execution_log(upload_id=upload_id, stdout='', stderr='; '.join(errores), returncode=1, timestamp=datetime.utcnow().isoformat())
            return render_template('history_detail.html', upload=upload, logs=db.get_execution_logs_for_upload(upload_id))
        if tipo == 'VENTAS':
            destino = DATA_DIR / 'Orden de venta (sale.order).csv'
            datos.to_csv(destino, index=False, encoding='utf-8-sig')
            comando = [get_project_python_executable(), str(PROJECT_DIR / 'scripts' / 'AUTOMATIZAR_TODO.py')]
        else:
            comando = [get_project_python_executable(), str(PROJECT_DIR / 'scripts' / 'generar_inventario_html.py'), str(archivo)]
        # ejecutar reprocess con encoding UTF-8 en el entorno
        env = dict(**{} if 'PYTHONIOENCODING' not in __import__('os').environ else __import__('os').environ)
        env.update({'PYTHONIOENCODING': 'utf-8', 'PYTHONUTF8': '1'})
        resultado = subprocess.run(comando, cwd=str(PROJECT_DIR), capture_output=True, text=True, check=False, env=env)
        # truncar y redactar logs antes de guardar
        def _redact_and_truncate_local(s: str | None, limit: int = 10000) -> str:
            if not s:
                return ''
            lines = []
            for line in s.splitlines():
                if 'password' in line.lower() or 'passwd' in line.lower() or 'secret' in line.lower():
                    lines.append('[REDACTED]')
                else:
                    lines.append(line)
            joined = '\n'.join(lines)
            if len(joined) > limit:
                return joined[:limit] + '\n...[truncated]'
            return joined

        try:
            db.insert_execution_log(
                upload_id=upload_id,
                stdout=_redact_and_truncate_local(resultado.stdout),
                stderr=_redact_and_truncate_local(resultado.stderr),
                returncode=resultado.returncode,
                timestamp=datetime.utcnow().isoformat(),
            )
            try:
                evaluate_alerts_for_upload(upload_id)
            except Exception:
                pass
        except Exception:
            pass
        return redirect(url_for('history_detail', upload_id=upload_id))
    except Exception:
        return redirect(url_for('history'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    next_url = request.args.get('next') or url_for('index')
    if request.method == 'POST':
        user = request.form.get('user')
        password = request.form.get('password')
        # intentar buscar usuario en la DB
        try:
            db_user = db.get_user_by_username(user)
        except Exception:
            db_user = None
        if db_user:
            stored = db_user['password_hash']
            try:
                if isinstance(stored, str) and (stored.startswith('pbkdf2:') or ':' in stored):
                    ok = check_password_hash(stored, password)
                else:
                    ok = (password == stored)
            except Exception:
                ok = (password == stored)
            if ok:
                u = User(db_user['username'])
                login_user(u)
                return redirect(request.form.get('next') or url_for('index'))
        else:
            # fallback: comprobar contra ADMIN_USER/ADMIN_PASS env
            if user == app.config.get('ADMIN_USER'):
                stored = app.config.get('ADMIN_PASS')
                ok = False
                try:
                    if isinstance(stored, str) and (stored.startswith('pbkdf2:') or ':' in stored):
                        ok = check_password_hash(stored, password)
                    else:
                        ok = (password == stored)
                except Exception:
                    ok = (password == stored)
                if ok:
                    u = User(user)
                    login_user(u)
                    return redirect(request.form.get('next') or url_for('index'))
        error = 'Usuario o contraseña inválidos.'
    return render_template('login.html', error=error, next=next_url)


@app.route('/registro', methods=['GET', 'POST'])
def register():
    next_url = request.args.get('next') or request.form.get('next') or url_for('index')
    error = None
    if request.method == 'POST':
        username = (request.form.get('username') or '').strip()
        password = request.form.get('password') or ''
        password_confirmation = request.form.get('password_confirmation') or ''
        if not username or not password:
            error = 'Completá todos los campos.'
        elif len(username) < 3:
            error = 'El usuario debe tener al menos 3 caracteres.'
        elif len(password) < 6:
            error = 'La contraseña debe tener al menos 6 caracteres.'
        elif password != password_confirmation:
            error = 'Las contraseñas no coinciden.'
        else:
            try:
                if db.get_user_by_username(username):
                    error = 'Ese usuario ya existe.'
                else:
                    from werkzeug.security import generate_password_hash
                    db.create_user(username, generate_password_hash(password), is_admin=False)
                    return redirect(url_for('login', next=next_url, registered=1))
            except Exception:
                error = 'No se pudo crear la cuenta. Probá con otro usuario.'
    return render_template('register.html', error=error, next=next_url)


@app.get('/logout')
def logout():
    try:
        logout_user()
    except Exception:
        session.pop('user', None)
    return redirect(url_for('index'))


@app.get('/dashboard.html')
@require_login
def dashboard():
    # Servir el archivo estático dashboard.html usando send_file para asegurar entrega completa
    try:
        file_path = PROJECT_DIR / 'dashboard.html'
        return send_file(str(file_path), mimetype='text/html', as_attachment=False)
    except Exception:
        return ('Dashboard no disponible', 500)


@app.get('/centro_control/dashboard')
@require_login
def dashboard_with_alerts():
    try:
        alerts = db.get_unacknowledged_alerts(200)
    except Exception:
        alerts = []
    return render_template('dashboard_with_alerts.html', alerts=alerts)


@app.get('/inventario.html')
def inventario():
    return send_from_directory(PROJECT_DIR, 'inventario.html')


@app.get('/monitor.html')
def monitor():
    return send_from_directory(PROJECT_DIR, 'monitor.html')


@app.get('/reports/<path:nombre>')
def reporte(nombre):
    return send_from_directory(PROJECT_DIR / 'reports', nombre)


@app.get('/centro_control/alerts')
@require_login
def alerts_list():
    try:
        alerts = db.get_unacknowledged_alerts(200)
    except Exception:
        alerts = []
    return render_template('alerts.html', alerts=alerts)


@app.get('/centro_control/users')
@require_login
@require_admin
def users_list():
    try:
        users = db.list_users(200)
    except Exception:
        users = []
    return render_template('users.html', users=users)


@app.route('/centro_control/users/create', methods=['GET', 'POST'])
@require_login
@require_admin
def users_create():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        is_admin = bool(request.form.get('is_admin'))
        if not username or not password:
            return render_template('create_user.html', error='Faltan campos')
        from werkzeug.security import generate_password_hash
        ph = generate_password_hash(password)
        try:
            db.create_user(username, ph, is_admin=is_admin)
            return redirect(url_for('users_list'))
        except Exception as e:
            return render_template('create_user.html', error=str(e))
    return render_template('create_user.html')


@app.route('/centro_control/users/<username>/delete', methods=['POST'])
@require_login
@require_admin
def users_delete(username: str):
    try:
        db.delete_user(username)
    except Exception:
        pass
    return redirect(url_for('users_list'))


@app.route('/centro_control/users/<username>/password', methods=['GET', 'POST'])
@require_login
@require_admin
def users_change_password(username: str):
    if request.method == 'POST':
        password = request.form.get('password')
        if not password:
            return render_template('change_password.html', username=username, error='Falta contraseña')
        from werkzeug.security import generate_password_hash
        ph = generate_password_hash(password)
        try:
            db.update_user_password(username, ph)
            return redirect(url_for('users_list'))
        except Exception as e:
            return render_template('change_password.html', username=username, error=str(e))
    return render_template('change_password.html', username=username)


@app.post('/centro_control/alerts/<int:alert_id>/ack')
@require_login
def alerts_ack(alert_id: int):
    try:
        db.acknowledge_alert(alert_id)
    except Exception:
        pass
    return redirect(url_for('alerts_list'))


if __name__ == '__main__':
    # Sólo activar debug si la variable de entorno FLASK_DEBUG está explícitamente activada
    debug_mode = getenv('FLASK_DEBUG', '0') in ('1', 'true', 'True')
    if debug_mode:
        print('Advertencia: Flask en modo DEBUG. Desactivá en producción.')
    # Bind to 0.0.0.0 in dev so localhost and other interfaces can connect if needed.
    # Keep debug_mode unchanged; this is safe for local development only.
    app.run(host='0.0.0.0', debug=debug_mode)
