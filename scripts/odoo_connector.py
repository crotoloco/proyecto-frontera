import os
import requests
import json
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

# Obtener credenciales desde variables de entorno
ODOO_URL = os.getenv('ODOO_URL')
ODOO_DB = os.getenv('ODOO_DB')
ODOO_USER = os.getenv('ODOO_USER')
ODOO_PASSWORD = os.getenv('ODOO_PASSWORD')


class OdooConnector:
    def __init__(self):
        """Inicializar la conexión a Odoo"""
        self.url = ODOO_URL.rstrip('/')  # Quitar slash final si existe
        self.db = ODOO_DB
        self.user = ODOO_USER
        self.password = ODOO_PASSWORD
        self.uid = None
        self.headers = {'Content-Type': 'application/json'}
    
    def conectar(self):
        """Conectar a Odoo y autenticarse usando JSON-RPC"""
        try:
            print(f"✓ Conectando a: {self.url}")
            print(f"✓ Base de datos: {self.db}")
            print(f"✓ Usuario: {self.user}")
            
            # Datos de autenticación
            datos_auth = {
                'jsonrpc': '2.0',
                'method': 'call',
                'params': {
                    'service': 'common',
                    'method': 'authenticate',
                    'args': [self.db, self.user, self.password, {}]
                },
                'id': 1
            }
            
            # Realizar solicitud de autenticación
            respuesta = requests.post(
                f'{self.url}/jsonrpc',
                json=datos_auth,
                headers=self.headers,
                timeout=10
            )
            
            if respuesta.status_code == 200:
                resultado = respuesta.json()
                
                if 'result' in resultado and resultado['result']:
                    self.uid = resultado['result']
                    print(f"✓ Autenticación exitosa. UID: {self.uid}")
                    return True
                else:
                    print(f"✗ Error de autenticación: {resultado.get('error', 'Desconocido')}")
                    return False
            else:
                print(f"✗ Error HTTP {respuesta.status_code}")
                return False
                
        except requests.exceptions.ConnectionError:
            print(f"✗ Error: No se puede conectar a {self.url}")
            return False
        except Exception as e:
            print(f"✗ Error de conexión: {e}")
            return False
    
    def obtener_ventas(self, limite=10):
        """Obtener datos de ventas (sale.order)"""
        if not self.uid:
            print("✗ No estás conectado a Odoo. Ejecuta conectar() primero.")
            return None
        
        try:
            # Primero: buscar IDs de órdenes
            datos_busqueda = {
                'jsonrpc': '2.0',
                'method': 'call',
                'params': {
                    'service': 'object',
                    'method': 'execute_kw',
                    'args': [self.db, self.uid, self.password, 'sale.order', 'search', [], {'limit': limite}]
                },
                'id': 2
            }
            
            respuesta_busqueda = requests.post(
                f'{self.url}/jsonrpc',
                json=datos_busqueda,
                headers=self.headers,
                timeout=10
            )
            
            resultado_busqueda = respuesta_busqueda.json()
            
            if 'result' in resultado_busqueda:
                ordenes_ids = resultado_busqueda['result']
                
                if ordenes_ids:
                    print(f"✓ Se encontraron {len(ordenes_ids)} órdenes de venta")
                    
                    # Segundo: obtener detalles de las órdenes
                    datos_lectura = {
                        'jsonrpc': '2.0',
                        'method': 'call',
                        'params': {
                            'service': 'object',
                            'method': 'execute_kw',
                            'args': [
                                self.db, self.uid, self.password, 
                                'sale.order', 'read', 
                                [ordenes_ids],
                                {'fields': ['id', 'name', 'partner_id', 'amount_total', 'state', 'date_order']}
                            ]
                        },
                        'id': 3
                    }
                    
                    respuesta_lectura = requests.post(
                        f'{self.url}/jsonrpc',
                        json=datos_lectura,
                        headers=self.headers,
                        timeout=10
                    )
                    
                    resultado_lectura = respuesta_lectura.json()
                    
                    if 'result' in resultado_lectura:
                        return resultado_lectura['result']
                    else:
                        print(f"✗ Error al leer datos: {resultado_lectura.get('error', 'Desconocido')}")
                        return None
                else:
                    print("✓ No se encontraron órdenes de venta")
                    return []
            else:
                print(f"✗ Error en búsqueda: {resultado_busqueda.get('error', 'Desconocido')}")
                return None
                
        except Exception as e:
            print(f"✗ Error al obtener ventas: {e}")
            return None


# Código de prueba
if __name__ == "__main__":
    print("=" * 50)
    print("PRUEBA DE CONEXIÓN A ODOO (JSON-RPC)")
    print("=" * 50)
    
    # Crear conector
    conector = OdooConnector()
    
    # Intentar conectar
    if conector.conectar():
        print("\n" + "=" * 50)
        print("OBTENIENDO VENTAS")
        print("=" * 50)
        
        # Obtener últimas 5 ventas
        ventas = conector.obtener_ventas(limite=5)
        
        if ventas:
            print("\nPrimeras 5 ventas:")
            for venta in ventas:
                print(f"\n- Orden: {venta.get('name')}")
                print(f"  ID: {venta.get('id')}")
                print(f"  Cliente: {venta.get('partner_id')}")
                print(f"  Total: ${venta.get('amount_total')}")
                print(f"  Estado: {venta.get('state')}")
    else:
        print("\n✗ No se pudo conectar a Odoo")
