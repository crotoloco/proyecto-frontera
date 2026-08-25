#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Ejecuta AUTOMATIZAR_TODO.py cada 15 minutos.

Uso:
    python automatizar_cada_15_minutos.py
    python automatizar_cada_15_minutos.py --once
"""

import sys
import time
from datetime import datetime
from pathlib import Path
import subprocess

import pandas as pd

INTERVALO_SEGUNDOS = 15 * 60
BASE_DIR = Path(__file__).resolve().parent
PROJECT_DIR = BASE_DIR.parent
SCRIPT_PRINCIPAL = BASE_DIR / 'AUTOMATIZAR_TODO.py'
DATA_DIR = PROJECT_DIR / 'data'
CSV_CANONICO = DATA_DIR / 'Orden de venta (sale.order).csv'
DATA_DIR.mkdir(exist_ok=True)


def actualizar_desde_archivo():
    """Usa el CSV o Excel más nuevo de Odoo como entrada del proceso."""
    candidatos = [
        archivo for archivo in DATA_DIR.iterdir()
        if archivo.suffix.lower() in {'.csv', '.xlsx'}
        and archivo.name != CSV_CANONICO.name
        and not archivo.name.startswith('~$')
    ]

    if not candidatos:
        print('No hay un CSV o Excel nuevo; se conserva el archivo actual.')
        return True

    archivo_nuevo = max(candidatos, key=lambda archivo: archivo.stat().st_mtime)
    print(f'Archivo nuevo detectado: {archivo_nuevo.name}')

    try:
        if archivo_nuevo.suffix.lower() == '.xlsx':
            datos = pd.read_excel(archivo_nuevo)
        else:
            datos = pd.read_csv(archivo_nuevo, encoding='utf-8-sig')
        if datos.empty:
            print('El archivo está vacío; se conserva el CSV actual.')
            return False

        datos.to_csv(CSV_CANONICO, index=False, encoding='utf-8-sig')
        print(f'CSV actualizado desde Excel: {len(datos)} filas')
        return True
    except Exception as error:
        print(f'No se pudo leer el archivo todavía: {error}')
        print('Puede estar copiándose. Se conserva el CSV actual para el próximo ciclo.')
        return False


def ejecutar_automatizacion():
    print('\n' + '=' * 90)
    print(f'[{datetime.now().strftime("%d/%m/%Y %H:%M:%S")}] Ejecutando flujo automático...')
    print('=' * 90)

    if not actualizar_desde_archivo():
        return 1

    resultado = subprocess.run(
        [sys.executable, str(SCRIPT_PRINCIPAL)],
        cwd=str(PROJECT_DIR),
        check=False,
    )

    if resultado.returncode == 0:
        print(f'[{datetime.now().strftime("%d/%m/%Y %H:%M:%S")}] Flujo finalizado correctamente.')
    else:
        print(f'[{datetime.now().strftime("%d/%m/%Y %H:%M:%S")}] El flujo falló con código: {resultado.returncode}')

    return resultado.returncode


def main():
    ejecutar_una_vez = '--once' in sys.argv

    if ejecutar_una_vez:
        return ejecutar_automatizacion()

    print('AUTOMATIZACIÓN ACTIVA - Se ejecutará cada 15 minutos.')
    print(f'Ruta del script principal: {SCRIPT_PRINCIPAL}')
    print('Presiona Ctrl+C para detener la automatización.')

    while True:
        codigo = ejecutar_automatizacion()
        print(f'Próxima ejecución en {INTERVALO_SEGUNDOS // 60} minutos...')
        time.sleep(INTERVALO_SEGUNDOS)

    return 0


if __name__ == '__main__':
    raise SystemExit(main())
