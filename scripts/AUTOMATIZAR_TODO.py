#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
╔════════════════════════════════════════════════════════════════════════════╗
║                                                                            ║
║                    🚀 AUTOMATIZAR TODO - FRONTERA LIVING                  ║
║                                                                            ║
║         Este script GENERA AUTOMÁTICAMENTE todos los reportes             ║
║                                                                            ║
╚════════════════════════════════════════════════════════════════════════════╝

Uso:
    python AUTOMATIZAR_TODO.py

Genera:
    ✓ REPORTE_VENTAS.xlsx (Excel profesional)
    ✓ REPORTE_EJECUTIVO.txt (Análisis completo)
    ✓ dashboard.html (Gráficos interactivos)
    ✓ analisis_detallado.json (Datos estructurados)

"""

import os
import sys
import pandas as pd
import json
from datetime import datetime
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_DIR / 'data'
REPORTS_DIR = PROJECT_DIR / 'reports'
CSV_PATH = DATA_DIR / 'Orden de venta (sale.order).csv'
REPORTS_DIR.mkdir(exist_ok=True)

# Forzar UTF-8 en stdout/stderr cuando sea posible (evita errores de 'charmap' en Windows)
try:
    os.environ.setdefault('PYTHONIOENCODING', 'utf-8')
    os.environ.setdefault('PYTHONUTF8', '1')
    if hasattr(sys.stdout, 'reconfigure'):
        try:
            sys.stdout.reconfigure(encoding='utf-8')
            sys.stderr.reconfigure(encoding='utf-8')
        except Exception:
            pass
except Exception:
    pass

# Colores para terminal
VERDE = '\033[92m'
AZUL = '\033[94m'
AMARILLO = '\033[93m'
ROJO = '\033[91m'
RESET = '\033[0m'

def print_header():
    """Muestra el header del programa"""
    print("\n" + "=" * 90)
    print("🚀 AUTOMATIZACIÓN COMPLETA DE REPORTES - FRONTERA LIVING".center(90))
    print("=" * 90)
    print(f"Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")

def print_paso(numero, titulo):
    """Imprime un paso del proceso"""
    print(f"\n{AZUL}[PASO {numero}] {titulo}{RESET}")
    print("-" * 90)

def print_ok(mensaje):
    """Imprime mensaje de éxito"""
    print(f"{VERDE}✓ {mensaje}{RESET}")

def print_error(mensaje):
    """Imprime mensaje de error"""
    print(f"{ROJO}✗ {mensaje}{RESET}")

def print_info(mensaje):
    """Imprime mensaje informativo"""
    print(f"{AMARILLO}ℹ {mensaje}{RESET}")

# ============================================================================
# PASO 1: VERIFICAR DEPENDENCIAS
# ============================================================================

def verificar_dependencias():
    """Verifica que Python tenga las librerías necesarias"""
    print_paso(1, "Verificando Dependencias")
    
    dependencias = {
        'pandas': 'Lectura de CSV',
        'openpyxl': 'Generación de Excel',
    }
    
    faltantes = []
    for modulo, descripcion in dependencias.items():
        try:
            __import__(modulo)
            print_ok(f"{modulo} - {descripcion}")
        except ImportError:
            faltantes.append(modulo)
            print_error(f"{modulo} no está instalado")
    
    if faltantes:
        print_info("\nInstalando dependencias faltantes...")
        os.system(f'python -m pip install {" ".join(faltantes)} -q')
        print_ok("Dependencias instaladas correctamente")
    
    return True

# ============================================================================
# PASO 2: VERIFICAR ARCHIVOS
# ============================================================================

def verificar_archivos():
    """Verifica que exista el archivo CSV"""
    print_paso(2, "Verificando Archivos")
    
    csv_file = CSV_PATH
    
    if not Path(csv_file).exists():
        print_error(f"No se encontró: {csv_file}")
        print_info("El archivo CSV debe estar en la misma carpeta que este script")
        return False
    
    print_ok(f"Archivo encontrado: {csv_file}")
    
    # Verificar que se puede leer
    try:
        df = pd.read_csv(csv_file, encoding='utf-8')
        print_ok(f"CSV cargado: {len(df)} órdenes, {len(df.columns)} columnas")
        return df
    except Exception as e:
        print_error(f"Error al leer CSV: {e}")
        return False

# ============================================================================
# PASO 3: GENERAR EXCEL
# ============================================================================

def generar_excel(df):
    """Genera el archivo Excel profesional"""
    print_paso(3, "Generando Reporte Excel")
    
    try:
        excel_file = REPORTS_DIR / 'REPORTE_VENTAS.xlsx'
        totales = pd.to_numeric(df['Total'], errors='coerce').dropna()
        
        with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
            # Hoja 1: Datos Completos
            df.to_excel(writer, sheet_name='Datos Completos', index=False)
            print_ok("Hoja: Datos Completos")
            
            # Hoja 2: Análisis por Cliente
            cliente_analisis = df.groupby('Cliente').agg({
                'Total': ['sum', 'count', 'mean'],
            }).round(2)
            cliente_analisis.columns = ['Monto Total', 'Cantidad', 'Promedio']
            cliente_analisis = cliente_analisis.sort_values('Monto Total', ascending=False)
            cliente_analisis.to_excel(writer, sheet_name='Clientes')
            print_ok("Hoja: Análisis por Clientes")
            
            # Hoja 3: Análisis por Vendedor
            vendedor_analisis = df.groupby('Vendedor').agg({
                'Total': ['sum', 'count', 'mean'],
                'Cliente': 'nunique'
            }).round(2)
            vendedor_analisis.columns = ['Monto Total', 'Órdenes', 'Promedio', 'Clientes']
            vendedor_analisis.to_excel(writer, sheet_name='Vendedores')
            print_ok("Hoja: Análisis por Vendedores")
            
            # Hoja 4: KPIs
            kpis = {
                'KPI': [
                    'Total Ingresos',
                    'Órdenes',
                    'Clientes',
                    'Ticket Promedio',
                    'Máximo',
                    'Mínimo',
                    'Desviación'
                ],
                'Valor': [
                    f"${totales.sum():,.2f}",
                    f"{len(df)}",
                    f"{df['Cliente'].nunique()}",
                    f"${totales.mean():,.2f}",
                    f"${totales.max():,.2f}",
                    f"${totales.min():,.2f}",
                    f"${totales.std():,.2f}"
                ]
            }
            kpis_df = pd.DataFrame(kpis)
            kpis_df.to_excel(writer, sheet_name='KPIs', index=False)
            print_ok("Hoja: KPIs Resumen")
            
            # Hoja 5: Estados
            estados = df['Estado'].value_counts().to_frame('Cantidad')
            estados.to_excel(writer, sheet_name='Estados')
            print_ok("Hoja: Estados")
            
            # Hoja 6: Términos de Pago
            terminos = df['Términos de pago'].value_counts().to_frame('Cantidad')
            terminos.to_excel(writer, sheet_name='Términos')
            print_ok("Hoja: Términos de Pago")
        
        print_ok(f"✨ Excel generado: {excel_file}")
        return True
    
    except Exception as e:
        print_error(f"Error generando Excel: {e}")
        return False

# ============================================================================
# PASO 4: GENERAR REPORTE EJECUTIVO
# ============================================================================

def generar_reporte_ejecutivo(df):
    """Genera el reporte en texto"""
    print_paso(4, "Generando Reporte Ejecutivo")
    
    try:
        totales = pd.to_numeric(df['Total'], errors='coerce').dropna()
        
        reporte = f"""
{'='*100}
REPORTE EJECUTIVO DE VENTAS - FRONTERA LIVING S.A
{'='*100}

GENERADO: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
PERÍODO: {df['Fecha de creación'].min()} a {df['Fecha de creación'].max()}

{'─'*100}
INDICADORES PRINCIPALES
{'─'*100}

Total Ingresos:          ${totales.sum():>20,.2f}
Número de Órdenes:                        {len(df):>6}
Clientes Únicos:                          {df['Cliente'].nunique():>6}
Ticket Promedio:         ${totales.mean():>20,.2f}
Ticket Máximo:           ${totales.max():>20,.2f}
Ticket Mínimo:           ${totales.min():>20,.2f}
Vendedores:                               {df['Vendedor'].nunique():>6}

{'─'*100}
TOP 10 CLIENTES
{'─'*100}

"""
        cliente_totales = df.groupby('Cliente')['Total'].sum().sort_values(ascending=False)
        for i, (cliente, monto) in enumerate(cliente_totales.head(10).items(), 1):
            porcentaje = (monto / totales.sum()) * 100
            ordenes = len(df[df['Cliente'] == cliente])
            reporte += f"{i:2}. {cliente[:45]:45} ${monto:>13,.2f}  ({porcentaje:5.1f}%)  [{ordenes} órdenes]\n"
        
        reporte += f"""
{'─'*100}
INFORMACIÓN OPERATIVA
{'─'*100}

Estados:
"""
        for estado, cantidad in df['Estado'].value_counts().items():
            reporte += f"   • {estado}: {cantidad} órdenes ({(cantidad/len(df)*100):.1f}%)\n"
        
        reporte += f"\nTérminos de Pago:\n"
        for termino, cantidad in df['Términos de pago'].value_counts().items():
            reporte += f"   • {termino}: {cantidad} órdenes ({(cantidad/len(df)*100):.1f}%)\n"
        
        reporte += f"""
{'═'*100}
CONCLUSIONES Y RECOMENDACIONES
{'═'*100}

1. RETENCIÓN DE TOP CLIENTES
   Top 5 clientes generan {(df.groupby('Cliente')['Total'].sum().nlargest(5).sum() / totales.sum() * 100):.1f}% de ingresos
   → Implementar account management dedicado

2. DIVERSIFICACIÓN DE CARTERA
   → Captar nuevos clientes para reducir riesgo

3. EXPANSIÓN DE FUERZA DE VENTAS
   Actualmente {df['Vendedor'].nunique()} vendedor(es)
   → Considerar expansion del equipo de ventas

4. PROGRAMA DE FIDELIZACIÓN
   Muchos clientes tienen una única orden
   → Implementar programa de repetición

{'═'*100}
Generado automáticamente por Sistema de Reportes Frontera Living
{datetime.now().year}
{'═'*100}
"""
        
        with open(REPORTS_DIR / 'REPORTE_EJECUTIVO.txt', 'w', encoding='utf-8') as f:
            f.write(reporte)
        
        print_ok("Reporte Ejecutivo generado: REPORTE_EJECUTIVO.txt")
        return True
    
    except Exception as e:
        print_error(f"Error generando reporte: {e}")
        return False

# ============================================================================
# PASO 5: GENERAR JSON
# ============================================================================

def generar_json(df):
    """Genera archivo JSON con datos"""
    print_paso(5, "Generando Datos JSON")
    
    try:
        totales = pd.to_numeric(df['Total'], errors='coerce').dropna()
        cliente_totales = df.groupby('Cliente')['Total'].sum().sort_values(ascending=False)
        
        datos = {
            'fecha_generacion': datetime.now().isoformat(),
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
                    'cliente': str(cliente),
                    'monto': float(monto),
                    'ordenes': int(len(df[df['Cliente'] == cliente]))
                }
                for cliente, monto in cliente_totales.head(10).items()
            ]
        }
        
        with open(REPORTS_DIR / 'analisis_detallado.json', 'w', encoding='utf-8') as f:
            json.dump(datos, f, ensure_ascii=False, indent=2)
        
        print_ok("Datos JSON generados: analisis_detallado.json")
        return True
    
    except Exception as e:
        print_error(f"Error generando JSON: {e}")
        return False

# ============================================================================
# PASO 6: VERIFICAR DASHBOARD
# ============================================================================

def verificar_dashboard():
    """Verifica que el dashboard HTML existe"""
    print_paso(6, "Verificando Dashboard")
    
    if (PROJECT_DIR / 'dashboard.html').exists():
        print_ok("Dashboard HTML disponible: dashboard.html")
        print_info("Abre en navegador: start dashboard.html")
        return True
    else:
        print_error("Dashboard no encontrado")
        return False

# ============================================================================
# PASO 7: RESUMEN FINAL
# ============================================================================

def mostrar_resumen():
    """Muestra resumen final"""
    print_paso(7, "Resumen de Archivos Generados")
    
    archivos = {
        REPORTS_DIR / 'REPORTE_VENTAS.xlsx': 'Excel con 6 hojas de análisis',
        REPORTS_DIR / 'REPORTE_EJECUTIVO.txt': 'Reporte profesional en texto',
        REPORTS_DIR / 'analisis_detallado.json': 'Datos en formato JSON',
        PROJECT_DIR / 'dashboard.html': 'Gráficos interactivos'
    }
    
    for archivo, descripcion in archivos.items():
        if Path(archivo).exists():
            tamaño = Path(archivo).stat().st_size / 1024
            print_ok(f"{str(archivo.relative_to(PROJECT_DIR)):40} ({tamaño:.1f} KB) - {descripcion}")
        else:
            print_error(f"{archivo:40} (No generado)")
    
    print(f"\n{VERDE}{'='*90}")
    print("✨ AUTOMATIZACIÓN COMPLETADA EXITOSAMENTE ✨".center(90))
    print(f"{'='*90}{RESET}\n")

# ============================================================================
# MAIN
# ============================================================================

def main():
    """Ejecuta el flujo completo"""
    os.chdir(PROJECT_DIR)
    print_header()
    
    # Paso 1
    if not verificar_dependencias():
        return
    
    # Paso 2
    df = verificar_archivos()
    if df is False or df is None:
        print_error("No se puede continuar sin el archivo CSV")
        return
    
    # Paso 3
    if not generar_excel(df):
        return 1
    
    # Paso 4
    if not generar_reporte_ejecutivo(df):
        return 1
    
    # Paso 5
    if not generar_json(df):
        return 1
    
    # Paso 6
    if not verificar_dashboard():
        return 1
    
    # Paso 7
    mostrar_resumen()
    
    print(f"{AZUL}PRÓXIMOS PASOS:{RESET}")
    print("   1. Abre: REPORTE_VENTAS.xlsx")
    print("   2. Abre: start dashboard.html (en navegador)")
    print("   3. Lee: REPORTE_EJECUTIVO.txt")
    print()

if __name__ == "__main__":
    try:
        raise SystemExit(main() or 0)
    except KeyboardInterrupt:
        print(f"\n{AMARILLO}Proceso interrumpido por el usuario{RESET}\n")
    except Exception as e:
        print(f"\n{ROJO}Error inesperado: {e}{RESET}\n")
