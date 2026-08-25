╔═══════════════════════════════════════════════════════════════════════════════╗
║                                                                               ║
║        🚀 GUÍA COMPLETA DE AUTOMATIZACIÓN - FRONTERA LIVING                   ║
║                    Análisis y Reportes de Ventas                              ║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝

═══════════════════════════════════════════════════════════════════════════════
1. REQUISITOS PREVIOS
═══════════════════════════════════════════════════════════════════════════════

✓ Python 3.10+ instalado
✓ Archivo CSV: "Orden de venta (sale.order).csv"
✓ Conexión a Internet (para Gemini AI - opcional)

Instalar dependencias (ejecutar 1 sola vez):
───────────────────────────────────────────
python -m pip install pandas openpyxl python-dotenv google-generativeai -q

═══════════════════════════════════════════════════════════════════════════════
2. AUTOMATIZACIÓN BÁSICA (RECOMENDADO)
═══════════════════════════════════════════════════════════════════════════════

El script "scripts\AUTOMATIZAR_TODO.py" hace TODO automáticamente:

PASO 1: Ejecutar el script maestro
────────────────────────────────────
Abre PowerShell en la carpeta del proyecto y ejecuta:

   python scripts\AUTOMATIZAR_TODO.py

PASO 2: Resultados automáticos
───────────────────────────────
Se generan automáticamente:

    ✓ REPORTE_VENTAS.xlsx
    ✓ REPORTE_EJECUTIVO.txt
    ✓ dashboard.html
    ✓ analisis_detallado.json

═══════════════════════════════════════════════════════════════════════════════
3. FLUJO DE TRABAJO AUTOMATIZADO
═══════════════════════════════════════════════════════════════════════════════

OPCIÓN A: Ejecución Manual (Cada vez que quieras generar reportes)
───────────────────────────────────────────────────────────────────

   1. Actualiza el CSV en "data\Orden de venta (sale.order).csv"
    2. Abre PowerShell en la carpeta
   3. Ejecuta: python scripts\AUTOMATIZAR_TODO.py
    4. Listo! Tienes todos los reportes

OPCIÓN B: Automatización Programada (Se ejecuta cada día a una hora)
───────────────────────────────────────────────────────────────────

WINDOWS (Recomendado):

    1. Abre "Programador de tareas" de Windows
    2. Crear tarea básica:
       - Nombre: "GenerarReportesVentas"
       - Acción: Ejecutar programa
       - Programa: python
       - Argumentos: C:\ruta\a\AUTOMATIZAR_TODO.py
       - Frecuencia: Diaria a las 6:00 AM

LINUX/MAC (En terminal):

    Editar crontab:
    $ crontab -e

    Agregar línea (ejecuta a las 6 AM diariamente):
    0 6 * * * cd /ruta/a/proyecto && python AUTOMATIZAR_TODO.py

OPCIÓN D: Excel nuevo en la carpeta (recomendado para Odoo)
─────────────────────────────────────────────────────────────

La tarea "Frontera Living Automatico" revisa "data" cada 15 minutos.
Cuando dejas allí un Excel nuevo exportado desde Odoo, el sistema:

   1. Detecta el Excel más reciente (ignora los reportes generados)
   2. Lo convierte automáticamente en "Orden de venta (sale.order).csv"
   3. Ejecuta AUTOMATIZAR_TODO.py
   4. Actualiza los archivos dentro de "reports" y el dashboard

La única acción manual que queda es exportar el Excel desde Odoo y guardarlo
en la carpeta "data". La descarga desde Odoo requiere una conexión/API o que el
usuario exporte el archivo.

OPCIÓN C: Integración con Google Drive
──────────────────────────────────────

(Próxima versión - Subirá reportes automáticamente a Google Drive)

═══════════════════════════════════════════════════════════════════════════════
4. PERSONALIZACIÓN DEL FLUJO
═══════════════════════════════════════════════════════════════════════════════

Si quieres SOLO algunos reportes, ejecuta:

Opción 1: Solo análisis rápido
    python analisis_completo.py

Opción 2: Solo Excel profesional
    python generar_reporte.py

Opción 3: Solo dashboard
    python -c "from generar_reporte import *; start('dashboard.html')"

═══════════════════════════════════════════════════════════════════════════════
5. ARCHIVOS EXPLICADOS
═══════════════════════════════════════════════════════════════════════════════

ENTRADA:
   data\Orden de venta (sale.order).csv  ← TU ARCHIVO ORIGINAL
   .env                             ← Configuración (GEMINI_API_KEY opcional)

SCRIPTS (Python):
   scripts\AUTOMATIZAR_TODO.py     ← 🎯 EJECUTA ESTE ARCHIVO
   scripts\generar_reporte.py      ← Genera Excel y reportes
   scripts\analisis_completo.py    ← Análisis detallado
   scripts\gemini_dashboard.py     ← Dashboard con IA (opcional)
   scripts\ventas_reader.py        ← Lector de CSV
   scripts\odoo_connector.py       ← Conexión Odoo (si la tienes)

SALIDA (Se generan automáticamente):
   reports\REPORTE_VENTAS.xlsx     ← Excel profesional con 6 hojas
   reports\REPORTE_EJECUTIVO.txt   ← Reporte en texto
   dashboard.html                   ← Gráficos interactivos
   reports\analisis_detallado.json ← Datos en JSON

═══════════════════════════════════════════════════════════════════════════════
6. VENTAJAS DEL SISTEMA AUTOMATIZADO
═══════════════════════════════════════════════════════════════════════════════

✅ NO necesitas subirme datos (todo local en tu PC)
✅ Se ejecuta automáticamente cada día
✅ Genera 4 reportes simultáneamente
✅ Cero dependencia de internet (menos Gemini)
✅ Puedes modificar los scripts a tu gusto
✅ Compatible con Windows, Mac, Linux

═══════════════════════════════════════════════════════════════════════════════
7. CONFIGURACIÓN AVANZADA
═══════════════════════════════════════════════════════════════════════════════

Usar Gemini AI para análisis automático:
────────────────────────────────────────

1. Obtén tu API Key gratis:
   → Ve a: https://aistudio.google.com/app/apikey
   → Copia tu GEMINI_API_KEY

2. Abre el archivo .env y reemplaza:
   GEMINI_API_KEY=TU_CLAVE_AQUI

3. Ejecuta:
   python gemini_dashboard.py

   Se generará:
   → dashboard/index.html (análisis con IA)

═══════════════════════════════════════════════════════════════════════════════
8. SOLUCIÓN DE PROBLEMAS
═══════════════════════════════════════════════════════════════════════════════

Error: "python: El término no se reconoce"
├─ Solución: Usa la ruta completa
├─ Ejecuta: C:\Python\python.exe AUTOMATIZAR_TODO.py
└─ O reinstala Python y marca "Add to PATH"

Error: "Archivo no encontrado: Orden de venta..."
├─ Solución: El CSV debe estar en la MISMA carpeta
├─ Verifica el NOMBRE exacto (mayúsculas, acentos)
└─ Ejecuta desde esa carpeta

Error: "ModuleNotFoundError: No module named 'pandas'"
├─ Solución: Instala las dependencias
└─ Ejecuta: python -m pip install pandas openpyxl -q

Error: "GEMINI_API_KEY inválida"
├─ Solución: Verificar que empiece con "AIza"
├─ Crear nueva key en: https://aistudio.google.com/app/apikey
└─ El campo GEMINI_API_KEY en .env debe estar exacto

═══════════════════════════════════════════════════════════════════════════════
9. FLUJO RECOMENDADO
═══════════════════════════════════════════════════════════════════════════════

SEMANA 1 (Setup):
   □ Copiar todos los archivos .py al proyecto
   □ Instalar dependencias: pip install pandas openpyxl
   □ Ejecutar: python AUTOMATIZAR_TODO.py
   □ Verificar que se generan los reportes

SEMANA 2+:
   □ Actualizar CSV con nuevos datos
   □ Ejecutar: python AUTOMATIZAR_TODO.py
   □ Revisar reportes (Excel, HTML, Texto)
   □ Compartir reportes con equipo

IMPLEMENTACIÓN AUTOMÁTICA:
   □ Configurar Programador de Tareas (Windows)
   □ O Cron (Linux/Mac)
   □ Olvidarse de ejecutar manualmente

═══════════════════════════════════════════════════════════════════════════════
10. CONTACTO Y SOPORTE
═══════════════════════════════════════════════════════════════════════════════

Sistema Independiente ✓
Todavía tienes duda sobre algo? Verifica:

   • Que Python está instalado: python --version
   • Que las dependencias están: pip list | findstr pandas
   • Que el CSV está en la carpeta correcta
   • Que ejecutas desde la carpeta del proyecto

Si quieres PERSONALIZAR:
   • Edita los scripts .py directamente
   • Puedes cambiar colores, formatos, campos
   • Todo es TUYO - no me necesitas más

═══════════════════════════════════════════════════════════════════════════════
RESUMEN FINAL
═══════════════════════════════════════════════════════════════════════════════

Para usar SIN mí:

    1. python AUTOMATIZAR_TODO.py  (1 comando)
    2. Espera 30 segundos
    3. Tienes 4 reportes profesionales
    4. Programar cron/scheduler para automatizar
    5. LISTO - Sistema 100% independiente

No necesitas:
    ✗ Subirme datos
    ✗ Llamarme cada vez
    ✗ Internet (para análisis básico)
    ✗ Depender de nada

Tienes:
    ✓ Sistema automatizado
    ✓ Reportes profesionales
    ✓ Control total
    ✓ Libertad completa

═══════════════════════════════════════════════════════════════════════════════

Última actualización: 14/08/2026
Frontera Living S.A - Sistema de Reportes Automatizado
