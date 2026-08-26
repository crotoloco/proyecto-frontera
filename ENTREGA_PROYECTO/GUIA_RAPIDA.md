# Guia rapida de uso

## Ventas

```powershell
.venv\Scripts\python.exe scripts\automatizar_cada_15_minutos.py --once
start dashboard.html
```

## Inventario

```powershell
.venv\Scripts\python.exe scripts\generar_inventario_html.py
start inventario.html
```

## Automatizacion continua

```powershell
.venv\Scripts\python.exe scripts\automatizar_cada_15_minutos.py
```

Detener con `Ctrl+C`.

## Dependencias

```powershell
.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## Problemas frecuentes

- Si falta `pandas`, instalar `requirements.txt`.
- Si no aparece inventario, revisar `data/Producto (product.template) (1).csv`.
- Si Odoo rechaza el acceso, revisar las variables de `.env` y los permisos.
- Si se usa un repositorio publico, quitar o anonimizar datos reales.
