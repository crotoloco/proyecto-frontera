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
import os

import pandas as pd

from normalizador import normalizar_ventas
from odoo_connector import OdooConnector
from monitor_sistema import registrar_ejecucion

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
        and 'Orden de venta' in archivo.name
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
        datos = normalizar_ventas(datos)
        if datos.empty:
            print('El archivo está vacío; se conserva el CSV actual.')
            return CSV_CANONICO.exists()

        datos.to_csv(CSV_CANONICO, index=False, encoding='utf-8-sig')
        print(f'CSV actualizado desde Excel: {len(datos)} filas')
        return True
    except Exception as error:
        print(f'No se pudo leer el archivo todavía: {error}')
        print('Puede estar copiándose. Se conserva el CSV actual para el próximo ciclo.')
        return CSV_CANONICO.exists()


def actualizar_desde_odoo():
    """Obtiene ventas de Odoo y las guarda en el mismo CSV canónico."""
    if os.getenv('ODOO_API_ENABLED', 'false').lower() not in {'1', 'true', 'si', 'yes'}:
        return None

    print('API de Odoo habilitada; intentando sincronizar...')
    conector = OdooConnector()
    if not conector.conectar():
        print('Odoo no disponible; se conserva el último CSV válido.')
        return False

    ventas = conector.obtener_ventas()
    if ventas is None:
        print('Odoo no devolvió datos; se conserva el último CSV válido.')
        return False

    try:
        datos = normalizar_ventas(ventas)
        if datos.empty:
            print('Odoo devolvió cero ventas; se conserva el último CSV válido.')
            return False
        datos.to_csv(CSV_CANONICO, index=False, encoding='utf-8-sig')
        print(f'CSV actualizado desde Odoo: {len(datos)} filas')
        return True
    except (TypeError, ValueError, OSError) as error:
        print(f'No se pudo normalizar la respuesta de Odoo: {error}')
        print('Se conserva el último CSV válido.')
        return False


def ejecutar_automatizacion():
    inicio = datetime.now()
    fuente = 'odoo' if os.getenv('ODOO_API_ENABLED', 'false').lower() in {'1', 'true', 'si', 'yes'} else 'archivo'
    procesamiento = 'ERROR'
    error = ''
    print('\n' + '=' * 90)
    print(f'[{datetime.now().strftime("%d/%m/%Y %H:%M:%S")}] Ejecutando flujo automático...')
    print('=' * 90)

    try:
        resultado_odoo = actualizar_desde_odoo()
        if resultado_odoo is False:
            fuente = 'fallback_csv'
            if not CSV_CANONICO.exists():
                error = 'No hay un CSV válido disponible para usar como respaldo.'
                print(error)
                return 1
        elif resultado_odoo is None and not actualizar_desde_archivo():
            error = 'No se pudo actualizar desde un archivo y no existe respaldo válido.'
            print(error)
            return 1

        resultado = subprocess.run(
            [sys.executable, str(SCRIPT_PRINCIPAL)],
            cwd=str(PROJECT_DIR),
            check=False,
        )
        if resultado.returncode == 0:
            procesamiento = 'OK'
            print(f'[{datetime.now().strftime("%d/%m/%Y %H:%M:%S")}] Flujo finalizado correctamente.')
        else:
            error = f'El flujo falló con código: {resultado.returncode}'
            print(f'[{datetime.now().strftime("%d/%m/%Y %H:%M:%S")}] {error}')
        return resultado.returncode
    except Exception as exception:
        error = str(exception)
        print(f'Error inesperado en el automatizador: {error}')
        return 1
    finally:
        registrar_ejecucion(
            inicio=inicio,
            fuente=fuente,
            codigo=0 if procesamiento == 'OK' else 1,
            procesamiento=procesamiento,
            error=error,
        )


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
