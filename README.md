# Frontera Living - Automatizacion de ventas

Dashboard y reportes de ventas a partir de archivos exportados desde Odoo.

## Como funciona

1. Exportar las ventas desde Odoo en CSV o Excel.
2. Guardar el archivo en `data/`.
3. Ejecutar la automatizacion.
4. Revisar los resultados en `reports/` o abrir `dashboard.html`.

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
- `images.jpg`: logo de Frontera Living.

## Requisitos

- Python 3.10 o superior.
- `pandas` y `openpyxl`.

Instalacion:

```powershell
python -m pip install pandas openpyxl
```

El dashboard funciona localmente y no depende de la API de Gemini.
