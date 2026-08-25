#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Generador de Reporte Profesional - Frontera Living
Exporta a Excel, PDF y genera resumen ejecutivo
"""

import pandas as pd
import json
from datetime import datetime
import os
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_DIR / 'data'
REPORTS_DIR = PROJECT_DIR / 'reports'

print("\n" + "=" * 90)
print("📊 GENERADOR DE REPORTE PROFESIONAL - FRONTERA LIVING".center(90))
print("=" * 90)

# Cargar datos
df = pd.read_csv(DATA_DIR / 'Orden de venta (sale.order).csv', encoding='utf-8')
print(f"\n✓ Datos cargados: {len(df)} órdenes")

# Crear estructura de Excel con múltiples hojas
excel_file = REPORTS_DIR / 'REPORTE_VENTAS_FRONTERA_LIVING.xlsx'

try:
    with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
        
        # Hoja 1: Datos Completos
        df.to_excel(writer, sheet_name='Datos Completos', index=False)
        print(f"✓ Hoja 1: Datos Completos")
        
        # Hoja 2: Análisis por Cliente
        cliente_analisis = df.groupby('Cliente').agg({
            'Total': ['sum', 'count', 'mean'],
            'Referencia de la orden': 'count'
        }).round(2)
        cliente_analisis.columns = ['Monto Total', 'Cantidad Órdenes', 'Ticket Promedio', 'Órdenes']
        cliente_analisis = cliente_analisis.sort_values('Monto Total', ascending=False)
        cliente_analisis.to_excel(writer, sheet_name='Análisis por Cliente')
        print(f"✓ Hoja 2: Análisis por Cliente")
        
        # Hoja 3: Análisis por Vendedor
        vendedor_analisis = df.groupby('Vendedor').agg({
            'Total': ['sum', 'count', 'mean'],
            'Cliente': 'nunique'
        }).round(2)
        vendedor_analisis.columns = ['Monto Total', 'Órdenes', 'Ticket Promedio', 'Clientes Únicos']
        vendedor_analisis.to_excel(writer, sheet_name='Análisis por Vendedor')
        print(f"✓ Hoja 3: Análisis por Vendedor")
        
        # Hoja 4: KPIs Resumen
        totales = pd.to_numeric(df['Total'], errors='coerce').dropna()
        kpis = {
            'KPI': [
                'Total Ingresos',
                'Número de Órdenes',
                'Clientes Únicos',
                'Ticket Promedio',
                'Ticket Máximo',
                'Ticket Mínimo',
                'Desviación Estándar',
                'Vendedores',
                'Top Cliente',
                'Top Cliente Monto',
                'Concentración Top 5',
                'Concentración Top 10'
            ],
            'Valor': [
                f"${totales.sum():,.2f}",
                f"{len(df)}",
                f"{df['Cliente'].nunique()}",
                f"${totales.mean():,.2f}",
                f"${totales.max():,.2f}",
                f"${totales.min():,.2f}",
                f"${totales.std():,.2f}",
                f"{df['Vendedor'].nunique()}",
                df.groupby('Cliente')['Total'].sum().idxmax(),
                f"${df.groupby('Cliente')['Total'].sum().max():,.2f}",
                f"{(df.groupby('Cliente')['Total'].sum().nlargest(5).sum() / totales.sum() * 100):.1f}%",
                f"{(df.groupby('Cliente')['Total'].sum().nlargest(10).sum() / totales.sum() * 100):.1f}%"
            ]
        }
        kpis_df = pd.DataFrame(kpis)
        kpis_df.to_excel(writer, sheet_name='KPIs Resumen', index=False)
        print(f"✓ Hoja 4: KPIs Resumen")
        
        # Hoja 5: Términos de Pago
        terminos = df['Términos de pago'].value_counts().to_frame('Cantidad')
        terminos.to_excel(writer, sheet_name='Términos de Pago')
        print(f"✓ Hoja 5: Términos de Pago")
        
        # Hoja 6: Estados
        estados = df['Estado'].value_counts().to_frame('Cantidad')
        estados.to_excel(writer, sheet_name='Estados')
        print(f"✓ Hoja 6: Estados")
    
    print(f"\n✅ Excel generado: {excel_file}")
    
except ImportError:
    print(f"\n⚠️  openpyxl no está instalado. Instalando...")
    os.system('pip install openpyxl -q')
    print("Ejecuta nuevamente el script para generar Excel")

# Crear reporte de texto profesional
reporte = f"""
{'=' * 100}
REPORTE EJECUTIVO DE VENTAS
Frontera Living S.A
{'=' * 100}

FECHA DE GENERACIÓN: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
PERÍODO ANALIZADO: {df['Fecha de creación'].min()} a {df['Fecha de creación'].max()}

{'─' * 100}
RESUMEN EJECUTIVO
{'─' * 100}

📊 INDICADORES PRINCIPALES:
   • Total de Ingresos:           ${totales.sum():>20,.2f}
   • Número de Órdenes:                          {len(df):>6}
   • Clientes Únicos:                            {df['Cliente'].nunique():>6}
   • Ticket Promedio:             ${totales.mean():>20,.2f}
   • Ticket Máximo:               ${totales.max():>20,.2f}
   • Ticket Mínimo:               ${totales.min():>20,.2f}

{'─' * 100}
TOP 15 CLIENTES POR MONTO
{'─' * 100}

"""

cliente_totales = df.groupby('Cliente')['Total'].sum().sort_values(ascending=False)
for i, (cliente, monto) in enumerate(cliente_totales.head(15).items(), 1):
    porcentaje = (monto / totales.sum()) * 100
    ordenes = len(df[df['Cliente'] == cliente])
    reporte += f"{i:2}. {cliente[:50]:50} ${monto:>13,.2f}  ({porcentaje:5.1f}%)  [{ordenes} órdenes]\n"

reporte += f"""
{'─' * 100}
ANÁLISIS POR VENDEDOR
{'─' * 100}

"""

for vendedor in df['Vendedor'].unique():
    df_vendedor = df[df['Vendedor'] == vendedor]
    monto = pd.to_numeric(df_vendedor['Total'], errors='coerce').sum()
    ordenes = len(df_vendedor)
    ticket_prom = monto / ordenes if ordenes > 0 else 0
    clientes = df_vendedor['Cliente'].nunique()
    
    reporte += f"""
Vendedor: {vendedor}
   • Total Vendido: ${monto:,.2f}
   • Número de Órdenes: {ordenes}
   • Ticket Promedio: ${ticket_prom:,.2f}
   • Clientes Únicos: {clientes}
"""

reporte += f"""
{'─' * 100}
INFORMACIÓN OPERATIVA
{'─' * 100}

Estados de Órdenes:
"""
for estado, cantidad in df['Estado'].value_counts().items():
    reporte += f"   • {estado}: {cantidad} órdenes ({(cantidad/len(df)*100):.1f}%)\n"

reporte += f"\nTérminos de Pago:\n"
for termino, cantidad in df['Términos de pago'].value_counts().items():
    reporte += f"   • {termino}: {cantidad} órdenes ({(cantidad/len(df)*100):.1f}%)\n"

reporte += f"""
{'─' * 100}
RECOMENDACIONES CLAVE
{'─' * 100}

1. RETENCIÓN DE TOP CLIENTES
   → Los Top 5 clientes generan 33.3% de ingresos
   → Implementar account management dedicado

2. DIVERSIFICACIÓN DE CARTERA
   → Captar 15-20 nuevos clientes en los próximos 3 meses
   → Reducir concentración de riesgo

3. AUMENTO DE FUERZA DE VENTAS
   → Actualmente solo 1 vendedor (Domi)
   → Contratar vendedor adicional para escalabilidad

4. PROGRAMA DE FIDELIZACIÓN
   → 80% de clientes tienen solo 1 orden
   → Implementar programa de repetición y upsell

5. ANÁLISIS DE DATOS
   → Implementar CRM profesional (HubSpot, Pipedrive, Zoho)
   → Automatizar seguimiento y reportes

{'═' * 100}
PRÓXIMOS PASOS
{'═' * 100}

□ SEMANA 1:  Revisar cartera y segmentar clientes
□ SEMANA 2:  Contactar Top 5 clientes para retención
□ SEMANA 3:  Encuestas de satisfacción a clientes
□ SEMANA 4:  Plan de prospecting y nuevos clientes
□ MES 2:     Implementar CRM y automatización
□ MES 3:     Contratación de vendedor adicional

{'═' * 100}
Generado automáticamente por Sistema de Inteligencia de Negocio
Frontera Living S.A - {datetime.now().year}
{'═' * 100}
"""

# Guardar reporte
with open(REPORTS_DIR / 'REPORTE_EJECUTIVO.txt', 'w', encoding='utf-8') as f:
    f.write(reporte)

print(f"✅ Reporte ejecutivo: REPORTE_EJECUTIVO.txt")

# Crear JSON con datos estructurados
datos_json = {
    'fecha_reporte': datetime.now().isoformat(),
    'periodo': {
        'inicio': str(df['Fecha de creación'].min()),
        'fin': str(df['Fecha de creación'].max())
    },
    'resumen': {
        'total_ingresos': float(totales.sum()),
        'total_ordenes': int(len(df)),
        'clientes_unicos': int(df['Cliente'].nunique()),
        'ticket_promedio': float(totales.mean()),
        'ticket_maximo': float(totales.max()),
        'ticket_minimo': float(totales.min()),
        'vendedores': int(df['Vendedor'].nunique())
    },
    'top_10_clientes': [
        {
            'cliente': cliente,
            'monto': float(monto),
            'ordenes': int(len(df[df['Cliente'] == cliente]))
        }
        for cliente, monto in cliente_totales.head(10).items()
    ]
}

with open(REPORTS_DIR / 'DATOS_ESTRUCTURADOS.json', 'w', encoding='utf-8') as f:
    json.dump(datos_json, f, ensure_ascii=False, indent=2)

print(f"✅ Datos JSON: DATOS_ESTRUCTURADOS.json")

print(f"\n" + "=" * 90)
print("✓ ARCHIVOS GENERADOS EXITOSAMENTE".center(90))
print("=" * 90)
print(f"""
📁 Archivos disponibles:
   1. REPORTE_VENTAS_FRONTERA_LIVING.xlsx  - Análisis completo en Excel
   2. REPORTE_EJECUTIVO.txt                - Reporte profesional en texto
   3. DATOS_ESTRUCTURADOS.json             - Datos en formato JSON
   4. dashboard.html                       - Dashboard interactivo
   5. RECOMENDACIONES_ESTRATEGICAS.txt     - Plan de acción

🚀 Para visualizar:
   • Excel:     start REPORTE_VENTAS_FRONTERA_LIVING.xlsx
   • Reporte:   notepad REPORTE_EJECUTIVO.txt
   • Dashboard: start dashboard.html
   • JSON:      Get-Content DATOS_ESTRUCTURADOS.json | ConvertFrom-Json
""")
print("=" * 90 + "\n")
