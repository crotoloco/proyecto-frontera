# Frontera Living - Automatizacion de ventas

Dashboard y reportes de ventas a partir de archivos exportados desde Odoo.

## Como funciona

1. Exportar las ventas desde Odoo en CSV o Excel.
2. Guardar el archivo en `data/`.
3. Ejecutar la automatizacion.
4. Revisar los resultados en `reports/` o abrir `dashboard.html`.

La segunda etapa agrega una fuente Odoo opcional mediante JSON-RPC. El
procesamiento existente no cambia: la respuesta de Odoo se normaliza al mismo
formato que el CSV y, si Odoo falla, se conserva el ultimo CSV valido.

## Ejecucion manual

Desde la carpeta del proyecto:

```powershell
python scripts\automatizar_cada_15_minutos.py --once
```

Para dejar el proceso corriendo cada 15 minutos:

```powershell
python scripts\automatizar_cada_15_minutos.py
```

## Carpetas

- `data/`: archivos de entrada exportados desde Odoo.
- `scripts/`: programas Python.
- `reports/`: Excel, JSON y reportes generados.
- `docs/`: documentacion adicional.
- `dashboard.html`: dashboard de una sola pagina.
- `inventario.html`: vista separada del catalogo de productos.
- `images.jpg`: logo de Frontera Living.

## Requisitos

- Python 3.10 o superior.
- Dependencias indicadas en `requirements.txt`.

Instalacion:

```powershell
python -m pip install -r requirements.txt
```

## Vista de inventario

Para generar la vista de productos desde un export `.xls`:

```powershell
python scripts\generar_inventario_html.py C:\ruta\product_template.xls
```

Esto genera `inventario.html` con los productos, referencias, tipo, precio y
costo. El ranking de productos mas vendidos requiere un export de lineas de
pedido que incluya producto y cantidad; el archivo de catalogo no contiene esa
informacion.

El dashboard funciona localmente y no depende de la API de Gemini.

## Conexion opcional con Odoo

1. Copiar `.env.example` como `.env`.
2. Completar `ODOO_URL`, `ODOO_DB`, `ODOO_USER` y `ODOO_PASSWORD`.
3. Cambiar `ODOO_API_ENABLED=false` a `ODOO_API_ENABLED=true`.
4. Ejecutar una prueba unica:

```powershell
python scripts\automatizar_cada_15_minutos.py --once
```

Con la API habilitada, el automatizador intenta consultar `sale.order` y
actualiza el CSV canonico solo cuando la respuesta es valida. Si la conexión,
autenticacion o normalizacion fallan, utiliza el ultimo archivo valido y
continua con el procesamiento local.

Las credenciales reales deben permanecer en `.env`, que esta excluido por
`.gitignore`. No subir datos reales de clientes a un repositorio publico.
