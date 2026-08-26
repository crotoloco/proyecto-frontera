import os
import requests
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
        self.url = (ODOO_URL or '').rstrip('/')
        self.db = ODOO_DB
        self.user = ODOO_USER
        self.password = ODOO_PASSWORD
        self.uid = None
        self.headers = {'Content-Type': 'application/json'}

    def _validar_configuracion(self):
        faltantes = [
            nombre for nombre, valor in {
                'ODOO_URL': self.url,
                'ODOO_DB': self.db,
                'ODOO_USER': self.user,
                'ODOO_PASSWORD': self.password,
            }.items() if not valor
        ]
        if faltantes:
            raise ValueError(f'Faltan variables de entorno: {", ".join(faltantes)}')

    def _llamar(self, payload):
        self._validar_configuracion()
        respuesta = requests.post(
            f'{self.url}/jsonrpc',
            json=payload,
            headers=self.headers,
            timeout=10,
        )
        respuesta.raise_for_status()
        cuerpo = respuesta.json()
        if cuerpo.get('error'):
            raise RuntimeError('Odoo devolvió un error JSON-RPC')
        return cuerpo.get('result')
    
    def conectar(self):
        """Conectar a Odoo y autenticarse usando JSON-RPC"""
        try:
            self._validar_configuracion()
            print(f"✓ Conectando a: {self.url}")
            print(f"✓ Base de datos: {self.db}")
            
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
            resultado = self._llamar(datos_auth)
            if resultado:
                self.uid = resultado
                print("✓ Autenticación exitosa")
                return True
            print("✗ Error de autenticación")
            return False
                
        except (requests.exceptions.RequestException, ValueError, RuntimeError) as error:
            print(f"✗ Error de conexión: {error}")
            return False
        except Exception as e:
            print(f"✗ Error de conexión: {e}")
            return False
    
    def obtener_ventas(self, limite=None):
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
                    'args': [
                        self.db, self.uid, self.password, 'sale.order', 'search', [],
                        {**({'limit': limite} if limite else {}), 'order': 'id desc'}
                    ]
                },
                'id': 2
            }
            
            ordenes_ids = self._llamar(datos_busqueda)
            if ordenes_ids is not None:
                
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
                    
                    return self._llamar(datos_lectura)
                else:
                    print("✓ No se encontraron órdenes de venta")
                    return []
        except (requests.exceptions.RequestException, ValueError, RuntimeError) as e:
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
