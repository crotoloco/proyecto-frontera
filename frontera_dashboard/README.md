# Dashboard Ejecutivo Frontera Living

## 📊 Descripción

Módulo custom de Odoo 16.0+ que proporciona un **dashboard ejecutivo en tiempo real** con KPIs de:
- **Ventas**: ingresos, órdenes confirmadas, cotizaciones, entregas
- **Inventario**: recepciones, traslados, órdenes de entrega pendientes
- **Producción**: órdenes en espera, en progreso, completadas
- **Reparaciones**: confirmadas, en proceso, completadas

## 🚀 Instalación Rápida

### Paso 1: Copiar el módulo a tu instancia de Odoo
```bash
# En tu servidor Odoo, dentro de la carpeta addons:
cp -r frontera_dashboard /ruta/a/tu/odoo/addons/
```

### Paso 2: Instalar en Odoo
1. Ir a **Apps** en tu instancia de Odoo
2. Buscar "Frontera Dashboard"
3. Hacer clic en **Instalar**

### Paso 3: Activar el cron (automático)
- El módulo incluye un **cron que se ejecuta cada 30 minutos**
- Los datos se actualizan automáticamente
- Puedes cambiar la frecuencia en **Configuración > Trabajos Programados**

## 📱 Cómo Usar

### Acceder al Dashboard
1. Después de instalar, aparecerá en el menú: **📊 Frontera Dashboard**
2. Hacer clic en **Dashboard Ejecutivo**

### Vistas Disponibles
- **Vista Kanban** (por defecto): Cards visuales con KPIs por categoría
- **Vista de Lista**: Tabla con todos los datos
- **Vista de Formulario**: Detalles completos de cada KPI
- **Inventario de productos**: existencias, disponible, por recibir y por entregar

### Filtros y Búsqueda
- Filtrar por **Categoría**: Ventas, Inventario, Producción, Reparaciones
- Filtrar por **Estado**: Crítico 🔴, Atención 🟡, Bien 🟢
- Agrupar por categoría o estado

### Actualizar Manualmente
Si necesitas forzar una actualización inmediata:
1. Ir a **Frontera Dashboard > Dashboard Ejecutivo**
2. Hacer clic en el menú **⋮** (más opciones)
3. Seleccionar **Actualizar Dashboard Frontera Living**

## 🔧 Configuración

### Cambiar frecuencia del cron
1. Ir a **Configuración > Trabajos Programados**
2. Buscar "Actualizar KPIs Frontera Dashboard"
3. Editar y cambiar **Cada 30 minutos** al intervalo deseado

### Cambiar objetivos/metas
Edita el archivo `frontera_dashboard/models/dashboard.py` y busca la sección `_refresh_sales_kpis()`, `_refresh_inventory_kpis()`, etc.

Cambia los valores de `target`:
```python
self.create({
    'name': 'Ingresos totales',
    'category': 'sales',
    'target': 1500000,  # <-- CAMBIAR ESTE VALOR
    ...
})
```

## 📊 KPIs Disponibles

### Ventas
- Ingresos totales (vs meta mensual)
- Órdenes confirmadas (pendiente de entrega)
- Cotizaciones pendientes
- Órdenes entregadas

### Inventario
- Recepciones en espera
- Órdenes de entrega (con atrasados)
- Traslados internos

### Inventario de productos
Desde **Frontera Dashboard > Inventario de productos** se pueden consultar los
productos activos, su categoría, stock actual, unidades disponibles, entradas
esperadas y salidas pendientes. Los valores son los campos calculados por Odoo.

### Producción
- Órdenes de producción (en espera y atrasadas)
- Órdenes en progreso
- Órdenes completadas

### Reparaciones
- Reparaciones confirmadas
- Reparaciones en proceso
- Reparaciones completadas

## 🎨 Indicadores Visuales

- **🟢 Verde (Bien)**: Cumplimiento ≥ 70% y sin atrasados
- **🟡 Amarillo (Atención)**: Cumplimiento < 70%
- **🔴 Rojo (Crítico)**: Hay órdenes atrasadas

## 🔐 Permisos

El módulo usa los permisos estándar de Odoo:
- **Usuarios**: Pueden ver el dashboard
- **Gerentes de Ventas**: Acceso completo a datos de ventas
- **Gerentes de Stock**: Acceso a inventario y entregas
- **Planificadores**: Acceso a producción

## 🐛 Troubleshooting

### No aparece el menú del dashboard
- Reinicia Odoo: `Configuración > Actualizar Apps`
- Limpia el cache del navegador (Ctrl+Shift+Del)

### Los datos no se actualizan
- Verifica que el cron esté activo: `Configuración > Trabajos Programados`
- Haz clic en actualizar manual desde el dashboard

### Error: "No se puede acceder a sale.order"
- Asegúrate de que el módulo **Sales** está instalado
- Verifica que tienes permisos de lectura en los modelos

## 📞 Soporte

Para preguntas o ajustes personalizados, contacta con el equipo técnico.

---

**Última actualización**: 2026-08-14  
**Versión**: 16.0.1.0.0
