from odoo import api, fields, models
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta


class DashboardKpi(models.Model):
    _name = 'dashboard.kpi'
    _description = 'Dashboard KPI Executive'
    _rec_name = 'name'

    name = fields.Char(string='Nombre', required=True)
    category = fields.Selection([
        ('sales', 'Ventas'),
        ('inventory', 'Inventario'),
        ('production', 'Producción'),
        ('repair', 'Reparaciones'),
    ], string='Categoría', required=True)
    period = fields.Char(string='Período')
    value = fields.Float(string='Valor')
    target = fields.Float(string='Objetivo')
    completion_percentage = fields.Float(string='Cumplimiento %', compute='_compute_completion')
    delayed_count = fields.Integer(string='Atrasados')
    pending_count = fields.Integer(string='Pendientes')
    completed_count = fields.Integer(string='Completados')
    status = fields.Selection([
        ('danger', '🔴 Crítico'),
        ('warning', '🟡 Atención'),
        ('success', '🟢 Bien'),
    ], string='Estado', compute='_compute_status')
    last_update = fields.Datetime(string='Última actualización', auto_now=True)

    @api.depends('value', 'target')
    def _compute_completion(self):
        for record in self:
            if record.target and record.target != 0:
                record.completion_percentage = round((record.value / record.target) * 100, 1)
            else:
                record.completion_percentage = 0

    @api.depends('completion_percentage', 'delayed_count')
    def _compute_status(self):
        for record in self:
            if record.delayed_count > 0:
                record.status = 'danger'
            elif record.completion_percentage < 70:
                record.status = 'warning'
            else:
                record.status = 'success'

    @api.model
    def refresh_dashboard(self):
        """Actualiza todos los KPIs del dashboard con datos reales"""
        self.search([]).unlink()
        
        today = datetime.now().date()
        month_start = today.replace(day=1)
        month_end = (today.replace(day=1) + relativedelta(months=1)) - timedelta(days=1)
        
        # ====== VENTAS ======
        self._refresh_sales_kpis(month_start, today)
        
        # ====== INVENTARIO ======
        self._refresh_inventory_kpis()
        
        # ====== PRODUCCIÓN ======
        self._refresh_production_kpis()
        
        # ====== REPARACIONES ======
        self._refresh_repair_kpis()
        
        return True

    def _refresh_sales_kpis(self, month_start, today):
        """KPIs de ventas desde sale.order"""
        SaleOrder = self.env['sale.order']
        
        # Total vendido este mes
        month_orders = SaleOrder.search([
            ('date_order', '>=', month_start),
            ('date_order', '<=', today),
            ('state', 'not in', ['cancel', 'draft'])
        ])
        total_sales = sum(order.amount_total for order in month_orders)
        
        # Órdenes por estado
        quotations = SaleOrder.search_count([('state', '=', 'draft')])
        confirmed = SaleOrder.search_count([('state', 'in', ['sent', 'sale'])])
        invoiced = SaleOrder.search_count([('state', '=', 'done')])
        
        # KPI: Total vendido
        self.create({
            'name': 'Ingresos totales',
            'category': 'sales',
            'period': 'Este mes',
            'value': total_sales,
            'target': 1500000,
            'completed_count': len(month_orders),
        })
        
        # KPI: Órdenes confirmadas
        self.create({
            'name': 'Órdenes confirmadas',
            'category': 'sales',
            'period': 'Pendiente de entrega',
            'value': confirmed,
            'target': 50,
            'completed_count': confirmed,
        })
        
        # KPI: Cotizaciones pendientes
        self.create({
            'name': 'Cotizaciones pendientes',
            'category': 'sales',
            'period': 'Esperando aprobación',
            'value': quotations,
            'target': 20,
            'pending_count': quotations,
        })
        
        # KPI: Órdenes entregadas
        self.create({
            'name': 'Órdenes entregadas',
            'category': 'sales',
            'period': 'Este mes',
            'value': invoiced,
            'target': 40,
            'completed_count': invoiced,
        })

    def _refresh_inventory_kpis(self):
        """KPIs de inventario desde stock.picking"""
        Picking = self.env['stock.picking']
        
        # Recepciones
        receipts = Picking.search_count([('picking_type_code', '=', 'incoming')])
        receipts_delayed = Picking.search_count([
            ('picking_type_code', '=', 'incoming'),
            ('scheduled_date', '<', datetime.now()),
            ('state', 'not in', ['done', 'cancel'])
        ])
        
        # Entregas
        deliveries = Picking.search_count([('picking_type_code', '=', 'outgoing')])
        deliveries_delayed = Picking.search_count([
            ('picking_type_code', '=', 'outgoing'),
            ('scheduled_date', '<', datetime.now()),
            ('state', 'not in', ['done', 'cancel'])
        ])
        
        # Traslados internos
        transfers = Picking.search_count([('picking_type_code', '=', 'internal')])
        
        # KPI: En espera de recepción
        self.create({
            'name': 'Recepciones en espera',
            'category': 'inventory',
            'period': 'Por recibir',
            'value': receipts,
            'target': 30,
            'pending_count': receipts,
            'delayed_count': receipts_delayed,
        })
        
        # KPI: Entregas pendientes
        self.create({
            'name': 'Órdenes de entrega',
            'category': 'inventory',
            'period': 'Pendientes',
            'value': deliveries,
            'target': 50,
            'pending_count': deliveries,
            'delayed_count': deliveries_delayed,
        })
        
        # KPI: Traslados internos
        self.create({
            'name': 'Traslados internos',
            'category': 'inventory',
            'period': 'En proceso',
            'value': transfers,
            'target': 20,
            'pending_count': transfers,
        })

    def _refresh_production_kpis(self):
        """KPIs de producción desde mrp.production"""
        Production = self.env['mrp.production']
        
        # Órdenes por estado
        waiting = Production.search_count([('state', '=', 'confirmed')])
        in_progress = Production.search_count([('state', '=', 'progress')])
        done = Production.search_count([('state', '=', 'done')])
        delayed = Production.search_count([
            ('date_deadline', '<', datetime.now()),
            ('state', 'in', ['confirmed', 'progress'])
        ])
        
        # KPI: En espera de producción
        self.create({
            'name': 'Órdenes de producción',
            'category': 'production',
            'period': 'En espera',
            'value': waiting,
            'target': 30,
            'pending_count': waiting,
            'delayed_count': delayed,
        })
        
        # KPI: En producción
        self.create({
            'name': 'Órdenes en progreso',
            'category': 'production',
            'period': 'Fabricando',
            'value': in_progress,
            'target': 25,
            'pending_count': in_progress,
        })
        
        # KPI: Completadas
        self.create({
            'name': 'Órdenes completadas',
            'category': 'production',
            'period': 'Este mes',
            'value': done,
            'target': 40,
            'completed_count': done,
        })

    def _refresh_repair_kpis(self):
        """KPIs de reparaciones desde repair.order"""
        Repair = self.env['repair.order']
        
        # Órdenes de reparación
        confirmed = Repair.search_count([('state', '=', 'confirmed')])
        in_repair = Repair.search_count([('state', '=', 'under_repair')])
        done = Repair.search_count([('state', '=', 'done')])
        delayed = Repair.search_count([
            ('warranty_return_date', '<', datetime.now()),
            ('state', 'in', ['confirmed', 'under_repair'])
        ])
        
        # KPI: Confirmadas
        self.create({
            'name': 'Reparaciones confirmadas',
            'category': 'repair',
            'period': 'Esperando',
            'value': confirmed,
            'target': 15,
            'pending_count': confirmed,
            'delayed_count': delayed,
        })
        
        # KPI: En reparación
        self.create({
            'name': 'Reparaciones en proceso',
            'category': 'repair',
            'period': 'En taller',
            'value': in_repair,
            'target': 20,
            'pending_count': in_repair,
        })
        
        # KPI: Completadas
        self.create({
            'name': 'Reparaciones completadas',
            'category': 'repair',
            'period': 'Este mes',
            'value': done,
            'target': 25,
            'completed_count': done,
        })
