"""Genera una vista HTML de inventario a partir de un export de productos."""

from __future__ import annotations

import html
import sys
from pathlib import Path

import pandas as pd


PROJECT_DIR = Path(__file__).resolve().parent.parent
DEFAULT_SOURCE = PROJECT_DIR / 'data' / 'product_template.xls'
OUTPUT = PROJECT_DIR / 'inventario.html'


def money(value):
    if pd.isna(value) or value == '':
        return 'Sin dato'
    return f'${float(value):,.2f}'


def main(source=DEFAULT_SOURCE):
    source = Path(source)
    if not source.exists():
        raise FileNotFoundError(f'No se encontró el export de productos: {source}')

    products = pd.read_excel(source)
    required = {'Name', 'Product Type', 'Internal Reference', 'Sales Price', 'Cost'}
    missing = required - set(products.columns)
    if missing:
        raise ValueError(f'Faltan columnas del export: {", ".join(sorted(missing))}')

    products = products.fillna('')
    rows = []
    for _, product in products.iterrows():
        rows.append(
            '<tr>'
            f'<td><strong>{html.escape(str(product["Name"]))}</strong></td>'
            f'<td>{html.escape(str(product["Internal Reference"]))}</td>'
            f'<td>{html.escape(str(product["Product Type"]))}</td>'
            f'<td class="number">{money(product["Sales Price"])}</td>'
            f'<td class="number">{money(product["Cost"])}</td>'
            '</tr>'
        )

    document = f'''<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Frontera Living · Inventario de productos</title>
<style>
:root {{ --ink:#202b2d; --muted:#667274; --paper:#f4f1ea; --panel:#fffdf8; --line:#d8d4c9; --accent:#1d6b69; --warm:#b8753e; }}
* {{ box-sizing:border-box; }}
body {{ margin:0; color:var(--ink); background:linear-gradient(135deg,#e8eee9,#f4f1ea 55%,#e7e0d4); font-family:Georgia,'Times New Roman',serif; }}
main {{ max-width:1180px; margin:0 auto; padding:42px 24px 64px; }}
header {{ display:flex; justify-content:space-between; gap:24px; align-items:end; border-bottom:2px solid var(--ink); padding-bottom:20px; }}
h1 {{ margin:0; font-size:clamp(30px,5vw,58px); line-height:.95; font-weight:500; }}
.kicker {{ color:var(--accent); font:700 12px Arial,sans-serif; letter-spacing:.12em; text-transform:uppercase; margin-bottom:10px; }}
.meta {{ color:var(--muted); font:13px Arial,sans-serif; max-width:280px; line-height:1.5; }}
.metrics {{ display:grid; grid-template-columns:repeat(3,1fr); gap:14px; margin:28px 0; }}
.metric {{ background:rgba(255,253,248,.78); border:1px solid var(--line); padding:20px; }}
.metric span {{ display:block; color:var(--muted); font:11px Arial,sans-serif; text-transform:uppercase; letter-spacing:.08em; }}
.metric strong {{ display:block; margin-top:8px; font-size:30px; font-weight:500; }}
.notice {{ border-left:4px solid var(--warm); background:rgba(255,253,248,.78); padding:16px 18px; margin:24px 0 30px; font:14px Arial,sans-serif; line-height:1.5; }}
section {{ background:var(--panel); border:1px solid var(--line); padding:22px; }}
.section-head {{ display:flex; justify-content:space-between; align-items:baseline; gap:16px; margin-bottom:16px; }}
h2 {{ margin:0; font-size:25px; font-weight:500; }}
.section-head span {{ color:var(--muted); font:12px Arial,sans-serif; }}
table {{ width:100%; border-collapse:collapse; font:14px Arial,sans-serif; }}
th {{ text-align:left; color:var(--muted); font-size:11px; text-transform:uppercase; letter-spacing:.06em; border-bottom:2px solid var(--ink); padding:10px 8px; }}
td {{ border-bottom:1px solid var(--line); padding:13px 8px; }}
.number {{ text-align:right; font-variant-numeric:tabular-nums; }}
@media(max-width:700px) {{ main {{ padding:28px 14px 40px; }} header {{ display:block; }} .meta {{ margin-top:18px; }} .metrics {{ grid-template-columns:1fr; }} section {{ overflow-x:auto; padding:14px; }} table {{ min-width:650px; }} }}
</style>
</head>
<body>
<main>
<header><div><div class="kicker">Frontera Living · Segunda vista</div><h1>Inventario<br>de productos</h1></div><div class="meta">Catálogo leído desde el export de inventario-productos-productos.<br>Fuente: {html.escape(source.name)}</div></header>
<div class="metrics"><div class="metric"><span>Productos</span><strong>{len(products)}</strong></div><div class="metric"><span>Precio promedio</span><strong>{money(pd.to_numeric(products['Sales Price'], errors='coerce').mean())}</strong></div><div class="metric"><span>Tipos de producto</span><strong>{products['Product Type'].nunique()}</strong></div></div>
<div class="notice"><strong>Ranking de más vendidos pendiente:</strong> este export contiene el catálogo, pero no incluye cantidades vendidas ni líneas de pedido. Para calcularlo hacen falta las columnas Producto y Cantidad desde Odoo. No se muestran datos inventados.</div>
<section><div class="section-head"><h2>Catálogo de productos</h2><span>{len(products)} registros del export</span></div><table><thead><tr><th>Producto</th><th>Referencia</th><th>Tipo</th><th class="number">Precio venta</th><th class="number">Costo</th></tr></thead><tbody>{''.join(rows)}</tbody></table></section>
</main>
</body>
</html>'''
    OUTPUT.write_text(document, encoding='utf-8')
    print(f'Inventario generado: {OUTPUT} ({len(products)} productos)')


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else DEFAULT_SOURCE)
