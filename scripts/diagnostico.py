import os
import sys

print("=" * 80)
print("DIAGNÓSTICO DE PROYECTO")
print("=" * 80)

# Mostrar directorio actual
cwd = os.getcwd()
print(f"\n📁 Directorio actual: {cwd}")

# Listar archivos
print(f"\n📄 Archivos en el directorio:")
try:
    archivos = os.listdir(cwd)
    for archivo in archivos:
        ruta_completa = os.path.join(cwd, archivo)
        if os.path.isfile(ruta_completa):
            tamaño = os.path.getsize(ruta_completa)
            print(f"   - {archivo} ({tamaño} bytes)")
        else:
            print(f"   📁 {archivo}/")
except Exception as e:
    print(f"   ❌ Error al listar archivos: {e}")

# Verificar si existe el CSV
print(f"\n🔍 Buscando archivo CSV...")
csv_encontrado = False
for archivo in os.listdir(cwd):
    if archivo.endswith('.csv'):
        print(f"   ✓ Encontrado: {archivo}")
        csv_encontrado = True
        
        # Intentar cargar con pandas
        try:
            import pandas as pd
            df = pd.read_csv(archivo, encoding='utf-8')
            print(f"   ✓ Cargado exitosamente")
            print(f"   ✓ Filas: {len(df)}, Columnas: {len(df.columns)}")
            print(f"   ✓ Columnas: {list(df.columns)}")
        except Exception as e:
            print(f"   ❌ Error al cargar: {e}")

if not csv_encontrado:
    print(f"   ❌ No se encontró ningún archivo .csv")

print("\n" + "=" * 80)
