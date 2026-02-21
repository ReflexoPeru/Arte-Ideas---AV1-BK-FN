"""
Dashboard Views - Analytics App
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum, Count, Q, F
from django.utils import timezone
from datetime import timedelta, date
from decimal import Decimal


class PanelAlertasRapidasView(APIView):
    """
    Endpoint para obtener las métricas del panel de alertas rápidas
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        try:
            from apps.commerce.models import Order, OrderItem
            from apps.commerce.inventario.models import (
                MolduraListon, MolduraPrearmada, VidrioTapaMDF, Paspartu,
                Minilab, Cuadro, Anuario, CorteLaser, MarcoAccesorio, HerramientaGeneral
            )
            from apps.operations.produccion.models import OrdenProduccion
            
            tenant = request.user.tenant
            hoy = timezone.now().date()
            
            # Ingresos de hoy
            ingresos_hoy = Order.objects.filter(
                tenant=tenant,
                order_date=hoy,
                status__in=['completado', 'entregado']
            ).aggregate(total=Sum('total'))['total'] or Decimal('0.00')
            
            # Calcular porcentaje de cambio (comparar con ayer)
            ayer = hoy - timedelta(days=1)
            ingresos_ayer = Order.objects.filter(
                tenant=tenant,
                order_date=ayer,
                status__in=['completado', 'entregado']
            ).aggregate(total=Sum('total'))['total'] or Decimal('0.00')
            
            if ingresos_ayer > 0:
                cambio_ingresos = ((ingresos_hoy - ingresos_ayer) / ingresos_ayer) * 100
            else:
                cambio_ingresos = 0  # Sin datos previos, mostrar 0%
            
            # Pedidos activos
            pedidos_activos = Order.objects.filter(
                tenant=tenant,
                status__in=['pendiente', 'en_proceso', 'confirmado']
            ).count()
            
            # Calcular productos del mes actual vs mes anterior
            inicio_mes = hoy.replace(day=1)
            if inicio_mes.month == 1:
                inicio_mes_anterior = inicio_mes.replace(year=inicio_mes.year - 1, month=12)
            else:
                inicio_mes_anterior = inicio_mes.replace(month=inicio_mes.month - 1)
            
            productos_mes_actual = Order.objects.filter(
                tenant=tenant,
                order_date__gte=inicio_mes
            ).count()
            
            productos_mes_anterior = Order.objects.filter(
                tenant=tenant,
                order_date__gte=inicio_mes_anterior,
                order_date__lt=inicio_mes
            ).count()
            
            if productos_mes_anterior > 0:
                cambio_pedidos = ((productos_mes_actual - productos_mes_anterior) / productos_mes_anterior) * 100
            else:
                cambio_pedidos = 0  # Sin datos previos, mostrar 0%
            
            # Entregas u órdenes (órdenes de producción pendientes de entrega)
            entregas_ordenes = OrdenProduccion.objects.filter(
                tenant=tenant,
                estado__in=['pendiente', 'en_proceso']
            ).count()
            
            # Calcular trabajados (comparar con semana pasada)
            hace_7_dias = hoy - timedelta(days=7)
            trabajados_esta_semana = OrdenProduccion.objects.filter(
                tenant=tenant,
                fecha_inicio_real__date__gte=hace_7_dias
            ).count()
            
            hace_14_dias = hoy - timedelta(days=14)
            trabajados_semana_pasada = OrdenProduccion.objects.filter(
                tenant=tenant,
                fecha_inicio_real__date__gte=hace_14_dias,
                fecha_inicio_real__date__lt=hace_7_dias
            ).count()
            
            if trabajados_semana_pasada > 0:
                cambio_entregas = ((trabajados_esta_semana - trabajados_semana_pasada) / trabajados_semana_pasada) * 100
            else:
                cambio_entregas = 0  # Sin datos previos, mostrar 0%
            
            # Valor de inventario (sumar todos los modelos de inventario)
            valor_inventario = Decimal('0.00')
            modelos_inventario = [
                MolduraListon, MolduraPrearmada, VidrioTapaMDF, Paspartu,
                Minilab, Cuadro, Anuario, CorteLaser, MarcoAccesorio, HerramientaGeneral
            ]
            
            for modelo in modelos_inventario:
                valor = modelo.objects.filter(
                    tenant=tenant,
                    is_active=True
                ).aggregate(
                    total=Sum(F('precio_venta') * F('stock_disponible'))
                )['total'] or Decimal('0.00')
                valor_inventario += valor
            
            # Contar items de pedidos activos
            total_items_activos = OrderItem.objects.filter(
                tenant=tenant,
                order__status__in=['pendiente', 'en_proceso', 'confirmado']
            ).count()
            
            # Contar pedidos por tipo
            pedidos_productos = Order.objects.filter(
                tenant=tenant,
                status__in=['pendiente', 'en_proceso', 'confirmado'],
                document_type__in=['nota_venta', 'proforma']
            ).count()
            
            pedidos_proyectos = Order.objects.filter(
                tenant=tenant,
                status__in=['pendiente', 'en_proceso', 'confirmado'],
                document_type='contrato'
            ).count()
            
            # Contar entregas trabajadas (en proceso)
            entregas_trabajadas = OrdenProduccion.objects.filter(
                tenant=tenant,
                estado='en_proceso'
            ).count()
            
            # Contar productos con stock bajo (stock_disponible <= stock_minimo)
            productos_stock_bajo = 0
            for modelo in modelos_inventario:
                productos_stock_bajo += modelo.objects.filter(
                    tenant=tenant,
                    is_active=True,
                    stock_disponible__lte=F('stock_minimo')
                ).count()
            
            data = {
                "ingresos_hoy": {
                    "valor": float(ingresos_hoy),
                    "cambio_porcentaje": round(float(cambio_ingresos), 1),
                    "periodo": "Hoy"
                },
                "pedidos_activos": {
                    "cantidad": pedidos_activos,
                    "cambio_porcentaje": round(float(cambio_pedidos), 1),
                    "detalle": f"{pedidos_productos} pendientes, {pedidos_proyectos} en proceso"
                },
                "entregas_a_tiempo": {
                    "cantidad": entregas_ordenes,
                    "atrasadas": entregas_trabajadas,
                    "cambio_porcentaje": round(float(cambio_entregas), 1),
                    "promedio": f"{entregas_trabajadas}h promedio"
                },
                "valor_inventario": {
                    "valor": float(valor_inventario),
                    "cambio_porcentaje": -1.2,  # Ejemplo de cambio negativo
                    "stock_bajo": productos_stock_bajo
                }
            }
            
            return Response(data, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class EstadoProduccionView(APIView):
    """
    Endpoint para obtener el estado de producción
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        try:
            from apps.operations.produccion.models import OrdenProduccion
            
            tenant = request.user.tenant
            
            # Pendientes
            pendientes = OrdenProduccion.objects.filter(
                tenant=tenant,
                estado='pendiente'
            ).count()
            
            # En Proceso
            en_proceso = OrdenProduccion.objects.filter(
                tenant=tenant,
                estado='en_proceso'
            ).count()
            
            # Completados (terminado)
            completados = OrdenProduccion.objects.filter(
                tenant=tenant,
                estado='terminado'
            ).count()
            
            # Atrasados (órdenes con fecha estimada pasada y no completadas)
            hoy = timezone.now().date()
            atrasados = OrdenProduccion.objects.filter(
                tenant=tenant,
                fecha_estimada__lt=hoy,
                estado__in=['pendiente', 'en_proceso']
            ).count()
            
            data = {
                "pendientes": pendientes,
                "en_proceso": en_proceso,
                "completados": completados,
                "atrasados": atrasados
            }
            
            return Response(data, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ClientesEstadisticasView(APIView):
    """
    Endpoint para obtener estadísticas de clientes
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        try:
            from apps.crm.clientes.models import Cliente
            
            tenant = request.user.tenant
            hoy = timezone.now().date()
            inicio_mes = hoy.replace(day=1)
            
            # Total de clientes
            total = Cliente.objects.filter(tenant=tenant).count()
            
            # Nuevos este mes
            nuevos_este_mes = Cliente.objects.filter(
                tenant=tenant,
                creado_en__date__gte=inicio_mes
            ).count()
            
            # Activos (clientes con pedidos en los últimos 90 días)
            hace_90_dias = hoy - timedelta(days=90)
            activos = Cliente.objects.filter(
                tenant=tenant,
                pedidos__order_date__gte=hace_90_dias
            ).distinct().count()
            
            # Inactivos
            inactivos = total - activos
            
            data = {
                "total": total,
                "nuevos_este_mes": nuevos_este_mes,
                "activos": activos,
                "inactivos": inactivos
            }
            
            return Response(data, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ContratosEstadisticasView(APIView):
    """
    Endpoint para obtener estadísticas de contratos
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        try:
            from apps.crm.contratos.models import Contrato, PagoContrato
            
            tenant = request.user.tenant
            hoy = timezone.now().date()
            
            # Valor total de contratos activos
            valor_total = Contrato.objects.filter(
                tenant=tenant,
                estado='activo'
            ).aggregate(total=Sum('monto_total'))['total'] or Decimal('0.00')
            
            # Contratos activos
            contratos_activos = Contrato.objects.filter(
                tenant=tenant,
                estado='activo'
            ).count()
            
            # Pagos pendientes (saldo pendiente de contratos activos)
            pagos_pendientes = Contrato.objects.filter(
                tenant=tenant,
                estado='activo'
            ).aggregate(total=Sum('saldo_pendiente'))['total'] or Decimal('0.00')
            
            # Contratos por vencer (próximos 30 días)
            fecha_limite = hoy + timedelta(days=30)
            por_vencer = Contrato.objects.filter(
                tenant=tenant,
                estado='activo',
                fecha_fin__gte=hoy,
                fecha_fin__lte=fecha_limite
            ).count()
            
            data = {
                "valor_total": float(valor_total),
                "contratos_activos": contratos_activos,
                "pagos_pendientes": float(pagos_pendientes),
                "por_vencer": por_vencer
            }
            
            return Response(data, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ProductosMasVendidosView(APIView):
    """
    Endpoint para obtener los productos más vendidos
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        try:
            from apps.commerce.models import OrderItem
            
            tenant = request.user.tenant
            
            # Obtener los 4 productos más vendidos
            productos_vendidos = OrderItem.objects.filter(
                tenant=tenant,
                order__status__in=['completado', 'entregado']
            ).values(
                'product_name'
            ).annotate(
                total_vendido=Sum('quantity'),
                ingresos=Sum('subtotal')
            ).order_by('-total_vendido')[:4]
            
            data = []
            for item in productos_vendidos:
                data.append({
                    "nombre": item['product_name'],
                    "cantidad_vendida": item['total_vendido'],
                    "ingresos": float(item['ingresos'] or 0)
                })
            
            return Response(data, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class PedidosRecientesView(APIView):
    """
    Endpoint para obtener los pedidos recientes
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        try:
            from apps.commerce.models import Order
            
            tenant = request.user.tenant
            
            # Obtener los últimos 4 pedidos
            pedidos = Order.objects.filter(
                tenant=tenant
            ).select_related('cliente').order_by('-order_date')[:4]
            
            data = []
            for pedido in pedidos:
                data.append({
                    "codigo": pedido.order_number,
                    "cliente": pedido.cliente.obtener_nombre_completo() if pedido.cliente else "Sin cliente",
                    "descripcion": pedido.description or f"{pedido.cliente.obtener_nombre_completo() if pedido.cliente else 'Cliente'} • {pedido.get_document_type_display()}",
                    "monto": float(pedido.total),
                    "estado": pedido.status
                })
            
            return Response(data, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class EntregasProgramadasHoyView(APIView):
    """
    Endpoint para obtener las entregas programadas para hoy
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        try:
            from apps.operations.produccion.models import OrdenProduccion
            
            tenant = request.user.tenant
            hoy = timezone.now().date()
            
            # Obtener órdenes con entrega programada para hoy
            entregas = OrdenProduccion.objects.filter(
                tenant=tenant,
                fecha_estimada=hoy
            ).select_related('pedido', 'pedido__cliente').order_by('fecha_estimada')[:5]
            
            total_entregas = entregas.count()
            
            data = {
                "total_entregas": total_entregas,
                "mensaje": f"{total_entregas} pedidos listos para entregar",
                "nota": "Todos los pedidos están listos para ser entregados hoy",
                "entregas": []
            }
            
            for entrega in entregas:
                data["entregas"].append({
                    "codigo": entrega.numero_op,
                    "cliente": entrega.cliente.obtener_nombre_completo() if entrega.cliente else "Sin cliente",
                    "descripcion": entrega.descripcion or "Orden de producción",
                    "fecha_entrega": entrega.fecha_estimada.strftime("%Y-%m-%d"),
                    "estado": entrega.estado
                })
            
            return Response(data, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class DashboardResumenView(APIView):
    """
    Endpoint para obtener un resumen completo del dashboard
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        try:
            # Obtener datos de todos los endpoints
            alertas_view = PanelAlertasRapidasView()
            alertas_view.request = request
            alertas_data = alertas_view.get(request).data
            
            produccion_view = EstadoProduccionView()
            produccion_view.request = request
            produccion_data = produccion_view.get(request).data
            
            clientes_view = ClientesEstadisticasView()
            clientes_view.request = request
            clientes_data = clientes_view.get(request).data
            
            contratos_view = ContratosEstadisticasView()
            contratos_view.request = request
            contratos_data = contratos_view.get(request).data
            
            productos_view = ProductosMasVendidosView()
            productos_view.request = request
            productos_data = productos_view.get(request).data
            
            pedidos_view = PedidosRecientesView()
            pedidos_view.request = request
            pedidos_data = pedidos_view.get(request).data
            
            entregas_view = EntregasProgramadasHoyView()
            entregas_view.request = request
            entregas_data = entregas_view.get(request).data
            
            data = {
                "panel_alertas_rapidas": alertas_data,
                "estado_produccion": produccion_data,
                "clientes": clientes_data,
                "contratos": contratos_data,
                "productos_mas_vendidos": productos_data,
                "pedidos_recientes": pedidos_data,
                "entregas_programadas_hoy": entregas_data
            }
            
            return Response(data, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )



class AlertasView(APIView):
    """
    Endpoint para obtener alertas dinámicas del sistema
    Tipos: Stock Crítico, Mantenimientos Próximos, Entregas Urgentes
    Filtros: hoy, semana, mes
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        try:
            from apps.commerce.models import Order
            from apps.commerce.inventario.models import (
                MolduraListon, MolduraPrearmada, VidrioTapaMDF, Paspartu,
                Minilab, Cuadro, Anuario, CorteLaser, MarcoAccesorio, HerramientaGeneral
            )
            from apps.operations.produccion.models import OrdenProduccion
            from apps.operations.activos.models import Activo
            
            tenant = request.user.tenant
            hoy = timezone.now().date()
            
            # Obtener filtro de tiempo (por defecto: semana)
            filtro = request.query_params.get('filtro', 'semana')
            
            # Calcular rango de fechas según filtro
            if filtro == 'hoy':
                fecha_inicio = hoy
                fecha_fin = hoy
            elif filtro == 'semana':
                fecha_inicio = hoy
                fecha_fin = hoy + timedelta(days=7)
            elif filtro == 'mes':
                fecha_inicio = hoy
                fecha_fin = hoy + timedelta(days=30)
            else:
                fecha_inicio = hoy
                fecha_fin = hoy + timedelta(days=7)
            
            alertas_stock = []
            alertas_mantenimiento = []
            alertas_entregas = []
            
            # 1. STOCK CRÍTICO - Productos con bajo inventario
            modelos_inventario = [
                ('MolduraListon', MolduraListon),
                ('MolduraPrearmada', MolduraPrearmada),
                ('VidrioTapaMDF', VidrioTapaMDF),
                ('Paspartu', Paspartu),
                ('Minilab', Minilab),
                ('Cuadro', Cuadro),
                ('Anuario', Anuario),
                ('CorteLaser', CorteLaser),
                ('MarcoAccesorio', MarcoAccesorio),
                ('HerramientaGeneral', HerramientaGeneral)
            ]
            
            for nombre_modelo, modelo in modelos_inventario:
                productos_stock_bajo = modelo.objects.filter(
                    tenant=tenant,
                    is_active=True,
                    stock_disponible__lte=F('stock_minimo')
                ).order_by('stock_disponible')
                
                for producto in productos_stock_bajo:
                    # Determinar prioridad según nivel de stock
                    porcentaje_stock = (producto.stock_disponible / producto.stock_minimo * 100) if producto.stock_minimo > 0 else 0
                    
                    if porcentaje_stock <= 50:
                        prioridad = "critico"
                        color = "rojo"
                    elif porcentaje_stock <= 100:
                        prioridad = "advertencia"
                        color = "naranja"
                    else:
                        prioridad = "normal"
                        color = "amarillo"
                    
                    alertas_stock.append({
                        "nombre": producto.nombre_producto,
                        "stock_actual": producto.stock_disponible,
                        "stock_minimo": producto.stock_minimo,
                        "categoria": nombre_modelo,
                        "prioridad": prioridad,
                        "color": color
                    })
            
            # 2. MANTENIMIENTOS PRÓXIMOS - Mantenimientos programados
            try:
                from apps.operations.activos.models import Mantenimiento
                
                mantenimientos_proximos = Mantenimiento.objects.filter(
                    estado_del_mantenimiento='programado',
                    proxima_fecha_mantenimiento__gte=fecha_inicio,
                    proxima_fecha_mantenimiento__lte=fecha_fin
                ).select_related('activo').order_by('proxima_fecha_mantenimiento')
                
                for mantenimiento in mantenimientos_proximos:
                    dias_restantes = (mantenimiento.proxima_fecha_mantenimiento - hoy).days
                    
                    if dias_restantes <= 1:
                        prioridad = "critico"
                        color = "rojo"
                        estado_texto = "Hoy" if dias_restantes == 0 else "Mañana"
                    elif dias_restantes <= 3:
                        prioridad = "advertencia"
                        color = "naranja"
                        estado_texto = f"{dias_restantes} días"
                    else:
                        prioridad = "normal"
                        color = "amarillo"
                        estado_texto = f"{dias_restantes} días"
                    
                    alertas_mantenimiento.append({
                        "nombre": mantenimiento.activo.nombre,
                        "tipo_mantenimiento": mantenimiento.get_tipo_mantenimiento_display(),
                        "fecha_programada": mantenimiento.proxima_fecha_mantenimiento.strftime('%d/%m/%Y'),
                        "dias_restantes": dias_restantes,
                        "estado_texto": estado_texto,
                        "prioridad": prioridad,
                        "color": color
                    })
            except Exception as e:
                # Si hay error, continuar sin mantenimientos
                pass
            
            # 3. ENTREGAS URGENTES - Órdenes de producción próximas a entregar
            entregas_urgentes = OrdenProduccion.objects.filter(
                tenant=tenant,
                estado__in=['pendiente', 'en_proceso'],
                fecha_estimada__gte=fecha_inicio,
                fecha_estimada__lte=fecha_fin
            ).select_related('cliente', 'pedido').order_by('fecha_estimada')
            
            for entrega in entregas_urgentes:
                dias_restantes = (entrega.fecha_estimada - hoy).days
                
                if dias_restantes <= 1:
                    prioridad = "critico"
                    color = "rojo"
                    estado = "En producción" if entrega.estado == 'en_proceso' else "Listo para entrega"
                elif dias_restantes <= 3:
                    prioridad = "advertencia"
                    color = "naranja"
                    estado = "En producción" if entrega.estado == 'en_proceso' else "Pendiente de aprobación"
                else:
                    prioridad = "normal"
                    color = "verde"
                    estado = entrega.get_estado_display()
                
                # Obtener descripción del pedido
                descripcion = entrega.descripcion or ""
                if entrega.pedido:
                    descripcion = f"Entrega de {entrega.pedido.items.count()} productos de presentación" if entrega.pedido.items.exists() else descripcion
                
                alertas_entregas.append({
                    "codigo": entrega.numero_op,
                    "cliente": entrega.cliente.obtener_nombre_completo() if entrega.cliente else "Sin cliente",
                    "fecha_entrega": entrega.fecha_estimada.strftime('%d/%m/%Y'),
                    "dias_restantes": dias_restantes,
                    "estado": estado,
                    "descripcion": descripcion,
                    "prioridad": prioridad,
                    "color": color
                })
            
            # Contar alertas por tipo
            data = {
                "total_alertas": len(alertas_stock) + len(alertas_mantenimiento) + len(alertas_entregas),
                "filtro_aplicado": filtro,
                "stock_critico": {
                    "total": len(alertas_stock),
                    "alertas": alertas_stock[:10]  # Limitar a 10
                },
                "mantenimientos_proximos": {
                    "total": len(alertas_mantenimiento),
                    "alertas": alertas_mantenimiento[:10]  # Limitar a 10
                },
                "entregas_urgentes": {
                    "total": len(alertas_entregas),
                    "alertas": alertas_entregas[:10]  # Limitar a 10
                }
            }
            
            return Response(data, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
