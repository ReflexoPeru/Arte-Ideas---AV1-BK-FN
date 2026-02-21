from django.contrib import admin
from .models import OrdenProduccion
from apps.core.models import User, Tenant
from apps.crm.clientes.models import Cliente
from apps.commerce.pedidos.models import Order

@admin.register(OrdenProduccion)
class OrdenProduccionAdmin(admin.ModelAdmin):
    list_display = ('numero_op', 'pedido', 'cliente', 'tipo', 'estado', 'prioridad', 
                   'operario', 'fecha_estimada', 'tenant')
    list_filter = ('estado', 'tipo', 'prioridad', 'tenant')
    search_fields = ('numero_op', 'pedido__order_number', 'descripcion', 'cliente__first_name', 'cliente__last_name')
    date_hierarchy = 'fecha_estimada'
    readonly_fields = ('creado_en', 'actualizado_en')
    
    def get_fields(self, request, obj=None):
        """Ocultar tenant para usuarios no superusuarios"""
        fields = list(super().get_fields(request, obj))
        
        # Si no es superusuario, ocultar tenant
        if not request.user.is_superuser and 'tenant' in fields:
            fields.remove('tenant')
        
        return fields
    
    def get_readonly_fields(self, request, obj=None):
        """Hacer readonly algunos campos según el usuario"""
        readonly_fields = list(super().get_readonly_fields(request, obj))
        
        # Para superusuarios, mostrar tenant pero como readonly si ya existe el objeto
        if request.user.is_superuser and obj:
            if 'tenant' not in readonly_fields:
                readonly_fields.append('tenant')
        
        return readonly_fields
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """
        Filtrar campos relacionados según el inquilino del usuario.
        Corrige el KeyError: 'queryset' asegurando que siempre exista un queryset base.
        """
        
        # Obtener el queryset base del campo
        if 'queryset' not in kwargs:
            kwargs['queryset'] = db_field.remote_field.model.objects.all()
        
        # Filtrar pedidos por tenant
        if db_field.name == "pedido":
            if request.user.is_superuser:
                # Superusuarios ven todos los pedidos
                kwargs["queryset"] = Order.objects.all()
            elif hasattr(request.user, 'tenant') and request.user.tenant:
                # Usuarios normales solo ven pedidos de su tenant
                kwargs["queryset"] = Order.objects.filter(tenant=request.user.tenant)
            else:
                # Usuario sin tenant asignado - mostrar lista vacía
                kwargs["queryset"] = Order.objects.none()
        
        # Filtrar clientes por tenant
        elif db_field.name == "cliente":
            if request.user.is_superuser:
                # Superusuarios ven todos los clientes
                kwargs["queryset"] = Cliente.objects.all()
            elif hasattr(request.user, 'tenant') and request.user.tenant:
                # Usuarios normales solo ven clientes de su tenant
                kwargs["queryset"] = Cliente.objects.filter(tenant=request.user.tenant)
            else:
                # Usuario sin tenant asignado - mostrar lista vacía
                kwargs["queryset"] = Cliente.objects.none()
        
        # Filtrar operarios por rol y tenant
        elif db_field.name == "operario":
            if request.user.is_superuser:
                # Superusuarios ven todos los operarios
                kwargs["queryset"] = User.objects.filter(role='operario')
            elif hasattr(request.user, 'tenant') and request.user.tenant:
                # Usuarios normales solo ven operarios de su tenant
                kwargs["queryset"] = User.objects.filter(
                    role='operario',
                    tenant=request.user.tenant
                )
            else:
                # Usuario sin tenant asignado - mostrar lista vacía
                kwargs["queryset"] = User.objects.none()
        
        # Filtrar tenants
        elif db_field.name == "tenant":
            if request.user.is_superuser:
                # Superusuarios ven todos los tenants
                kwargs["queryset"] = Tenant.objects.all()
            elif hasattr(request.user, 'tenant') and request.user.tenant:
                # Usuarios normales solo ven su tenant
                kwargs["queryset"] = Tenant.objects.filter(id=request.user.tenant.id)
            else:
                # Usuario sin tenant asignado - mostrar lista vacía
                kwargs["queryset"] = Tenant.objects.none()
        
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
    
    def get_queryset(self, request):
        """Filtrar órdenes por tenant del usuario"""
        qs = super().get_queryset(request)
        
        # Superusuarios ven todas las órdenes
        if request.user.is_superuser:
            return qs
        
        # Usuarios normales solo ven de su tenant
        if hasattr(request.user, 'tenant') and request.user.tenant:
            return qs.filter(tenant=request.user.tenant)
        
        # Usuario sin tenant asignado - no ve nada
        return qs.none()
    
    def save_model(self, request, obj, form, change):
        """Asignar automáticamente el tenant del usuario"""
        
        # Si no es superusuario, asignar automáticamente su tenant
        if not request.user.is_superuser:
            if hasattr(request.user, 'tenant') and request.user.tenant:
                obj.tenant = request.user.tenant
        
        # Asignar usuario que crea/modifica
        if not change:  # Solo al crear
            obj.creado_por = request.user
        
        super().save_model(request, obj, form, change)
    
    def has_add_permission(self, request):
        """Verificar permisos para agregar órdenes"""
        # Usuarios sin tenant no pueden crear órdenes
        if not request.user.is_superuser:
            if not (hasattr(request.user, 'tenant') and request.user.tenant):
                return False
        return super().has_add_permission(request)
    
    def has_change_permission(self, request, obj=None):
        """Verificar permisos para modificar órdenes"""
        if not request.user.is_superuser and obj:
            # Solo puede modificar órdenes de su tenant
            if hasattr(request.user, 'tenant') and request.user.tenant:
                return obj.tenant == request.user.tenant
            return False
        return super().has_change_permission(request, obj)
    
    def has_delete_permission(self, request, obj=None):
        """Verificar permisos para eliminar órdenes"""
        if not request.user.is_superuser and obj:
            # Solo puede eliminar órdenes de su tenant
            if hasattr(request.user, 'tenant') and request.user.tenant:
                return obj.tenant == request.user.tenant
            return False
        return super().has_delete_permission(request, obj)