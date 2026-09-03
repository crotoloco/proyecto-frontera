"""Registra ejecuciones y genera el Centro de Control local."""
from __future__ import annotations

import html
import json
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd

PROJECT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_DIR / 'data'
REPORTS_DIR = PROJECT_DIR / 'reports'
MONITOR_FILE = REPORTS_DIR / 'MONITOREO_SISTEMA.json'
MONITOR_HTML = PROJECT_DIR / 'monitor.html'
CSV_CANONICO = DATA_DIR / 'Orden de venta (sale.order).csv'


def registrar_ejecucion(
    *,
    inicio: datetime,
    fuente: str,
    codigo: int,
    procesamiento: str,
    error: str = '',
) -> None:
    """Guarda el estado actual y un historial acotado de ejecuciones."""
    REPORTS_DIR.mkdir(exist_ok=True)
    fin = datetime.now()
    registros = []
    if MONITOR_FILE.exists():
        try:
            registros = json.loads(MONITOR_FILE.read_text(encoding='utf-8')).get('historial', [])
        except (OSError, json.JSONDecodeError):
            registros = []

    cantidad = 0
    if CSV_CANONICO.exists():
        try:
            cantidad = len(pd.read_csv(CSV_CANONICO, encoding='utf-8-sig'))
        except (OSError, ValueError, pd.errors.ParserError):
            cantidad = 0

    estado = 'OK' if codigo == 0 else 'ERROR'
    registro = {
        'fecha': fin.isoformat(timespec='seconds'),
        'estado': estado,
        'fuente': fuente,
        'registros': cantidad,
        'duracion_segundos': round((fin - inicio).total_seconds(), 2),
        'error': error,
    }
    historial = (registros + [registro])[-50:]
    documento = {
        'ultima_ejecucion': registro,
        'ultima_sincronizacion_exitosa': registro['fecha'] if codigo == 0 else _ultimo_exitoso(historial),
        'fuente_utilizada': fuente,
        'cantidad_registros': cantidad,
        'estado_odoo': 'NO APLICA' if fuente != 'odoo' else ('OK' if codigo == 0 else 'ERROR'),
        'estado_procesamiento': procesamiento,
        'estado_dashboard': 'OK' if (PROJECT_DIR / 'dashboard.html').exists() else 'ERROR',
        'historial': historial,
    }
    MONITOR_FILE.write_text(json.dumps(documento, ensure_ascii=False, indent=2), encoding='utf-8')
    _generar_html(documento)


def _ultimo_exitoso(historial: list[dict[str, Any]]) -> str:
    for registro in reversed(historial):
        if registro.get('estado') == 'OK':
            return str(registro.get('fecha', ''))
    return ''


def _generar_html(documento: dict[str, Any]) -> None:
    ultima = documento['ultima_ejecucion']
    historial = reversed(documento.get('historial', []))
    filas = ''.join(
        '<tr><td>{}</td><td><strong class="{}">{}</strong></td><td>{}</td><td>{}</td><td>{} s</td></tr>'.format(
            html.escape(str(item.get('fecha', ''))),
            'good' if item.get('estado') == 'OK' else 'bad',
            html.escape(str(item.get('estado', ''))),
            html.escape(str(item.get('fuente', ''))),
            item.get('registros', 0),
            item.get('duracion_segundos', 0),
        )
        for item in historial
    )
    error = html.escape(str(ultima.get('error') or 'Sin errores registrados'))
    status_class = 'good' if ultima.get('estado') == 'OK' else 'bad'
    document = f'''<!doctype html>
<html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Frontera Living | Centro de Control</title>
<style>
:root{{--ink:#162a2b;--muted:#657579;--bg:#f4f7f3;--card:#fff;--line:#dce5df;--teal:#087c78;--red:#a13f36;--shadow:0 18px 50px #16373417}}
*{{box-sizing:border-box}}body{{margin:0;color:var(--ink);background:radial-gradient(circle at 90% 0,#dcece1,transparent 32%),var(--bg);font-family:Segoe UI,Arial,sans-serif}}main{{max-width:1120px;margin:auto;padding:28px 24px 60px}}header{{display:flex;justify-content:space-between;align-items:center;margin-bottom:48px}}nav a{{color:var(--muted);margin-left:16px;text-decoration:none;font-size:13px}}h1{{font-size:clamp(38px,6vw,68px);line-height:.95;margin:0;letter-spacing:-2px}}.eyebrow{{color:var(--teal);font-size:11px;font-weight:700;letter-spacing:2px;text-transform:uppercase}}.grid{{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin:25px 0}}.card,.panel{{background:var(--card);border:1px solid var(--line);border-radius:12px;box-shadow:var(--shadow)}}.card{{padding:20px}}.label{{font-size:11px;color:var(--muted);text-transform:uppercase;letter-spacing:1px}}.value{{font-size:24px;font-weight:800;margin-top:10px}}.good,.bad{{font-weight:800}}.good{{color:var(--teal)}}.bad{{color:var(--red)}}.panel{{overflow:hidden;margin-top:18px}}.panel h2{{font-size:20px;margin:0;padding:20px 22px;border-bottom:1px solid var(--line)}}.notice{{padding:18px 22px;color:#704d2b;background:#fff8ed;border-bottom:1px solid #efd9b8;font-size:13px}}.table-wrap{{overflow:auto}}table{{width:100%;border-collapse:collapse;min-width:650px}}th,td{{padding:13px 22px;text-align:left;border-bottom:1px solid var(--line);font-size:13px}}th{{color:var(--muted);font-size:10px;text-transform:uppercase;letter-spacing:1px;background:#f7faf7}}@media(max-width:760px){{main{{padding:20px 14px 40px}}header{{align-items:flex-start;margin-bottom:34px}}nav{{display:grid;gap:8px;text-align:right}}.grid{{grid-template-columns:repeat(2,1fr)}}}}
</style></head><body><main><header><div><p class="eyebrow">Frontera Living</p><h1>Centro de<br>Control</h1></div><nav><a href="dashboard.html">Ventas</a><a href="inventario.html">Inventario</a></nav></header>
<section class="grid"><article class="card"><div class="label">Estado general</div><div class="value {status_class}">{html.escape(str(ultima.get('estado', 'N/D')))}</div></article><article class="card"><div class="label">Registros</div><div class="value">{documento.get('cantidad_registros', 0):,}</div></article><article class="card"><div class="label">Fuente</div><div class="value">{html.escape(str(documento.get('fuente_utilizada', 'N/D')))}</div></article><article class="card"><div class="label">Última ejecución</div><div class="value">{html.escape(str(ultima.get('fecha', 'N/D')))}</div></article></section>
<section class="panel"><h2>Estado del sistema</h2><div class="notice"><strong>Procesamiento: {html.escape(str(documento.get('estado_procesamiento', 'N/D')))}</strong><br>Dashboard: {html.escape(str(documento.get('estado_dashboard', 'N/D')))} · Odoo: {html.escape(str(documento.get('estado_odoo', 'N/D')))}<br>Último error: {error}</div></section>
<section class="panel"><h2>Historial de ejecuciones</h2><div class="table-wrap"><table><thead><tr><th>Fecha</th><th>Estado</th><th>Fuente</th><th>Registros</th><th>Duración</th></tr></thead><tbody>{filas}</tbody></table></div></section></main></body></html>'''
    MONITOR_HTML.write_text(document, encoding='utf-8')
