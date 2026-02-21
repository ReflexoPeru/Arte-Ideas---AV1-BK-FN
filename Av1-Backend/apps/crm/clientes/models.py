"""
Modelos de Clientes - Arte Ideas CRM
Gestión de clientes: particulares, colegios y empresas
"""
from django.db import models
from django.core.exceptions import ValidationError
from django.conf import settings
from apps.core.models import Tenant


class Cliente(models.Model):
    """
    Modelo para clientes del estudio fotográfico
    Soporta diferentes tipos de clientes: Particular, Colegio, Empresa
    """
    TIPO_CLIENTE_CHOICES = [
        ('particular', 'Particular'),
        ('colegio', 'Colegio'),
        ('empresa', 'Empresa'),
    ]
    
    id = models.AutoField(primary_key=True)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, verbose_name='Estudio Fotográfico')
    
    # Información básica del cliente
    tipo_cliente = models.CharField(
        max_length=20, 
        choices=TIPO_CLIENTE_CHOICES, 
        default='particular',
        verbose_name='Tipo de Cliente'
    )
    nombres = models.CharField(max_length=100, verbose_name='Nombres')
    apellidos = models.CharField(max_length=100, verbose_name='Apellidos')
    email = models.EmailField(verbose_name='Email')
    telefono = models.CharField(max_length=15, verbose_name='Teléfono')
    dni = models.CharField(max_length=15, verbose_name='DNI/RUC', unique=True)
    direccion = models.TextField(verbose_name='Dirección')
    
    # Campos específicos para colegios
    nivel_educativo = models.CharField(
        max_length=20,
        choices=[
            ('inicial', 'Inicial'),
            ('primaria', 'Primaria'),
            ('secundaria', 'Secundaria'),
        ],
        blank=True,
        null=True,
        verbose_name='Nivel (Colegios)'
    )
    grado = models.CharField(max_length=50, blank=True, null=True, verbose_name='Grado (Colegios)')
    seccion = models.CharField(max_length=50, blank=True, null=True, verbose_name='Sección (Colegios)')
    
    # Campos específicos para empresas
    razon_social = models.CharField(max_length=200, blank=True, null=True, verbose_name='Razón Social')
    
    # Estado del cliente
    activo = models.BooleanField(default=True, verbose_name='Activo')
    
    # Fechas importantes
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'
        ordering = ['apellidos', 'nombres']
        unique_together = ['tenant', 'dni']
    
    def __str__(self):
        if self.tipo_cliente == 'empresa' and self.razon_social:
            return f"{self.razon_social} - {self.obtener_nombre_completo()}"
        return self.obtener_nombre_completo()
    
    def obtener_nombre_completo(self):
        """Obtener nombre completo del cliente"""
        return f"{self.nombres} {self.apellidos}".strip()
    
    def clean(self):
        """Validaciones personalizadas"""
        # Validar campos requeridos según tipo de cliente
        if self.tipo_cliente == 'empresa' and not self.razon_social:
            raise ValidationError({'razon_social': 'La razón social es obligatoria para empresas'})
        
        # Validar formato de DNI/RUC
        if self.dni:
            self.dni = self.dni.strip()
            if not self.dni.replace('-', '').replace(' ', '').isalnum():
                raise ValidationError({'dni': 'El DNI/RUC debe contener solo números, letras y guiones'})
    
    def save(self, *args, **kwargs):
        """Guardar con validaciones"""
        self.full_clean()
        super().save(*args, **kwargs)


class HistorialCliente(models.Model):
    """
    Historial de interacciones con el cliente
    """
    TIPO_INTERACCION_CHOICES = [
        ('llamada', 'Llamada Telefónica'),
        ('email', 'Correo Electrónico'),
        ('reunion', 'Reunión Presencial'),
        ('whatsapp', 'WhatsApp'),
        ('visita', 'Visita al Estudio'),
        ('evento', 'Evento/Sesión'),
        ('otro', 'Otro'),
    ]
    
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='historial')
    tipo_interaccion = models.CharField(max_length=20, choices=TIPO_INTERACCION_CHOICES, verbose_name='Tipo')
    fecha = models.DateTimeField(verbose_name='Fecha y Hora')
    descripcion = models.TextField(verbose_name='Descripción')
    resultado = models.TextField(blank=True, verbose_name='Resultado')
    
    # Usuario que registra la interacción
    registrado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        verbose_name='Registrado Por'
    )
    
    creado_en = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Historial de Cliente'
        verbose_name_plural = 'Historiales de Cliente'
        ordering = ['-fecha']
    
    def __str__(self):
        return f"{self.cliente.obtener_nombre_completo()} - {self.get_tipo_interaccion_display()} - {self.fecha}"


class ContactoCliente(models.Model):
    """
    Contactos adicionales del cliente (para empresas y colegios)
    """
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='contactos')
    nombre = models.CharField(max_length=100, verbose_name='Nombre del Contacto')
    cargo = models.CharField(max_length=100, blank=True, verbose_name='Cargo')
    telefono = models.CharField(max_length=15, blank=True, verbose_name='Teléfono')
    email = models.EmailField(blank=True, verbose_name='Email')
    es_principal = models.BooleanField(default=False, verbose_name='Contacto Principal')
    
    creado_en = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Contacto de Cliente'
        verbose_name_plural = 'Contactos de Cliente'
        ordering = ['-es_principal', 'nombre']
    
    def __str__(self):
        return f"{self.nombre} - {self.cliente.obtener_nombre_completo()}"