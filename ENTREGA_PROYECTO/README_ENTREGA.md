# Frontera Living
## Automatizacion, ventas e inventario

Repositorio oficial:
https://github.com/crotoloco/proyecto-frontera

Esta carpeta contiene la informacion necesaria para entregar, instalar,
ejecutar y presentar el proyecto.

## 1. Objetivo

El sistema recibe datos exportados desde Odoo, los procesa con Python y
Pandas, y genera reportes de ventas y vistas HTML para consultar la
informacion.

Flujo actual:

CSV/Excel de Odoo -> Python/Pandas -> reportes -> dashboard HTML

Tambien se preparo una fuente opcional mediante API JSON-RPC:

Odoo API -> normalizador -> mismo procesamiento existente -> reportes

El CSV/Excel se conserva como respaldo si Odoo no esta disponible.

## 2. Estructura principal

- `dashboard.html`: vista de ventas.
- `inventario.html`: vista de inventario y productos.
- `scripts/AUTOMATIZAR_TODO.py`: genera reportes de ventas.
- `scripts/automatizar_cada_15_minutos.py`: ejecuta el flujo cada 15 minutos.
- `scripts/generar_inventario_html.py`: genera la vista de inventario.
- `scripts/normalizador.py`: adapta datos de Odoo al formato del proyecto.
- `scripts/odoo_connector.py`: conector JSON-RPC opcional.
- `data/`: archivos exportados desde Odoo.
- `reports/`: Excel, JSON y reportes ejecutivos.
- `frontera_dashboard/`: modulo personalizado de Odoo.
- `docs/`: documentacion adicional.
- `.env.example`: plantilla de configuracion sin secretos.
- `.gitignore`: evita subir credenciales, entornos y logs.

## 3. Instalacion en Windows

Desde la carpeta raiz del proyecto:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Si PowerShell bloquea la activacion:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
.venv\Scripts\Activate.ps1
```

## 4. Dashboard de ventas

Ejecucion unica:

```powershell
.venv\Scripts\python.exe scripts\automatizar_cada_15_minutos.py --once
```

Abrir dashboard:

```powershell
start dashboard.html
```

Se generan:

- `reports/REPORTE_VENTAS.xlsx`
- `reports/REPORTE_EJECUTIVO.txt`
- `reports/analisis_detallado.json`
- `dashboard.html`

## 5. Automatizacion cada 15 minutos

```powershell
.venv\Scripts\python.exe scripts\automatizar_cada_15_minutos.py
```

El proceso busca un CSV o Excel nuevo en `data/`, actualiza el archivo
canonico y vuelve a generar los reportes. Se detiene con `Ctrl+C`.

Tambien existen los archivos `run_automatizador.bat`,
`ejecutar_automatizacion_15min.bat` y `run_automatizador_15min.ps1`.

## 6. Dashboard de inventario

La fuente actual es:

`data/Producto (product.template) (1).csv`

Generar la vista:

```powershell
.venv\Scripts\python.exe scripts\generar_inventario_html.py
```

Abrirla:

```powershell
start inventario.html
```

La vista contiene 80 productos, stock a la mano, stock pronosticado, estado
de disponibilidad, precio, costo, busqueda y filtro.

## 7. Productos mas vendidos

El archivo actual de inventario permite consultar stock, pero no ventas.
Los archivos actuales de ordenes tampoco incluyen producto ni cantidad.

Para calcular el ranking se necesita exportar desde Odoo lineas de pedido con:

- Producto
- Cantidad
- Fecha
- Estado

No se deben inventar rankings con los datos actuales.

## 8. Conexion opcional con Odoo

Copiar `.env.example` como `.env` y completar:

```env
ODOO_API_ENABLED=false
ODOO_URL=https://tu-instancia.odoo.com
ODOO_DB=tu_base_de_datos
ODOO_USER=tu_usuario
ODOO_PASSWORD=tu_contrasena
```

Para activar la API:

```env
ODOO_API_ENABLED=true
```

Si la conexion falla, se conserva el ultimo CSV valido.

La autenticacion contra la instancia real fue rechazada durante la prueba.
Hay que revisar usuario, contrasena, base, permisos y si Odoo requiere una
clave API.

## 9. Gemini

Gemini es opcional. El procesamiento local funciona sin Gemini.

```env
GEMINI_API_KEY=
GEMINI_MODEL=gemini-2.0-flash
```

Si Gemini falla, se usa el fallback local.

## 10. Seguridad

- Nunca subir `.env`.
- Nunca poner credenciales en el codigo.
- Cambiar la contrasena de Odoo que fue expuesta durante la configuracion.
- Mantener privado el repositorio porque contiene datos reales.
- No compartir CSV, Excel o reportes con clientes sin anonimizar.
- No imprimir respuestas completas de Odoo si contienen datos sensibles.

## 11. Estado del proyecto

Completado:

- Automatizacion de reportes.
- Dashboard de ventas.
- Vista profesional de inventario.
- Procesamiento local CSV/Excel.
- Normalizador de datos.
- Conector Odoo opcional.
- Fallback al ultimo CSV valido.
- Documentacion y repositorio GitHub.

Pendiente:

- Corregir autenticacion real de Odoo.
- Exportar lineas de pedido para ranking de mas vendidos.
- Agregar monitoreo y alertas avanzadas.

## 12. Presentacion al tutor

Explicacion breve:

> El proyecto automatiza el analisis de ventas exportadas desde Odoo. Lee
> archivos, procesa los datos con Python y Pandas, genera reportes en Excel,
> JSON y texto, y actualiza un dashboard web. Tambien incluye una vista de
> inventario con stock real exportado desde Odoo. El sistema puede ejecutarse
> manualmente o cada 15 minutos. La conexion API con Odoo esta preparada como
> segunda etapa y mantiene CSV/Excel como respaldo.

Demostracion:

1. Abrir el repositorio.
2. Ejecutar el comando de ventas.
3. Mostrar `dashboard.html`.
4. Mostrar los archivos de `reports/`.
5. Ejecutar el generador de inventario.
6. Mostrar `inventario.html`.
7. Explicar el fallback CSV y la conexion Odoo opcional.

## 13. GitHub

La rama publicada es `main`.

Ultimo estado sincronizado con:

https://github.com/crotoloco/proyecto-frontera
