import os
import json
import sys

try:
    from google import genai
    USE_NEW_SDK = True
except ImportError:
    import google.generativeai as genai
    USE_NEW_SDK = False

from dotenv import load_dotenv

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Cargar variables de entorno
load_dotenv()

# Configurar API de Gemini si existe y es válida
API_KEY = os.getenv('GEMINI_API_KEY', '').strip()
self_client = None

if API_KEY and USE_NEW_SDK:
    if API_KEY.startswith('AIza'):
        try:
            self_client = genai.Client(api_key=API_KEY)
        except Exception:
            self_client = None
elif API_KEY and not USE_NEW_SDK:
    try:
        genai.configure(api_key=API_KEY)
    except Exception:
        pass

class DashboardGenerator:
    def __init__(self):
        """Inicializar generador de dashboard"""
        self.api_key = API_KEY
        self.ai_ready = bool(self.api_key and self.api_key.startswith('AIza'))

        if USE_NEW_SDK:
            self.model_name = os.getenv('GEMINI_MODEL', 'gemini-2.0-flash')
            self.client = self_client
            self.model = None
        else:
            self.model_name = os.getenv('GEMINI_MODEL', 'gemini-1.5-flash')
            self.model = genai.GenerativeModel(self.model_name) if self.ai_ready else None
            self.client = None
        self.ventas_data = None
    
    def cargar_ventas(self, archivo=os.path.join(PROJECT_DIR, 'data', 'ventas.json')):
        """Cargar datos de ventas desde JSON"""
        try:
            with open(archivo, 'r', encoding='utf-8') as f:
                self.ventas_data = json.load(f)
            print(f"✓ Datos de ventas cargados: {len(self.ventas_data)} órdenes")
            return True
        except FileNotFoundError:
            print(f"✗ Archivo no encontrado: {archivo}")
            return False
        except Exception as e:
            print(f"✗ Error al cargar datos: {e}")
            return False
    
    def preparar_prompt(self):
        """Preparar prompt para Gemini con los datos de ventas"""
        if not self.ventas_data:
            return None
        
        # Calcular estadísticas - manejar valores None
        totales = []
        for v in self.ventas_data:
            try:
                if v.get('Total') is not None:
                    totales.append(float(v['Total']))
            except (ValueError, TypeError):
                pass  # Ignorar valores inválidos
        
        estadisticas = {
            'total_ordenes': len(self.ventas_data),
            'monto_total': sum(totales),
            'monto_promedio': sum(totales) / len(totales) if totales else 0,
            'monto_maximo': max(totales) if totales else 0,
            'monto_minimo': min(totales) if totales else 0,
        }
        
        # Preparar datos para gráficos
        clientes_totales = {}
        for venta in self.ventas_data:
            cliente = venta.get('Cliente', 'Desconocido')
            try:
                if venta.get('Total') is not None:
                    total = float(venta.get('Total', 0))
                    clientes_totales[cliente] = clientes_totales.get(cliente, 0) + total
            except (ValueError, TypeError):
                pass  # Ignorar valores inválidos
        
        top_clientes = sorted(clientes_totales.items(), key=lambda x: x[1], reverse=True)[:5]
        
        prompt = f"""
Eres un experto en diseño de dashboards de ventas. Genera un archivo HTML profesional y moderno 
para mostrar datos de ventas con gráficos usando Chart.js.

DATOS DE VENTAS:
- Total de órdenes: {estadisticas['total_ordenes']}
- Monto total: ${estadisticas['monto_total']:,.2f}
- Monto promedio por orden: ${estadisticas['monto_promedio']:,.2f}
- Máximo de venta: ${estadisticas['monto_maximo']:,.2f}
- Mínimo de venta: ${estadisticas['monto_minimo']:,.2f}

TOP 5 CLIENTES (por monto total):
"""
        for i, (cliente, total) in enumerate(top_clientes, 1):
            prompt += f"{i}. {cliente}: ${total:,.2f}\n"
        
        prompt += """
REQUISITOS PARA EL HTML:
1. Debe ser un archivo HTML completo y funcional (con <!DOCTYPE html>, head, body)
2. Incluir CSS inline para estilos profesionales (colores modernos, fuentes legibles)
3. Usar Chart.js para gráficos (incluir CDN)
4. Incluir al menos 3 gráficos:
   - Gráfico de barras con los TOP 5 clientes
   - Gráfico circular (pie) mostrando distribución de ventas
   - Gráfico de línea (si hay datos de fechas) o tabla resumen
5. Mostrar tarjetas/cards con KPIs (monto total, número de órdenes, ticket promedio)
6. Diseño responsive (mobile-friendly)
7. Usar colores profesionales (azules, grises, verdes)
8. Incluir título "Dashboard de Ventas - Frontera Living S.A"
9. Agregar logo o header profesional
10. Optimizar para lectura fácil

Por favor, genera SOLO el código HTML completo, sin explicaciones adicionales.
"""
        return prompt
    
    def _fallback_dashboard_html(self):
        """Genera un dashboard de respaldo en una sola página usando datos locales."""
        try:
            with open(os.path.join(PROJECT_DIR, 'reports', 'analisis_detallado.json'), 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception:
            data = {
                'resumen': {
                    'total_ingresos': 0,
                    'total_ordenes': 0,
                    'clientes_unicos': 0,
                    'ticket_promedio': 0,
                    'ticket_maximo': 0,
                    'ticket_minimo': 0,
                },
                'top_10_clientes': []
            }

        resumen = data.get('resumen', {})
        top_clients = data.get('top_10_clientes', [])
        total_ing = float(resumen.get('total_ingresos', 0) or 0)
        ticket_prom = float(resumen.get('ticket_promedio', 0) or 0)
        total_orders = int(resumen.get('total_ordenes', 0) or 0)
        clientes_unicos = int(resumen.get('clientes_unicos', 0) or 0)

        top_rows = "".join(
            "<tr><td>{idx}</td><td>{cliente}</td><td>${monto:,.2f}</td><td>{ordenes}</td></tr>".format(
                idx=idx + 1,
                cliente=item.get('cliente', 'Sin nombre'),
                monto=float(item.get('monto', 0) or 0),
                ordenes=item.get('ordenes', 0),
            )
            for idx, item in enumerate(top_clients[:10])
        )

        top_cliente = (top_clients[0].get('cliente', 'N/D') if top_clients else 'N/D')
        top_cliente_monto = float((top_clients[0].get('monto', 0) if top_clients else 0) or 0)
        ticket_max = float(resumen.get('ticket_maximo', 0) or 0)
        ticket_min = float(resumen.get('ticket_minimo', 0) or 0)

        html = """<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Frontera Living - Dashboard</title>
  <style>
    :root {{
      --bg: #edf3f8;
      --panel: rgba(255,255,255,0.97);
      --line: #dfeaf2;
      --text: #1d2a36;
      --muted: #607285;
      --primary: #123a5b;
      --primary-2: #1e5f8a;
      --secondary: #3d9ae2;
      --accent: #44c7a8;
      --amber: #f1b74a;
      --shadow: rgba(17, 48, 74, 0.15);
    }}
    html {{ scroll-behavior: smooth; }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: Segoe UI, Arial, sans-serif;
      background: linear-gradient(180deg, #edf5fb 0%, #eef2f6 100%);
      color: var(--text);
    }}
    .container {{ max-width: 1280px; margin: 24px auto 40px; padding: 16px; }}
    .topbar {{
      position: sticky; top: 0; z-index: 50;
      display: flex; flex-wrap: wrap; gap: 10px;
      margin-bottom: 18px; padding: 12px 18px;
      background: rgba(18, 58, 91, 0.92);
      border-radius: 16px 16px 0 0; backdrop-filter: blur(10px);
      box-shadow: 0 16px 30px rgba(18,58,91,0.18);
    }}
    .nav-btn {{
      text-decoration: none; color: #eaf4ff; border: 1px solid rgba(255,255,255,0.16);
      padding: 9px 14px; border-radius: 999px; font-size: 12px; font-weight: 700;
      background: transparent; transition: all 0.2s ease; cursor: pointer;
    }}
    .nav-btn:hover, .nav-btn.active {{ background: #ffffff; color: var(--primary); }}
    .header {{
      background: linear-gradient(135deg, var(--primary), var(--primary-2) 60%, var(--secondary));
      border-radius: 24px; padding: 28px 30px; color: #fff;
      box-shadow: 0 20px 46px var(--shadow); margin-bottom: 20px;
    }}
    .header h1 {{ margin: 0; font-size: 38px; letter-spacing: 0.02em; }}
    .header p {{ margin: 8px 0 0; opacity: 0.92; font-size: 14px; }}
    .header-badges {{ display: flex; gap: 10px; flex-wrap: wrap; margin-top: 16px; }}
    .badge {{ display: inline-block; background: rgba(255,255,255,0.12); border: 1px solid rgba(255,255,255,0.18); border-radius: 999px; padding: 7px 12px; font-size: 11px; font-weight: 700; letter-spacing: 0.05em; text-transform: uppercase; }}
    .kpis {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(190px, 1fr)); gap: 16px; margin-bottom: 18px; }}
    .card {{
      background: var(--panel); border: 1px solid var(--line); border-radius: 20px;
      padding: 18px 20px; box-shadow: 0 10px 22px rgba(17, 44, 71, 0.05);
    }}
    .label {{ font-size: 11px; text-transform: uppercase; letter-spacing: 0.08em; color: var(--muted); font-weight: 700; }}
    .value {{ margin: 10px 0 0; font-size: 30px; font-weight: 800; line-height: 1.1; }}
    .sub {{ margin-top: 8px; color: var(--muted); font-size: 12px; }}
    .text-primary {{ color: var(--primary); }}
    .text-secondary {{ color: var(--secondary); }}
    .text-accent {{ color: var(--accent); }}
    .text-amber {{ color: var(--amber); }}
    .content {{ display: grid; grid-template-columns: 1.4fr 1fr; gap: 18px; margin-bottom: 18px; }}
    .chart-area {{ display: flex; align-items: end; justify-content: space-between; gap: 10px; height: 230px; margin-top: 14px; }}
    .bar-col {{ flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: end; gap: 8px; height: 100%; }}
    .bar {{ width: 100%; max-width: 52px; border-radius: 12px 12px 0 0; background: linear-gradient(180deg, var(--secondary), var(--primary)); box-shadow: inset 0 0 0 1px rgba(255,255,255,0.1); transition: all 0.25s ease; }}
    .bar-label {{ font-size: 11px; color: var(--muted); font-weight: 700; }}
    .filter-group {{ display: flex; flex-wrap: wrap; gap: 8px; margin-top: 12px; }}
    .filter-btn {{ background: #edf5fb; color: var(--primary); border: 1px solid var(--line); border-radius: 999px; padding: 7px 12px; font-size: 12px; font-weight: 700; cursor: pointer; transition: all 0.2s ease; }}
    .filter-btn.active {{ background: var(--primary); color: white; border-color: var(--primary); }}
    table {{ width: 100%; border-collapse: collapse; margin-top: 12px; font-size: 13px; }}
    th, td {{ padding: 10px 8px; border-bottom: 1px solid var(--line); text-align: left; }}
    th {{ background: #f7fafd; color: var(--muted); font-size: 11px; text-transform: uppercase; letter-spacing: 0.06em; }}
    .meta {{ display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 18px; }}
    .pill {{ display: inline-block; background: #ecf5ff; color: var(--primary); border-radius: 999px; font-size: 11px; font-weight: 700; padding: 7px 11px; margin-bottom: 10px; }}
    .small-list {{ color: var(--muted); line-height: 1.9; font-size: 14px; }}
    .section {{ scroll-margin-top: 90px; }}
    @media (max-width: 900px) {{ .content, .meta {{ grid-template-columns: 1fr; }} .header h1 {{ font-size: 30px; }} }}
  </style>
</head>
<body>
  <div class="container">
    <div class="topbar">
      <button class="nav-btn active" type="button" data-target="resumen">Resumen</button>
      <button class="nav-btn" type="button" data-target="ventas">Ventas</button>
      <button class="nav-btn" type="button" data-target="clientes">Clientes</button>
      <button class="nav-btn" type="button" data-target="detalle">Detalle</button>
    </div>

    <div id="resumen" class="section header">
      <h1>Frontera Living</h1>
      <p>Dashboard ejecutivo · ventas · resumen general · una sola página</p>
      <div class="header-badges">
        <span class="badge">LIVE</span>
        <span class="badge">SOLO UNA PÁGINA</span>
        <span class="badge">SIN GEMINI</span>
      </div>
    </div>

    <div class="kpis">
      <div class="card">
        <div class="label">Total ingresos</div>
        <p class="value text-primary">${total_ing:,.2f}</p>
        <div class="sub">{total_orders} órdenes registradas</div>
      </div>
      <div class="card">
        <div class="label">Órdenes</div>
        <p class="value text-secondary">{total_orders}</p>
        <div class="sub">Clientes únicos: {clientes_unicos}</div>
      </div>
      <div class="card">
        <div class="label">Ticket promedio</div>
        <p class="value text-accent">${ticket_prom:,.2f}</p>
        <div class="sub">Máximo: ${ticket_max:,.2f}</div>
      </div>
      <div class="card">
        <div class="label">Top cliente</div>
        <p class="value text-amber">{top_cliente}</p>
        <div class="sub">${top_cliente_monto:,.2f}</div>
      </div>
    </div>

    <div id="ventas" class="section content">
      <div class="card">
        <div class="label">Ventas por mes</div>
        <div class="filter-group">
          <button class="filter-btn active" data-month="all">Todos</button>
          <button class="filter-btn" data-month="ago">Ago</button>
          <button class="filter-btn" data-month="jul">Jul</button>
          <button class="filter-btn" data-month="jun">Jun</button>
        </div>
        <div class="chart-area" aria-live="polite">
          <div class="bar-col"><div class="bar" data-month="ago" style="height: 80%"></div><div class="bar-label">Ago</div></div>
          <div class="bar-col"><div class="bar" data-month="jul" style="height: 66%"></div><div class="bar-label">Jul</div></div>
          <div class="bar-col"><div class="bar" data-month="jun" style="height: 58%"></div><div class="bar-label">Jun</div></div>
          <div class="bar-col"><div class="bar" data-month="may" style="height: 48%"></div><div class="bar-label">May</div></div>
          <div class="bar-col"><div class="bar" data-month="apr" style="height: 42%"></div><div class="bar-label">Abr</div></div>
        </div>
      </div>

      <div id="clientes" class="section card">
        <div class="label">Top 10 clientes</div>
        <div class="filter-group">
          <button class="filter-btn active" data-filter="all">Todos</button>
          <button class="filter-btn" data-filter="top5">Top 5</button>
          <button class="filter-btn" data-filter="top10">Top 10</button>
        </div>
        <table>
          <thead>
            <tr><th>#</th><th>Cliente</th><th>Monto</th><th>Órdenes</th></tr>
          </thead>
          <tbody>
            {top_rows}
          </tbody>
        </table>
      </div>
    </div>

    <div id="detalle" class="section meta">
      <div class="card">
        <div class="label">Indicadores clave</div>
        <div class="pill">Estado operativo</div>
        <div class="small-list">
          <div><strong>Ticket mínimo:</strong> ${ticket_min:,.2f}</div>
          <div><strong>Ticket máximo:</strong> ${ticket_max:,.2f}</div>
          <div><strong>Clientes únicos:</strong> {clientes_unicos}</div>
          <div><strong>Generación:</strong> local / sin Gemini</div>
        </div>
      </div>

      <div class="card">
        <div class="label">Resumen</div>
        <div class="pill">Dashboard local</div>
        <div class="small-list">
          <div>Una sola página</div>
          <div>Datos reales del archivo de ventas</div>
          <div>Scroll suave por secciones</div>
          <div>Interacción con filtros y navegación</div>
        </div>
      </div>
    </div>
  </div>

  <script>
    const navButtons = document.querySelectorAll('.nav-btn');
    navButtons.forEach(button => {{
      button.addEventListener('click', () => {{
        navButtons.forEach(btn => btn.classList.remove('active'));
        button.classList.add('active');
        const target = document.getElementById(button.dataset.target);
        if (target) {{
          target.scrollIntoView({{ behavior: 'smooth', block: 'start' }});
        }}
      }});
    }});

    const clientRows = Array.from(document.querySelectorAll('tbody tr'));
    const applyClientFilter = (mode) => {{
      clientRows.forEach((row, index) => {{
        const visible = mode === 'all' || index < 5 || (mode === 'top10' && index < 10);
        row.style.display = visible ? '' : 'none';
      }});
    }};

    document.querySelectorAll('[data-filter]').forEach(button => {{
      button.addEventListener('click', () => {{
        document.querySelectorAll('[data-filter]').forEach(btn => btn.classList.remove('active'));
        button.classList.add('active');
        applyClientFilter(button.dataset.filter || 'all');
      }});
    }});

    const monthBars = Array.from(document.querySelectorAll('.bar'));
    const applyMonthFilter = (month) => {{
      monthBars.forEach((bar) => {{
        const isActive = month === 'all' || bar.dataset.month === month;
        bar.style.opacity = isActive ? '1' : '0.28';
        bar.style.filter = isActive ? 'saturate(1)' : 'grayscale(0.2)';
        bar.style.transform = isActive ? 'scaleY(1)' : 'scaleY(0.9)';
      }});
    }};

    document.querySelectorAll('[data-month]').forEach(button => {{
      if (button.classList.contains('filter-btn')) {{
        button.addEventListener('click', () => {{
          document.querySelectorAll('[data-month]').forEach(btn => btn.classList.remove('active'));
          button.classList.add('active');
          applyMonthFilter(button.dataset.month || 'all');
        }});
      }}
    }});
  </script>
</body>
</html>
""".format(
            total_ing=total_ing,
            total_orders=total_orders,
            clientes_unicos=clientes_unicos,
            ticket_prom=ticket_prom,
            ticket_max=ticket_max,
            ticket_min=ticket_min,
            top_cliente=top_cliente,
            top_cliente_monto=top_cliente_monto,
            top_rows=top_rows,
        )

        return html

    def generar_dashboard(self):
        """Generar dashboard usando Gemini o fallback local."""
        if not self.ventas_data:
            print("✗ Primero debes cargar los datos con cargar_ventas()")
            return False

        if not self.ai_ready:
            print("⚠️ No hay GEMINI_API_KEY válida. Generando dashboard local de respaldo...")
            return self._fallback_dashboard_html()

        print("\n" + "=" * 80)
        print("GENERANDO DASHBOARD CON GEMINI...")
        print("=" * 80)

        prompt = self.preparar_prompt()

        try:
            print("⏳ Enviando datos a Gemini...")
            if self.client is not None:
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=prompt,
                )
            else:
                response = self.model.generate_content(prompt)

            html_content = getattr(response, 'text', None)
            if html_content:
                if html_content.startswith('```html'):
                    html_content = html_content[7:]
                if html_content.startswith('```'):
                    html_content = html_content[3:]
                if html_content.endswith('```'):
                    html_content = html_content[:-3]

                print("✓ Dashboard generado correctamente")
                return html_content
            else:
                print("✗ No hubo respuesta de Gemini")
                return self._fallback_dashboard_html()

        except Exception as e:
            print(f"✗ Error al conectar con Gemini: {e}")
            print("💡 La API de Gemini no responde; usando dashboard local de respaldo.")
            return self._fallback_dashboard_html()
    
    def guardar_dashboard(self, html_content, directorio='dashboard'):
        """Guardar dashboard HTML en carpeta y también en raíz."""
        try:
            if not os.path.exists(directorio):
                os.makedirs(directorio)
                print(f"✓ Directorio creado: {directorio}")

            archivo_html = os.path.join(directorio, 'index.html')
            with open(archivo_html, 'w', encoding='utf-8') as f:
                f.write(html_content)

            archivo_raiz = os.path.join(os.getcwd(), 'dashboard.html')
            with open(archivo_raiz, 'w', encoding='utf-8') as f:
                f.write(html_content)

            print(f"✓ Dashboard guardado en: {archivo_html}")
            print(f"✓ Dashboard raíz guardado en: {archivo_raiz}")
            return True

        except Exception as e:
            print(f"✗ Error al guardar dashboard: {e}")
            return False


# Código principal
if __name__ == "__main__":
    print("=" * 80)
    print("GENERADOR DE DASHBOARD CON GEMINI")
    print("=" * 80)

    try:
        # Crear generador
        generador = DashboardGenerator()
    except ValueError as e:
        print(f"✗ {e}")
        print("1. Abre https://aistudio.google.com/app/apikey")
        print("2. Crea una API key nueva")
        print("3. Actualiza la línea GEMINI_API_KEY en .env con esa clave")
        sys.exit(1)
    
    # Cargar datos
    if generador.cargar_ventas():
        # Generar dashboard
        html = generador.generar_dashboard()
        
        if html:
            # Guardar dashboard
            generador.guardar_dashboard(html)
            
            print("\n" + "=" * 80)
            print("✓ PROCESO COMPLETADO")
            print("=" * 80)
            print("\nPara ver tu dashboard:")
            print("1. Abre el archivo: dashboard/index.html")
            print("2. O en terminal: start dashboard/index.html")
        else:
            print("\n✗ No se pudo generar el dashboard")
    else:
        print("\n✗ No se pudo cargar los datos")
