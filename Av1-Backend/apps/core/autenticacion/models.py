"""
Modelos de Autenticación - Arte Ideas
Modelos relacionados con autenticación, permisos y roles
"""
from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """
    Usuario del sistema con roles específicos para estudios fotográficos
    """
    ROLE_CHOICES = [
        ('super_admin', 'Super Administrador'),  # Ve todos los tenants
        ('admin', 'Administrador'),              # Admin del tenant
        ('ventas', 'Ventas'),                    # Usuario de ventas
        ('produccion', 'Producción'),            # Usuario de producción
        ('operario', 'Operario'),                # Usuario operario
    ]
    
    id = models.AutoField(primary_key=True)
    
    # Relación con tenant (null para super_admin)
    tenant = models.ForeignKey(
        'multitenancy.Tenant', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        verbose_name='Estudio Fotográfico'
    )
    
    # Información adicional
    phone = models.CharField(max_length=15, blank=True, verbose_name='Teléfono')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, verbose_name='Avatar')
    role = models.CharField(
        max_length=20, 
        choices=ROLE_CHOICES, 
        default='operario',
        verbose_name='Rol'
    )
    
    # Control de cuenta
    is_new_user = models.BooleanField(default=True, verbose_name='Usuario Nuevo')
    email_verified = models.BooleanField(default=False, verbose_name='Email Verificado')
    
    # Información adicional del perfil
    address = models.TextField(blank=True, verbose_name='Dirección')
    bio = models.TextField(blank=True, verbose_name='Biografía')
    
    # Fechas importantes
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        
    def __str__(self):
        return f"{self.get_full_name()} ({self.username})"
        
    def get_permissions_list(self):
        """
        Obtener lista de permisos según el rol
        Basado en la imagen de roles y permisos
        """
        permissions_map = {
            'super_admin': [
                # Acceso a módulos
                'access:dashboard', 'access:agenda', 'access:pedidos', 'access:clientes',
                'access:inventario', 'access:activos', 'access:gastos', 'access:produccion',
                'access:contratos', 'access:reportes', 'access:configuration',
                # Acciones sensibles
                'view:costos', 'view:precios', 'view:margenes', 'view:datos_clientes',
                'view:datos_financieros', 'edit:precios', 'delete:registros',
                # Gestión de usuarios y tenants
                'manage:users', 'manage:tenants', 'manage:permissions'
            ],
            'admin': [
                # Acceso a módulos (todos)
                'access:dashboard', 'access:agenda', 'access:pedidos', 'access:clientes',
                'access:inventario', 'access:activos', 'access:gastos', 'access:produccion',
                'access:contratos', 'access:reportes', 'access:configuration',
                # Acciones sensibles (todas)
                'view:costos', 'view:precios', 'view:margenes', 'view:datos_clientes',
                'view:datos_financieros', 'edit:precios', 'delete:registros',
                # Gestión dentro del tenant
                'manage:users', 'manage:permissions'
            ],
            'ventas': [
                # Acceso a módulos de ventas
                'access:dashboard', 'access:agenda', 'access:pedidos', 'access:clientes',
                'access:contratos', 'access:reportes',
                # Acciones específicas de ventas
                'view:datos_clientes', 'view:precios'
            ],
            'produccion': [
                # Acceso a módulos de producción
                'access:dashboard', 'access:produccion', 'access:inventario', 'access:activos',
                'access:pedidos', 'access:reportes',
                # Acciones específicas de producción
                'view:costos', 'view:inventario'
            ],
            'operario': [
                # Acceso básico operacional
                'access:dashboard', 'access:agenda', 'access:produccion',
                # Solo acceso de visualización básica
            ]
        }
        
        return permissions_map.get(self.role, [])
        
    def has_permission(self, permission):
        """Verificar si el usuario tiene un permiso específico"""
        return permission in self.get_permissions_list()


class RolePermission(models.Model):
    """
    Permisos específicos por rol y tenant
    """
    tenant = models.ForeignKey('multitenancy.Tenant', on_delete=models.CASCADE, verbose_name='Tenant')
    role = models.CharField(max_length=20, choices=User.ROLE_CHOICES, verbose_name='Rol')
    
    # Módulos con acceso
    access_dashboard = models.BooleanField(default=True, verbose_name='Dashboard')
    access_agenda = models.BooleanField(default=True, verbose_name='Agenda')
    access_pedidos = models.BooleanField(default=True, verbose_name='Pedidos')
    access_clientes = models.BooleanField(default=True, verbose_name='Clientes')
    access_inventario = models.BooleanField(default=False, verbose_name='Inventario')
    access_activos = models.BooleanField(default=False, verbose_name='Activos')
    access_gastos = models.BooleanField(default=False, verbose_name='Gastos')
    access_produccion = models.BooleanField(default=False, verbose_name='Producción')
    access_contratos = models.BooleanField(default=False, verbose_name='Contratos')
    access_reportes = models.BooleanField(default=False, verbose_name='Reportes')
    
    # Acciones sensibles
    view_costos = models.BooleanField(default=False, verbose_name='Ver Costos')
    view_precios = models.BooleanField(default=False, verbose_name='Ver Precios')
    view_margenes = models.BooleanField(default=False, verbose_name='Ver Márgenes')
    view_datos_clientes = models.BooleanField(default=False, verbose_name='Ver Datos de Clientes')
    view_datos_financieros = models.BooleanField(default=False, verbose_name='Ver Datos Financieros')
    edit_precios = models.BooleanField(default=False, verbose_name='Editar Precios')
    delete_registros = models.BooleanField(default=False, verbose_name='Eliminar Registros')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Permiso de Rol'
        verbose_name_plural = 'Permisos de Roles'
        unique_together = ['tenant', 'role']
    
    def __str__(self):
        return f"{self.tenant.name} - {self.get_role_display()}"
    
    @classmethod
    def get_default_permissions(cls, role):
        """Obtener permisos por defecto para un rol"""
        defaults = {
            'super_admin': {
                'access_dashboard': True, 'access_agenda': True, 'access_pedidos': True,
                'access_clientes': True, 'access_inventario': True, 'access_activos': True,
                'access_gastos': True, 'access_produccion': True, 'access_contratos': True,
                'access_reportes': True, 'view_costos': True, 'view_precios': True,
                'view_margenes': True, 'view_datos_clientes': True, 'view_datos_financieros': True,
                'edit_precios': True, 'delete_registros': True
            },
            'admin': {
                'access_dashboard': True, 'access_agenda': True, 'access_pedidos': True,
                'access_clientes': True, 'access_inventario': True, 'access_activos': True,
                'access_gastos': True, 'access_produccion': True, 'access_contratos': True,
                'access_reportes': True, 'view_costos': True, 'view_precios': True,
                'view_margenes': True, 'view_datos_clientes': True, 'view_datos_financieros': True,
                'edit_precios': True, 'delete_registros': True
            },
            'ventas': {
                'access_dashboard': True, 'access_agenda': True, 'access_pedidos': True,
                'access_clientes': True, 'access_contratos': True, 'access_reportes': True,
                'view_datos_clientes': True, 'view_precios': True
            },
            'produccion': {
                'access_dashboard': True, 'access_produccion': True, 'access_inventario': True,
                'access_activos': True, 'access_pedidos': True, 'access_reportes': True,
                'view_costos': True
            },
            'operario': {
                'access_dashboard': True, 'access_agenda': True, 'access_produccion': True
            }
        }
        return defaults.get(role, {})