import pandas as pd
import json
from datetime import datetime
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_DIR / 'data'
REPORTS_DIR = PROJECT_DIR / 'reports'

class VentasReader:
    def __init__(self, archivo_csv=str(DATA_DIR / 'Orden de venta (sale.order).csv')):
        """Inicializar y cargar el archivo CSV"""
        self.archivo = archivo_csv
        self.df = None
        self.cargar_datos()
    
    def cargar_datos(self):
        """Cargar datos del CSV"""
        try:
            self.df = pd.read_csv(self.archivo, encoding='utf-8')
            print(f"✓ Archivo cargado: {self.archivo}")
            print(f"✓ Total de órdenes: {len(self.df)}")
            return True
        except FileNotFoundError:
            print(f"✗ Archivo no encontrado: {self.archivo}")
            return False
        except Exception as e:
            print(f"✗ Error al cargar archivo: {e}")
            return False
    
    def obtener_resumen(self):
        """Obtener resumen de ventas"""
        if self.df is None:
            print("✗ No hay datos cargados")
            return None
        
        try:
            resumen = {
                'total_ordenes': len(self.df),
                'monto_total': float(self.df['Total'].sum()),
                'monto_promedio': float(self.df['Total'].mean()),
                'monto_maximo': float(self.df['Total'].max()),
                'monto_minimo': float(self.df['Total'].min()),
                'vendedores_unicos': int(self.df['Vendedor'].nunique()),
                'clientes_unicos': int(self.df['Cliente'].nunique()),
                'estados': self.df['Estado'].value_counts().to_dict()
            }
            return resumen
        except Exception as e:
            print(f"✗ Error al calcular resumen: {e}")
            return None
    
    def obtener_ventas_json(self, limite=None):
        """Obtener ventas en formato JSON"""
        if self.df is None:
            print("✗ No hay datos cargados")
            return None
        
        try:
            df_salida = self.df.copy()
            
            if limite:
                df_salida = df_salida.head(limite)
            
            # Convertir a lista de diccionarios
            ventas = df_salida.to_dict('records')
            
            # Convertir valores NaN a None para JSON
            ventas_limpias = []
            for venta in ventas:
                venta_limpia = {}
                for key, value in venta.items():
                    if pd.isna(value):
                        venta_limpia[key] = None
                    else:
                        venta_limpia[key] = value
                ventas_limpias.append(venta_limpia)
            
            return ventas_limpias
        except Exception as e:
            print(f"✗ Error al convertir a JSON: {e}")
            return None
    
    def mostrar_primeras_ventas(self, cantidad=5):
        """Mostrar las primeras N ventas"""
        if self.df is None:
            print("✗ No hay datos cargados")
            return
        
        print(f"\n{'='*80}")
        print(f"PRIMERAS {cantidad} VENTAS")
        print(f"{'='*80}\n")
        
        for idx, fila in self.df.head(cantidad).iterrows():
            print(f"Orden #{idx + 1}")
            print(f"  Referencia: {fila['Referencia de la orden']}")
            print(f"  Cliente: {fila['Cliente']}")
            print(f"  Total: ${fila['Total']}")
            print(f"  Estado: {fila['Estado']}")
            print(f"  Fecha: {fila['Fecha de creación']}")
            print(f"  Vendedor: {fila['Vendedor']}")
            print()
    
    def guardar_json(self, nombre_archivo=str(DATA_DIR / 'ventas.json')):
        """Guardar datos en formato JSON"""
        try:
            ventas = self.obtener_ventas_json()
            if ventas:
                with open(nombre_archivo, 'w', encoding='utf-8') as f:
                    json.dump(ventas, f, ensure_ascii=False, indent=2)
                print(f"✓ Datos guardados en: {nombre_archivo}")
                return True
        except Exception as e:
            print(f"✗ Error al guardar JSON: {e}")
            return False


# Código de prueba
if __name__ == "__main__":
    print("=" * 80)
    print("LECTURA DE VENTAS DESDE CSV")
    print("=" * 80)
    
    # Crear lector
    lector = VentasReader()
    
    # Mostrar primeras 5 ventas
    lector.mostrar_primeras_ventas(5)
    
    # Mostrar resumen
    resumen = lector.obtener_resumen()
    if resumen:
        print("=" * 80)
        print("RESUMEN DE VENTAS")
        print("=" * 80)
        print(f"✓ Total de órdenes: {resumen['total_ordenes']}")
        print(f"✓ Monto total: ${resumen['monto_total']:,.2f}")
        print(f"✓ Monto promedio: ${resumen['monto_promedio']:,.2f}")
        print(f"✓ Monto máximo: ${resumen['monto_maximo']:,.2f}")
        print(f"✓ Monto mínimo: ${resumen['monto_minimo']:,.2f}")
        print(f"✓ Vendedores únicos: {resumen['vendedores_unicos']}")
        print(f"✓ Clientes únicos: {resumen['clientes_unicos']}")
        print(f"\n✓ Estados de órdenes:")
        for estado, cantidad in resumen['estados'].items():
            print(f"   - {estado}: {cantidad}")
    
    # Guardar en JSON
    lector.guardar_json()
