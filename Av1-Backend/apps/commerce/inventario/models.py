"""
Modelos de Inventario - Arte Ideas Commerce
Gestión completa de inventario y stock de productos
"""
from django.db import models
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from decimal import Decimal
from apps.core.models import Tenant


class BaseInventarioModel(models.Model):
    """Modelo base para todos los productos del inventario"""
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, verbose_name='Estudio Fotográfico')
    nombre_producto = models.CharField(max_length=200, verbose_name="Nombre del Producto")
    stock_disponible = models.PositiveIntegerField(verbose_name="Stock Disponible")
    stock_minimo = models.PositiveIntegerField(verbose_name="Stock Mínimo", default=0)
    costo_unitario = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name="Costo Unitario (S/)"
    )
    precio_venta = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0,
        verbose_name="Precio de Venta (S/)"
    )
    codigo_producto = models.CharField(max_length=50, blank=True, verbose_name="Código del Producto")
    ubicacion = models.CharField(max_length=100, blank=True, verbose_name="Ubicación en Almacén")
    proveedor = models.CharField(max_length=200, blank=True, verbose_name="Proveedor")
    fecha_ultima_compra = models.DateField(null=True, blank=True, verbose_name="Última Compra")
    is_active = models.BooleanField(default=True, verbose_name="Activo")
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True
    
    @property
    def costo_total(self):
        """Calcula el costo total: costo_unitario * stock_disponible"""
        if self.costo_unitario is None or self.stock_disponible is None:
            return 0
        return self.costo_unitario * self.stock_disponible
    
    @property
    def alerta_stock(self):
        """Verifica si el stock está en nivel de alerta"""
        # Manejar casos donde los valores pueden ser None (al crear nuevo objeto)
        if self.stock_disponible is None or self.stock_minimo is None:
            return False
        return self.stock_disponible <= self.stock_minimo


# CATEGORÍA: ENMARCADOS
class MolduraListon(BaseInventarioModel):
    """Subcategoría: Moldura (Listón)"""
    NOMBRES_MOLDURA = [
        ('clasica', 'Clásica'),
        ('moderna', 'Moderna'),
    ]
    
    ANCHOS = [
        ('1', '1"'),
        ('1.5', '1.5"'),
    ]
    
    COLORES = [
        ('dorado', 'Dorado'),
        ('plateado', 'Plateado'),
    ]
    
    MATERIALES = [
        ('madera', 'Madera'),
        ('aluminio', 'Aluminio'),
    ]
    
    nombre_moldura = models.CharField(max_length=50, choices=NOMBRES_MOLDURA, verbose_name="Nombre de Moldura")
    ancho = models.CharField(max_length=10, choices=ANCHOS, verbose_name="Ancho (pulgadas)")
    color = models.CharField(max_length=50, choices=COLORES, verbose_name="Color")
    material = models.CharField(max_length=50, choices=MATERIALES, verbose_name="Material")
    
    class Meta:
        verbose_name = "Moldura (Listón)"
        verbose_name_plural = "Molduras (Listones)"


class MolduraPrearmada(BaseInventarioModel):
    """Subcategoría: Moldura Prearmada"""
    DIMENSIONES = [
        ('20x25', '20x25cm'),
        ('30x40', '30x40cm'),
    ]
    
    COLORES = [
        ('dorado', 'Dorado'),
        ('plateado', 'Plateado'),
    ]
    
    MATERIALES = [
        ('madera', 'Madera'),
        ('aluminio', 'Aluminio'),
    ]
    
    dimensiones = models.CharField(max_length=20, choices=DIMENSIONES, verbose_name="Dimensiones")
    color = models.CharField(max_length=50, choices=COLORES, verbose_name="Color")
    material = models.CharField(max_length=50, choices=MATERIALES, verbose_name="Material")
    
    class Meta:
        verbose_name = "Moldura Prearmada"
        verbose_name_plural = "Molduras Prearmadas"


class VidrioTapaMDF(BaseInventarioModel):
    """Subcategoría: Vidrio o Tapa MDF"""
    TIPOS_MATERIAL = [
        ('vidrio', 'Vidrio'),
        ('tapa_mdf', 'Tapa MDF'),
    ]
    
    TIPOS_VIDRIO = [
        ('comun', 'Común'),
        ('antireflejo', 'Antireflejo'),
    ]
    
    GROSORES = [
        ('2', '2mm'),
        ('3', '3mm'),
    ]
    
    TAMAÑOS = [
        ('20x25', '20x25cm'),
        ('30x40', '30x40cm'),
    ]
    
    tipo_material = models.CharField(max_length=20, choices=TIPOS_MATERIAL, verbose_name="Tipo de Material")
    tipo_vidrio = models.CharField(max_length=20, choices=TIPOS_VIDRIO, blank=True, null=True, verbose_name="Tipo de Vidrio")
    grosor = models.CharField(max_length=10, choices=GROSORES, verbose_name="Grosor (mm)")
    tamaño = models.CharField(max_length=20, choices=TAMAÑOS, verbose_name="Tamaño (cm)")
    
    class Meta:
        verbose_name = "Vidrio o Tapa MDF"
        verbose_name_plural = "Vidrios o Tapas MDF"


class Paspartu(BaseInventarioModel):
    """Subcategoría: Paspartú"""
    TIPOS_MATERIAL = [
        ('estandar', 'Estándar'),
        ('premium', 'Premium'),
    ]
    
    TAMAÑOS = [
        ('30x40', '30x40cm'),
        ('40x50', '40x50cm'),
    ]
    
    GROSORES = [
        ('1.5', '1.5mm'),
        ('2', '2mm'),
    ]
    
    COLORES = [
        ('blanco', 'Blanco'),
        ('crema', 'Crema'),
    ]
    
    tipo_material = models.CharField(max_length=20, choices=TIPOS_MATERIAL, verbose_name="Tipo de Material")
    tamaño = models.CharField(max_length=20, choices=TAMAÑOS, verbose_name="Tamaño (cm)")
    grosor = models.CharField(max_length=10, choices=GROSORES, verbose_name="Grosor (mm)")
    color = models.CharField(max_length=50, choices=COLORES, verbose_name="Color")
    
    class Meta:
        verbose_name = "Paspartú"
        verbose_name_plural = "Paspartús"


# CATEGORÍA: MINILAB
class Minilab(BaseInventarioModel):
    """Categoría: Minilab"""
    TIPOS_INSUMO = [
        ('papel', 'Papel'),
        ('quimica', 'Química'),
        ('quimico', 'Químico'),
    ]
    
    NOMBRES_TIPO = [
        ('papel_lustre', 'Papel Lustre'),
        ('papel_mate', 'Papel Mate'),
        ('revelador_ra4', 'Revelador RA-4'),
        ('blanqueador', 'Blanqueador'),
    ]
    
    TAMAÑOS_PRESENTACION = [
        ('10x15', '10x15 cm'),
        ('20x30', '20x30 cm'),
        ('kit_5l', 'Kit 5L'),
        ('1_litro', '1 Litro'),
    ]
    
    tipo_insumo = models.CharField(max_length=20, choices=TIPOS_INSUMO, verbose_name="Tipo Insumo")
    nombre_tipo = models.CharField(max_length=50, choices=NOMBRES_TIPO, verbose_name="Nombre Tipo")
    tamaño_presentacion = models.CharField(max_length=20, choices=TAMAÑOS_PRESENTACION, verbose_name="Tamaño/Presentación")
    fecha_compra = models.DateField(verbose_name="Fecha Compra")
    
    class Meta:
        verbose_name = "Minilab"
        verbose_name_plural = "Minilab"


# CATEGORÍA: GRADUACIONES
class Cuadro(BaseInventarioModel):
    """Subcategoría: Cuadro"""
    FORMATOS = [
        ('horizontal', 'Horizontal'),
        ('vertical', 'Vertical'),
    ]
    
    DIMENSIONES = [
        ('20x25', '20x25cm'),
        ('30x40', '30x40cm'),
    ]
    
    MATERIALES = [
        ('canvas', 'Canvas'),
        ('papel_fotografico', 'Papel Fotográfico'),
    ]
    
    formato = models.CharField(max_length=20, choices=FORMATOS, verbose_name="Formato")
    dimensiones = models.CharField(max_length=20, choices=DIMENSIONES, verbose_name="Dimensiones")
    material = models.CharField(max_length=50, choices=MATERIALES, verbose_name="Material")
    
    class Meta:
        verbose_name = "Cuadro"
        verbose_name_plural = "Cuadros"


class Anuario(BaseInventarioModel):
    """Subcategoría: Anuario"""
    FORMATOS = [
        ('a4', 'A4'),
        ('a5', 'A5'),
    ]
    
    PAGINAS = [
        ('50', '50'),
        ('100', '100'),
    ]
    
    TIPOS_TAPA = [
        ('tapa_dura', 'Tapa Dura'),
        ('tapa_blanda', 'Tapa Blanda'),
    ]
    
    formato = models.CharField(max_length=10, choices=FORMATOS, verbose_name="Formato")
    paginas = models.CharField(max_length=10, choices=PAGINAS, verbose_name="Páginas")
    tipo_tapa = models.CharField(max_length=20, choices=TIPOS_TAPA, verbose_name="Tipo de Tapa")
    
    class Meta:
        verbose_name = "Anuario"
        verbose_name_plural = "Anuarios"


# CATEGORÍA: CORTE LÁSER
class CorteLaser(BaseInventarioModel):
    """Categoría: Corte Láser"""
    PRODUCTOS = [
        ('plancha_mdf_jeans', 'Plancha MDF Jeans'),
        ('plancha_acrilico_3mm', 'Plancha Acrílico 3mm'),
        ('carton_microcorrugado', 'Cartón Microcorrugado'),
        ('lamina_mdf_crillada', 'Lámina MDF Crillada'),
        ('lente_enfoque', 'Lente de Enfoque'),
        ('espejo_reflector', 'Espejo Reflector'),
    ]
    
    TIPOS = [
        ('mdf', 'MDF'),
        ('acrilico', 'Acrílico'),
        ('carton', 'Cartón'),
        ('lamina_crillada', 'Lámina Crillada'),
        ('lente', 'Lente'),
        ('espejo', 'Espejo'),
    ]
    
    TAMAÑOS = [
        ('60x70', '60x70cm'),
        ('60x40', '60x40cm'),
        ('2.5', '2.5"'),
        ('1', '1"'),
    ]
    
    COLORES = [
        ('natural', 'Natural'),
        ('transparente', 'Transparente'),
        ('blanco', 'Blanco'),
        ('plateado', 'Plateado'),
    ]
    
    UNIDADES = [
        ('plancha', 'Plancha'),
        ('pieza', 'Pieza'),
    ]
    
    producto = models.CharField(max_length=50, choices=PRODUCTOS, verbose_name="Producto")
    tipo = models.CharField(max_length=30, choices=TIPOS, verbose_name="Tipo")
    tamaño = models.CharField(max_length=20, choices=TAMAÑOS, verbose_name="Tamaño")
    color = models.CharField(max_length=30, choices=COLORES, verbose_name="Color")
    unidad = models.CharField(max_length=20, choices=UNIDADES, verbose_name="Unidad")
    proveedor = models.CharField(max_length=200, blank=True, null=True, verbose_name="Proveedor")
    
    class Meta:
        verbose_name = "Corte Láser"
        verbose_name_plural = "Corte Láser"


# CATEGORÍA: ACCESORIOS
class MarcoAccesorio(BaseInventarioModel):
    """Subcategoría: Marco y Accesorio"""
    TIPOS_MOLDURA = [
        ('gancho', 'Gancho'),
        ('soporte', 'Soporte'),
    ]
    
    MATERIALES = [
        ('metal', 'Metal'),
        ('plastico', 'Plástico'),
    ]
    
    COLORES = [
        ('dorado', 'Dorado'),
        ('plateado', 'Plateado'),
    ]
    
    nombre_moldura = models.CharField(max_length=200, verbose_name="Nombre de Moldura")
    tipo_moldura = models.CharField(max_length=20, choices=TIPOS_MOLDURA, verbose_name="Tipo de Moldura")
    material = models.CharField(max_length=20, choices=MATERIALES, verbose_name="Material")
    color = models.CharField(max_length=20, choices=COLORES, verbose_name="Color")
    dimensiones = models.CharField(max_length=100, verbose_name="Dimensiones")
    
    class Meta:
        verbose_name = "Marco y Accesorio"
        verbose_name_plural = "Marcos y Accesorios"


class HerramientaGeneral(BaseInventarioModel):
    """Subcategoría: Herramienta General"""
    MARCAS = [
        ('stanley', 'Stanley'),
        ('bosch', 'Bosch'),
    ]
    
    TIPOS_MATERIAL = [
        ('cortador', 'Cortador'),
        ('regla', 'Regla'),
    ]
    
    nombre_herramienta = models.CharField(max_length=200, verbose_name="Nombre de Herramienta")
    marca = models.CharField(max_length=50, choices=MARCAS, verbose_name="Marca")
    tipo_material = models.CharField(max_length=50, choices=TIPOS_MATERIAL, verbose_name="Tipo de Material")
    
    class Meta:
        verbose_name = "Herramienta General"
        verbose_name_plural = "Herramientas Generales"