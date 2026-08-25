#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Análisis Completo de Ventas - Frontera Living
Genera reportes, estadísticas y exporta datos
"""

import pandas as pd
import json
from datetime import datetime
from collections import Counter
import os

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(PROJECT_DIR, 'data')
REPORTS_DIR = os.path.join(PROJECT_DIR, 'reports')

print("\n" + "=" * 100)
print("🎯 ANÁLISIS COMPLETO DE VENTAS - FRONTERA LIVING".center(100))
print("=" * 100)

# Cargar datos
archivo_csv = os.path.join(DATA_DIR, 'Orden de venta (sale.order).csv')
df = pd.read_csv(archivo_csv, encoding='utf-8')

print(f"\n📊 INFORMACIÓN GENERAL")
print("-" * 100)
print(f"   Archivo: {archivo_csv}")
print(f"   Total de órdenes: {len(df)}")
print(f"   Columnas: {', '.join(df.columns)}")
print(f"   Período: {df['Fecha de creación'].min()} a {df['Fecha de creación'].max()}")

# ANÁLISIS 1: ESTADÍSTICAS DE MONTOS
print(f"\n💰 ANÁLISIS DE MONTOS")
print("-" * 100)
totales = pd.to_numeric(df['Total'], errors='coerce').dropna()
print(f"   Total Ingresos: ${totales.sum():,.2f}")
print(f"   Ticket Promedio: ${totales.mean():,.2f}")
print(f"   Venta Máxima: ${totales.max():,.2f}")
print(f"   Venta Mínima: ${totales.min():,.2f}")
print(f"   Desviación Estándar: ${totales.std():,.2f}")

# ANÁLISIS 2: CLIENTES
print(f"\n👥 ANÁLISIS DE CLIENTES")
print("-" * 100)
clientes_unicos = df['Cliente'].nunique()
print(f"   Total de Clientes Únicos: {clientes_unicos}")

# Top 10 clientes por monto
cliente_ventas = df.groupby('Cliente')['Total'].apply(lambda x: pd.to_numeric(x, errors='coerce').sum()).sort_values(ascending=False)
print(f"\n   TOP 10 CLIENTES (Por Monto Total):")
for i, (cliente, monto) in enumerate(cliente_ventas.head(10).items(), 1):
    porcentaje = (monto / totales.sum()) * 100
    print(f"   {i:2}. {cliente[:50]:50} ${monto:>13,.2f}  ({porcentaje:5.1f}%)")

# Clientes por cantidad de órdenes
cliente_ordenes = df['Cliente'].value_counts()
print(f"\n   TOP 5 CLIENTES (Por Número de Órdenes):")
for i, (cliente, cantidad) in enumerate(cliente_ordenes.head(5).items(), 1):
    print(f"   {i}. {cliente[:50]:50} {cantidad:3} órdenes")

# ANÁLISIS 3: VENDEDORES
print(f"\n🧑‍💼 ANÁLISIS DE VENDEDORES")
print("-" * 100)
vendedores_unicos = df['Vendedor'].nunique()
print(f"   Total de Vendedores: {vendedores_unicos}")

vendedor_ventas = df.groupby('Vendedor')['Total'].apply(lambda x: pd.to_numeric(x, errors='coerce').sum()).sort_values(ascending=False)
print(f"\n   VENTAS POR VENDEDOR:")
for i, (vendedor, monto) in enumerate(vendedor_ventas.items(), 1):
    ordenes = len(df[df['Vendedor'] == vendedor])
    ticket_promedio = monto / ordenes if ordenes > 0 else 0
    porcentaje = (monto / totales.sum()) * 100
    print(f"   {i}. {vendedor:20} ${monto:>13,.2f}  ({ordenes:2} órdenes, ticket: ${ticket_promedio:>10,.2f})  {porcentaje:5.1f}%")

# ANÁLISIS 4: ESTADOS
print(f"\n📋 ANÁLISIS DE ESTADOS")
print("-" * 100)
estados = df['Estado'].value_counts()
print(f"   Estados de Órdenes:")
for estado, cantidad in estados.items():
    porcentaje = (cantidad / len(df)) * 100
    print(f"   • {estado}: {cantidad} órdenes ({porcentaje:.1f}%)")

# ANÁLISIS 5: TÉRMINOS DE PAGO
print(f"\n💳 ANÁLISIS DE TÉRMINOS DE PAGO")
print("-" * 100)
terminos = df['Términos de pago'].value_counts()
print(f"   Términos de Pago:")
for termino, cantidad in terminos.items():
    porcentaje = (cantidad / len(df)) * 100
    print(f"   • {termino}: {cantidad} órdenes ({porcentaje:.1f}%)")

# ANÁLISIS 6: EMPRESAS
print(f"\n🏢 ANÁLISIS DE EMPRESAS")
print("-" * 100)
empresas = df['Empresa'].value_counts()
print(f"   Empresas ({len(empresas)} total):")
for empresa, cantidad in empresas.items():
    monto = df[df['Empresa'] == empresa]['Total'].apply(lambda x: pd.to_numeric(x, errors='coerce')).sum()
    porcentaje = (cantidad / len(df)) * 100
    print(f"   • {empresa}: {cantidad} órdenes (${monto:,.2f})  {porcentaje:.1f}%")

# ANÁLISIS 7: RANKINGS Y RATIOS
print(f"\n📈 ANÁLISIS DE RATIOS Y MÉTRICAS")
print("-" * 100)
print(f"   Valor Promedio por Cliente: ${totales.sum() / clientes_unicos:,.2f}")
print(f"   Órdenes por Cliente (promedio): {len(df) / clientes_unicos:.1f}")
print(f"   Órdenes por Vendedor (promedio): {len(df) / vendedores_unicos:.1f}")
print(f"   Concentración Top 5 Clientes: {(cliente_ventas.head(5).sum() / totales.sum() * 100):.1f}%")
print(f"   Concentración Top 10 Clientes: {(cliente_ventas.head(10).sum() / totales.sum() * 100):.1f}%")

# ANÁLISIS 8: EXCEPCIONES
print(f"\n⚠️  ANÁLISIS DE EXCEPCIONES")
print("-" * 100)
excepciones = df['Excepción principal'].value_counts()
if len(excepciones) > 0:
    print(f"   Excepciones Encontradas:")
    for exc, cantidad in excepciones.items():
        if pd.notna(exc) and exc != '':
            print(f"   • {exc}: {cantidad} órdenes")
        elif pd.isna(exc):
            print(f"   • Sin excepción: {cantidad} órdenes")
else:
    print(f"   No hay excepciones registradas ✓")

# ANÁLISIS 9: ACTIVIDADES
print(f"\n🎯 ANÁLISIS DE ACTIVIDADES")
print("-" * 100)
actividades = df['Actividades'].value_counts()
print(f"   Total de Registros con Actividades: {len(df[df['Actividades'].notna()])}")
if len(actividades) > 0:
    print(f"   Resumen de Actividades:")
    for act, cantidad in actividades.head(5).items():
        if pd.notna(act):
            print(f"   • {str(act)[:60]:60} {cantidad} órdenes")

# EXPORTAR A FORMATOS
print(f"\n💾 EXPORTANDO ANÁLISIS")
print("-" * 100)

# Exportar resumen como JSON
resumen = {
    'fecha_analisis': datetime.now().isoformat(),
    'total_ordenes': int(len(df)),
    'total_ingresos': float(totales.sum()),
    'ticket_promedio': float(totales.mean()),
    'ticket_maximo': float(totales.max()),
    'ticket_minimo': float(totales.min()),
    'clientes_unicos': int(clientes_unicos),
    'vendedores_unicos': int(vendedores_unicos),
    'top_5_clientes': [(str(cliente), float(monto)) for cliente, monto in cliente_ventas.head(5).items()],
    'estados': {str(k): int(v) for k, v in estados.items()},
    'terminos_pago': {str(k): int(v) for k, v in terminos.items()},
}

with open(os.path.join(REPORTS_DIR, 'analisis_ventas_resumen.json'), 'w', encoding='utf-8') as f:
    json.dump(resumen, f, ensure_ascii=False, indent=2)
print(f"   ✓ Resumen guardado en: analisis_ventas_resumen.json")

# Exportar tabla completa a Excel
try:
    df.to_excel(os.path.join(REPORTS_DIR, 'analisis_ventas_completo.xlsx'), index=False, sheet_name='Ventas')
    print(f"   ✓ Datos completos exportados a: analisis_ventas_completo.xlsx")
except Exception as e:
    print(f"   ℹ️  Para exportar a Excel: pip install openpyxl")

# Exportar CSV filtrado
df.to_csv(os.path.join(REPORTS_DIR, 'analisis_ventas_completo.csv'), index=False, encoding='utf-8')
print(f"   ✓ Datos exportados a: analisis_ventas_completo.csv")

print("\n" + "=" * 100)
print("✓ ANÁLISIS COMPLETADO".center(100))
print("=" * 100 + "\n")
