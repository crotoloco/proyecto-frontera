"""Genera inventario.html desde un export de productos de Odoo."""
from __future__ import annotations
import html
import sys
from pathlib import Path
import pandas as pd

PROJECT_DIR = Path(__file__).resolve().parent.parent
DEFAULT_SOURCE = PROJECT_DIR / 'data' / 'Producto (product.template) (1).csv'
OUTPUT = PROJECT_DIR / 'inventario.html'


def money(value):
    if pd.isna(value) or value == '':
        return 'Sin dato'
    return f'${float(value):,.2f}'


def main(source=DEFAULT_SOURCE):
    source = Path(source)
    products = pd.read_csv(source, encoding='utf-8-sig').fillna('')
    required = {'Nombre', 'Cantidad a la mano', 'Cantidad pronosticada', 'Costo', 'Precio de venta'}
    missing = required - set(products.columns)
    if missing:
        raise ValueError(f'Faltan columnas: {", ".join(sorted(missing))}')

    hand = pd.to_numeric(products['Cantidad a la mano'], errors='coerce').fillna(0)
    forecast = pd.to_numeric(products['Cantidad pronosticada'], errors='coerce').fillna(0)
    rows = []
    for _, product in products.iterrows():
        stock = float(product['Cantidad a la mano']) if str(product['Cantidad a la mano']).strip() else 0
        predicted = float(product['Cantidad pronosticada']) if str(product['Cantidad pronosticada']).strip() else 0
        name = html.escape(str(product['Nombre']))
        reference = html.escape(str(product.get('Referencia interna', '')))
        state = 'ok' if stock > 0 else 'low'
        label = 'Disponible' if stock > 0 else 'Sin stock'
        rows.append(''.join([
            f'<tr data-name="{name.lower()}" data-ref="{reference.lower()}" data-stock="{state}">',
            f'<td><strong>{name}</strong></td><td class="ref">{reference or "—"}</td>',
            f'<td><span class="stock {state}">{label}</span></td>',
            f'<td class="number">{stock:,.0f}</td><td class="number">{predicted:,.0f}</td>',
            f'<td class="number">{money(product["Precio de venta"])}</td><td class="number">{money(product["Costo"])}</td></tr>'
        ]))

    css = '''<style>:root{--ink:#13272a;--muted:#657579;--bg:#f4f7f3;--card:#fff;--line:#dce5df;--teal:#087c78;--gold:#d79b51;--shadow:0 18px 50px #16373417}*{box-sizing:border-box}body{margin:0;color:var(--ink);background:radial-gradient(circle at 90% 0,#dcece1,transparent 32%),var(--bg);font-family:Inter,system-ui,-apple-system,"Segoe UI",sans-serif}.shell{max-width:1280px;margin:auto;padding:28px 24px 60px}.top{display:flex;justify-content:space-between;align-items:center;margin-bottom:42px}.brand{display:flex;align-items:center;gap:12px;font-weight:800}.mark{display:grid;place-items:center;width:38px;height:38px;border-radius:11px;background:var(--teal);color:#fff}.nav{display:flex;gap:8px}.nav a{padding:9px 13px;border:1px solid var(--line);border-radius:8px;color:var(--muted);font-size:13px;text-decoration:none}.nav a.active{background:var(--ink);color:#fff}.hero{display:grid;grid-template-columns:1.5fr .8fr;gap:28px;align-items:end;margin-bottom:30px}.eyebrow{margin:0 0 12px;color:var(--teal);font-size:12px;font-weight:800;letter-spacing:.13em;text-transform:uppercase}h1{margin:0;font-size:clamp(42px,7vw,82px);line-height:.9;letter-spacing:-.07em}.hero-copy{color:var(--muted);font-size:15px;line-height:1.55;border-left:3px solid var(--gold);padding-left:18px}.metrics{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin-bottom:26px}.metric,.panel{background:var(--card);border:1px solid var(--line);border-radius:14px;box-shadow:var(--shadow)}.metric{padding:20px 22px}.label{color:var(--muted);font-size:11px;font-weight:800;letter-spacing:.1em;text-transform:uppercase}.value{margin-top:10px;font-size:30px;font-weight:800;letter-spacing:-.05em}.note{margin-top:5px;color:var(--muted);font-size:12px}.notice{display:flex;gap:14px;background:#fff8ed;border:1px solid #efd9b8;border-left:4px solid var(--gold);border-radius:10px;padding:16px 18px;margin-bottom:26px;color:#704d2b;font-size:13px;line-height:1.5}.notice strong{display:block;color:#553718;margin-bottom:2px}.panel{overflow:hidden}.panel-head{display:flex;justify-content:space-between;gap:18px;align-items:end;padding:22px 24px 18px;border-bottom:1px solid var(--line)}h2{margin:0;font-size:22px}.panel-head p{margin:5px 0 0;color:var(--muted);font-size:13px}.controls{display:flex;gap:8px}.controls input,.controls select{height:36px;border:1px solid var(--line);border-radius:8px;padding:0 11px;background:#fbfdfb;color:var(--ink);font:inherit;font-size:12px}.controls input{width:220px}.table-wrap{overflow:auto}table{width:100%;border-collapse:collapse;min-width:900px}th{padding:12px 24px;text-align:left;background:#f7faf7;color:var(--muted);font-size:10px;letter-spacing:.1em;text-transform:uppercase}td{padding:14px 24px;border-top:1px solid var(--line);font-size:13px}td:first-child{font-weight:750}.ref{color:var(--teal);font-family:Consolas,monospace;font-size:12px}.stock{display:inline-block;padding:5px 8px;border-radius:999px;font-size:11px;font-weight:700}.stock.ok{background:#e7f2ee;color:#075450}.stock.low{background:#fbe9e5;color:#8b382e}.number{text-align:right;font-variant-numeric:tabular-nums}.empty{display:none;text-align:center;padding:30px;color:var(--muted);font-size:13px}.footer{display:flex;justify-content:space-between;color:var(--muted);font-size:12px;margin-top:18px}@media(max-width:760px){.shell{padding:20px 14px 42px}.top{align-items:flex-start}.hero{display:block}.hero h1{font-size:58px;margin-bottom:24px}.metrics{grid-template-columns:repeat(2,1fr)}.panel-head{display:block}.controls{margin-top:16px;display:grid;grid-template-columns:1fr 120px}.controls input{width:auto}.panel-head,th,td{padding-left:16px;padding-right:16px}.footer{display:block;line-height:1.7}}@media(max-width:450px){.metrics{grid-template-columns:1fr}}</style>'''
    js = '''<script>const s=document.getElementById('search'),t=document.getElementById('stock'),r=[...document.querySelectorAll('#products tr')],e=document.getElementById('empty');function filter(){const q=s.value.toLowerCase(),v=t.value;let n=0;r.forEach(x=>{const ok=(!q||x.dataset.name.includes(q)||x.dataset.ref.includes(q))&&(!v||x.dataset.stock===v);x.hidden=!ok;if(ok)n++});e.style.display=n?'none':'block'}s.addEventListener('input',filter);t.addEventListener('change',filter);</script>'''
    document = '<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Frontera Living | Inventario</title>' + css + '</head><body><main class="shell"><header class="top"><div class="brand"><span class="mark">FL</span><span>Frontera Living</span></div><nav class="nav"><a href="dashboard.html">Ventas</a><a class="active" href="inventario.html">Inventario</a></nav></header><section class="hero"><div><p class="eyebrow">Segunda vista · Operaciones</p><h1>Inventario<br>de productos</h1></div><p class="hero-copy">Stock actual y stock pronosticado a partir del export de productos de Odoo.</p></section><section class="metrics"><article class="metric"><div class="label">Productos</div><div class="value">' + str(len(products)) + '</div><div class="note">Registros del export</div></article><article class="metric"><div class="label">Stock disponible</div><div class="value">' + f'{hand.sum():,.0f}' + '</div><div class="note">Unidades a la mano</div></article><article class="metric"><div class="label">Stock pronosticado</div><div class="value">' + f'{forecast.sum():,.0f}' + '</div><div class="note">Proyección de Odoo</div></article><article class="metric"><div class="label">Sin stock</div><div class="value">' + str(int((hand <= 0).sum())) + '</div><div class="note">Requieren atención</div></article></section><aside class="notice"><span>!</span><div><strong>Ranking de más vendidos pendiente</strong>Este export permite analizar stock, pero no cantidad vendida. Para el ranking necesitamos líneas de pedido con Producto y Cantidad.</div></aside><section class="panel"><div class="panel-head"><div><h2>Inventario actual</h2><p>' + str(len(products)) + ' productos · precio promedio ' + money(pd.to_numeric(products['Precio de venta'], errors='coerce').mean()) + '</p></div><div class="controls"><input id="search" type="search" placeholder="Buscar producto o referencia"><select id="stock"><option value="">Todo el stock</option><option value="ok">Disponibles</option><option value="low">Sin stock</option></select></div></div><div class="table-wrap"><table><thead><tr><th>Producto</th><th>Referencia</th><th>Estado</th><th class="number">A la mano</th><th class="number">Pronosticado</th><th class="number">Precio venta</th><th class="number">Costo</th></tr></thead><tbody id="products">' + ''.join(rows) + '</tbody></table><div id="empty" class="empty">No encontramos productos con esos filtros.</div></div></section><div class="footer"><span>Fuente: Producto (product.template) (1).csv</span><span>Frontera Living · Panel operativo</span></div></main>' + js + '</body></html>'
    OUTPUT.write_text(document, encoding='utf-8')
    print(f'Inventario generado: {OUTPUT} ({len(products)} productos)')


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else DEFAULT_SOURCE)
