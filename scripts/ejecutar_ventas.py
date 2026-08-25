#!/usr/bin/env python
# Script para ejecutar el análisis de ventas

from ventas_reader import VentasReader

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
    print("\n" + "=" * 80)
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
print("\n" + "=" * 80)
lector.guardar_json()
print("=" * 80)
print("✓ Proceso completado exitosamente")
