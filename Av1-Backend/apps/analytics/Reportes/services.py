"""
Servicios para Generación de Reportes - Arte Ideas Analytics
Servicios que obtienen y procesan datos de diferentes módulos para reportes
"""
from django.db.models import Sum, Count, Avg, Q, F, DecimalField
from django.db.models.functions import TruncDate, TruncMonth, TruncYear
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal

from apps.commerce.pedidos.models import Order, OrderItem, OrderPayment
from apps.commerce.inventario.models import (
    MolduraListon, MolduraPrearmada, VidrioTapaMDF, Paspartu,
    Minilab, Cuadro, Anuario, CorteLaser, MarcoAccesorio, HerramientaGeneral
)
from apps.crm.clientes.models import Cliente, HistorialCliente
from apps.crm.contratos.models import Contrato, PagoContrato
from apps.operations.produccion.models import OrdenProduccion


class ReportService:
    """Servicio base para generar reportes"""
    
    def __init__(self, tenant, fecha_inicio=None, fecha_fin=None):
        self.tenant = tenant
        self.fecha_inicio = fecha_inicio or (timezone.now() - timedelta(days=30)).date()
        self.fecha_fin = fecha_fin or timezone.now().date()
    
    def get_date_filter(self, field_name='created_at'):
        """Obtener filtro de fechas para queries"""
        # Si el campo es DateField, usar directamente
        # Si es DateTimeField, convertir a fecha
        return Q(**{
            f'{field_name}__date__gte': self.fecha_inicio,
            f'{field_name}__date__lte': self.fecha_fin
        })


class VentasReportService(ReportService):
    """Servicio para reportes de Ventas"""
    
    def get_metrics(self):
        """Obtener métricas de resumen de ventas"""
        orders = Order.objects.filter(
            tenant=self.tenant,
            order_date__gte=self.fecha_inicio,
            order_date__lte=self.fecha_fin
        )
        
        total_ventas = orders.aggregate(
            total=Sum('total', default=0)
        )['total'] or Decimal('0')
        
        total_pedidos = orders.count()
        
        promedio_venta = total_ventas / total_pedidos if total_pedidos > 0 else Decimal('0')
        
        pedidos_completados = orders.filter(status='completado').count()
        tasa_completitud = (pedidos_completados / total_pedidos * 100) if total_pedidos > 0 else 0
        
        total_pagado = orders.aggregate(
            total=Sum('paid_amount', default=0)
        )['total'] or Decimal('0')
        
        saldo_pendiente = total_ventas - total_pagado
        
        return {
            'total_ventas': float(total_ventas),
            'total_pedidos': total_pedidos,
            'promedio_venta': float(promedio_venta),
            'tasa_completitud': round(tasa_completitud, 2),
            'total_pagado': float(total_pagado),
            'saldo_pendiente': float(saldo_pendiente),
        }
    
    def get_detalle(self):
        """Obtener tabla detallada de ventas"""
        orders = Order.objects.filter(
            tenant=self.tenant,
            order_date__gte=self.fecha_inicio,
            order_date__lte=self.fecha_fin
        ).select_related('cliente').order_by('-order_date')
        
        detalle = []
        for order in orders:
            detalle.append({
                'id': order.id,
                'numero_pedido': order.order_number,
                'cliente': order.cliente.obtener_nombre_completo(),
                'fecha': order.order_date.isoformat(),
                'tipo_documento': order.get_document_type_display(),
                'total': float(order.total),
                'pagado': float(order.paid_amount),
                'saldo': float(order.balance),
                'estado': order.get_status_display(),
                'estado_pago': order.get_payment_status_display(),
            })
        
        return detalle


class InventarioReportService(ReportService):
    """Servicio para reportes de Inventario"""
    
    def get_metrics(self):
        """Obtener métricas de resumen de inventario"""
        # Obtener todos los modelos de inventario
        all_models = [
            MolduraListon, MolduraPrearmada, VidrioTapaMDF, Paspartu,
            Minilab, Cuadro, Anuario, CorteLaser, MarcoAccesorio, HerramientaGeneral
        ]
        
        total_productos = 0
        total_stock = 0
        total_valor_inventario = Decimal('0')
        productos_bajo_stock = 0
        
        for model in all_models:
            productos = model.objects.filter(tenant=self.tenant, is_active=True)
            total_productos += productos.count()
            
            for producto in productos:
                total_stock += producto.stock_disponible
                total_valor_inventario += producto.costo_total
                if producto.alerta_stock:
                    productos_bajo_stock += 1
        
        return {
            'total_productos': total_productos,
            'total_stock': total_stock,
            'total_valor_inventario': float(total_valor_inventario),
            'productos_bajo_stock': productos_bajo_stock,
            'productos_ok_stock': total_productos - productos_bajo_stock,
        }
    
    def get_detalle(self):
        """Obtener tabla detallada de inventario"""
        detalle = []
        
        # Lista de modelos con sus nombres
        models_data = [
            (MolduraListon, 'Moldura Listón'),
            (MolduraPrearmada, 'Moldura Prearmada'),
            (VidrioTapaMDF, 'Vidrio/Tapa MDF'),
            (Paspartu, 'Paspartú'),
            (Minilab, 'Minilab'),
            (Cuadro, 'Cuadro'),
            (Anuario, 'Anuario'),
            (CorteLaser, 'Corte Láser'),
            (MarcoAccesorio, 'Marco/Accesorio'),
            (HerramientaGeneral, 'Herramienta General'),
        ]
        
        for model, categoria in models_data:
            productos = model.objects.filter(tenant=self.tenant, is_active=True)
            for producto in productos:
                detalle.append({
                    'id': producto.id,
                    'categoria': categoria,
                    'nombre': producto.nombre_producto,
                    'codigo': producto.codigo_producto or '',
                    'stock_disponible': producto.stock_disponible,
                    'stock_minimo': producto.stock_minimo,
                    'costo_unitario': float(producto.costo_unitario),
                    'precio_venta': float(producto.precio_venta),
                    'valor_total': float(producto.costo_total),
                    'alerta_stock': producto.alerta_stock,
                    'proveedor': producto.proveedor or '',
                })
        
        # Ordenar por alerta de stock primero, luego por nombre
        detalle.sort(key=lambda x: (not x['alerta_stock'], x['nombre']))
        
        return detalle


class ProduccionReportService(ReportService):
    """Servicio para reportes de Producción"""
    
    def get_metrics(self):
        """Obtener métricas de resumen de producción"""
        ordenes = OrdenProduccion.objects.filter(
            tenant=self.tenant,
            fecha_estimada__gte=self.fecha_inicio,
            fecha_estimada__lte=self.fecha_fin
        )
        
        total_ordenes = ordenes.count()
        ordenes_completadas = ordenes.filter(estado='terminado').count()
        ordenes_en_proceso = ordenes.filter(estado='en_proceso').count()
        ordenes_pendientes = ordenes.filter(estado='pendiente').count()
        ordenes_vencidas = sum(1 for o in ordenes if o.is_vencida)
        
        # Calcular tiempo promedio
        ordenes_con_tiempo = ordenes.filter(tiempo_real_horas__isnull=False)
        tiempo_promedio = ordenes_con_tiempo.aggregate(
            avg=Avg('tiempo_real_horas')
        )['avg'] or 0
        
        tasa_completitud = (ordenes_completadas / total_ordenes * 100) if total_ordenes > 0 else 0
        
        return {
            'total_ordenes': total_ordenes,
            'ordenes_completadas': ordenes_completadas,
            'ordenes_en_proceso': ordenes_en_proceso,
            'ordenes_pendientes': ordenes_pendientes,
            'ordenes_vencidas': ordenes_vencidas,
            'tiempo_promedio_horas': round(float(tiempo_promedio), 2),
            'tasa_completitud': round(tasa_completitud, 2),
        }
    
    def get_detalle(self):
        """Obtener tabla detallada de producción"""
        ordenes = OrdenProduccion.objects.filter(
            tenant=self.tenant,
            fecha_estimada__gte=self.fecha_inicio,
            fecha_estimada__lte=self.fecha_fin
        ).select_related('pedido', 'cliente', 'operario').order_by('-fecha_estimada')
        
        detalle = []
        for orden in ordenes:
            detalle.append({
                'id': orden.id,
                'numero_op': orden.numero_op,
                'pedido': orden.pedido.order_number if orden.pedido else '',
                'cliente': orden.cliente.obtener_nombre_completo(),
                'tipo': orden.get_tipo_display(),
                'estado': orden.get_estado_display(),
                'prioridad': orden.get_prioridad_display(),
                'fecha_estimada': orden.fecha_estimada.isoformat(),
                'fecha_finalizacion': orden.fecha_finalizacion_real.date().isoformat() if orden.fecha_finalizacion_real else None,
                'operario': orden.operario.get_full_name() if (orden.operario and orden.operario.first_name) else (orden.operario.username if orden.operario else ''),
                'tiempo_estimado': float(orden.tiempo_estimado_horas) if orden.tiempo_estimado_horas else None,
                'tiempo_real': float(orden.tiempo_real_horas) if orden.tiempo_real_horas else None,
                'vencida': orden.is_vencida,
            })
        
        return detalle


class ClientesReportService(ReportService):
    """Servicio para reportes de Clientes"""
    
    def get_metrics(self):
        """Obtener métricas de resumen de clientes"""
        clientes = Cliente.objects.filter(tenant=self.tenant, activo=True)
        
        total_clientes = clientes.count()
        
        clientes_por_tipo = clientes.values('tipo_cliente').annotate(
            count=Count('id')
        )
        
        clientes_particulares = next((c['count'] for c in clientes_por_tipo if c['tipo_cliente'] == 'particular'), 0)
        clientes_colegios = next((c['count'] for c in clientes_por_tipo if c['tipo_cliente'] == 'colegio'), 0)
        clientes_empresas = next((c['count'] for c in clientes_por_tipo if c['tipo_cliente'] == 'empresa'), 0)
        
        # Clientes nuevos en el período
        clientes_nuevos = Cliente.objects.filter(
            tenant=self.tenant,
            creado_en__date__gte=self.fecha_inicio,
            creado_en__date__lte=self.fecha_fin
        ).count()
        
        return {
            'total_clientes': total_clientes,
            'clientes_particulares': clientes_particulares,
            'clientes_colegios': clientes_colegios,
            'clientes_empresas': clientes_empresas,
            'clientes_nuevos': clientes_nuevos,
        }
    
    def get_detalle(self):
        """Obtener tabla detallada de clientes"""
        clientes = Cliente.objects.filter(
            tenant=self.tenant,
            activo=True
        ).order_by('apellidos', 'nombres')
        
        # Contar pedidos por cliente
        detalle = []
        for cliente in clientes:
            total_pedidos = cliente.pedidos.count()
            total_ventas = cliente.pedidos.aggregate(
                total=Sum('total', default=0)
            )['total'] or Decimal('0')
            
            detalle.append({
                'id': cliente.id,
                'tipo_cliente': cliente.get_tipo_cliente_display(),
                'nombres': cliente.nombres,
                'apellidos': cliente.apellidos,
                'nombre_completo': cliente.obtener_nombre_completo(),
                'email': cliente.email,
                'telefono': cliente.telefono,
                'dni': cliente.dni,
                'total_pedidos': total_pedidos,
                'total_ventas': float(total_ventas),
                'fecha_registro': cliente.creado_en.date().isoformat(),
            })
        
        return detalle


class FinancieroReportService(ReportService):
    """Servicio para reportes Financieros"""
    
    def get_metrics(self):
        """Obtener métricas de resumen financiero"""
        # Ingresos de pedidos
        orders = Order.objects.filter(
            tenant=self.tenant,
            order_date__gte=self.fecha_inicio,
            order_date__lte=self.fecha_fin
        )
        
        total_ingresos = orders.aggregate(
            total=Sum('total', default=0)
        )['total'] or Decimal('0')
        
        total_pagado = orders.aggregate(
            total=Sum('paid_amount', default=0)
        )['total'] or Decimal('0')
        
        # Pagos recibidos
        pagos = OrderPayment.objects.filter(
            order__tenant=self.tenant,
            payment_date__gte=self.fecha_inicio,
            payment_date__lte=self.fecha_fin
        )
        
        total_pagos_recibidos = pagos.aggregate(
            total=Sum('amount', default=0)
        )['total'] or Decimal('0')
        
        # Pagos por método
        pagos_por_metodo = pagos.values('payment_method').annotate(
            total=Sum('amount', default=0)
        )
        
        # Saldo pendiente total
        saldo_pendiente = total_ingresos - total_pagado
        
        # IGV recaudado (18% de los ingresos)
        igv_recaudado = total_ingresos * Decimal('0.18') / Decimal('1.18')
        
        return {
            'total_ingresos': float(total_ingresos),
            'total_pagado': float(total_pagado),
            'total_pagos_recibidos': float(total_pagos_recibidos),
            'saldo_pendiente': float(saldo_pendiente),
            'igv_recaudado': float(igv_recaudado),
            'ingresos_netos': float(total_ingresos - igv_recaudado),
        }
    
    def get_detalle(self):
        """Obtener tabla detallada financiera"""
        pagos = OrderPayment.objects.filter(
            order__tenant=self.tenant,
            payment_date__gte=self.fecha_inicio,
            payment_date__lte=self.fecha_fin
        ).select_related('order', 'order__cliente').order_by('-payment_date')
        
        detalle = []
        for pago in pagos:
            detalle.append({
                'id': pago.id,
                'fecha': pago.payment_date.isoformat(),
                'numero_pedido': pago.order.order_number,
                'cliente': pago.order.cliente.obtener_nombre_completo(),
                'monto': float(pago.amount),
                'metodo_pago': pago.get_payment_method_display(),
                'numero_referencia': pago.reference_number or '',
                'notas': pago.notes or '',
            })
        
        return detalle


class ContratosReportService(ReportService):
    """Servicio para reportes de Contratos"""
    
    def get_metrics(self):
        """Obtener métricas de resumen de contratos"""
        contratos = Contrato.objects.filter(
            tenant=self.tenant,
            fecha_inicio__gte=self.fecha_inicio,
            fecha_inicio__lte=self.fecha_fin
        )
        
        total_contratos = contratos.count()
        
        total_monto = contratos.aggregate(
            total=Sum('monto_total', default=0)
        )['total'] or Decimal('0')
        
        total_adelantos = contratos.aggregate(
            total=Sum('adelanto', default=0)
        )['total'] or Decimal('0')
        
        total_saldo_pendiente = contratos.aggregate(
            total=Sum('saldo_pendiente', default=0)
        )['total'] or Decimal('0')
        
        contratos_activos = contratos.filter(estado='activo').count()
        contratos_completados = contratos.filter(estado='completado').count()
        
        return {
            'total_contratos': total_contratos,
            'total_monto': float(total_monto),
            'total_adelantos': float(total_adelantos),
            'total_saldo_pendiente': float(total_saldo_pendiente),
            'contratos_activos': contratos_activos,
            'contratos_completados': contratos_completados,
        }
    
    def get_detalle(self):
        """Obtener tabla detallada de contratos"""
        contratos = Contrato.objects.filter(
            tenant=self.tenant,
            fecha_inicio__gte=self.fecha_inicio,
            fecha_inicio__lte=self.fecha_fin
        ).select_related('cliente').order_by('-fecha_inicio')
        
        detalle = []
        for contrato in contratos:
            detalle.append({
                'id': contrato.id,
                'numero_contrato': contrato.numero_contrato,
                'titulo': contrato.titulo,
                'cliente': contrato.cliente.obtener_nombre_completo(),
                'tipo_servicio': contrato.get_tipo_servicio_display(),
                'fecha_inicio': contrato.fecha_inicio.isoformat(),
                'fecha_fin': contrato.fecha_fin.isoformat(),
                'monto_total': float(contrato.monto_total),
                'adelanto': float(contrato.adelanto),
                'saldo_pendiente': float(contrato.saldo_pendiente),
                'estado': contrato.get_estado_display(),
                'porcentaje_adelanto': round(contrato.porcentaje_adelanto, 2),
            })
        
        return detalle

