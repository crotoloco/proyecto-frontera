#!/usr/bin/env python
# Script simple para depuración

import os
import sys
import pandas as pd
import json
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_DIR / 'data'

print("🔍 VERIFICANDO INSTALACIONES...")
print(f"   Python: {sys.version}")
print(f"   Pandas: {pd.__version__}")

print("\n📁 ARCHIVOS DISPONIBLES:")
cwd = os.getcwd()
print(f"   Directorio: {cwd}\n")

for archivo in os.listdir(cwd):
    if archivo.endswith(('.csv', '.json', '.py')):
        tamaño = os.path.getsize(os.path.join(cwd, archivo))
        print(f"   ✓ {archivo} ({tamaño} bytes)")

print("\n🧪 PROBANDO LECTURA DE CSV...")
try:
    df = pd.read_csv(DATA_DIR / 'Orden de venta (sale.order).csv', encoding='utf-8')
    print(f"   ✓ CSV cargado exitosamente")
    print(f"   ✓ Filas: {len(df)}, Columnas: {len(df.columns)}")
except Exception as e:
    print(f"   ✗ Error: {e}")
    sys.exit(1)

print("\n✓ Sistema listo para análisis")
