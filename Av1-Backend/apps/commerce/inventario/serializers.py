"""
Serializers del Módulo de Inventario - Arte Ideas Commerce
"""
from rest_framework import serializers
from .models import (
    MolduraListon, MolduraPrearmada, VidrioTapaMDF, Paspartu,
    Minilab, Cuadro, Anuario, CorteLaser, MarcoAccesorio, HerramientaGeneral
)


class BaseInventarioSerializer(serializers.ModelSerializer):
    """Serializer base para todos los modelos de inventario"""
    costo_total = serializers.ReadOnlyField()
    alerta_stock = serializers.ReadOnlyField()
    
    class Meta:
        fields = [
            'id', 'nombre_producto', 'stock_disponible', 'stock_minimo',
            'costo_unitario', 'precio_venta', 'codigo_producto',
            'ubicacion', 'proveedor', 'fecha_ultima_compra',
            'is_active', 'costo_total', 'alerta_stock',
            'fecha_creacion', 'fecha_actualizacion'
        ]
        read_only_fields = ['id', 'costo_total', 'alerta_stock', 'fecha_creacion', 'fecha_actualizacion']


# CATEGORÍA: ENMARCADOS
class MolduraListonSerializer(BaseInventarioSerializer):
    """Serializer para Moldura (Listón)"""
    nombre_moldura_display = serializers.CharField(source='get_nombre_moldura_display', read_only=True)
    ancho_display = serializers.CharField(source='get_ancho_display', read_only=True)
    color_display = serializers.CharField(source='get_color_display', read_only=True)
    material_display = serializers.CharField(source='get_material_display', read_only=True)
    
    class Meta(BaseInventarioSerializer.Meta):
        model = MolduraListon
        fields = BaseInventarioSerializer.Meta.fields + [
            'nombre_moldura', 'nombre_moldura_display',
            'ancho', 'ancho_display',
            'color', 'color_display',
            'material', 'material_display'
        ]


class MolduraPrearmadaSerializer(BaseInventarioSerializer):
    """Serializer para Moldura Prearmada"""
    dimensiones_display = serializers.CharField(source='get_dimensiones_display', read_only=True)
    color_display = serializers.CharField(source='get_color_display', read_only=True)
    material_display = serializers.CharField(source='get_material_display', read_only=True)
    
    class Meta(BaseInventarioSerializer.Meta):
        model = MolduraPrearmada
        fields = BaseInventarioSerializer.Meta.fields + [
            'dimensiones', 'dimensiones_display',
            'color', 'color_display',
            'material', 'material_display'
        ]


class VidrioTapaMDFSerializer(BaseInventarioSerializer):
    """Serializer para Vidrio o Tapa MDF"""
    tipo_material_display = serializers.CharField(source='get_tipo_material_display', read_only=True)
    tipo_vidrio_display = serializers.CharField(source='get_tipo_vidrio_display', read_only=True)
    grosor_display = serializers.CharField(source='get_grosor_display', read_only=True)
    tamaño_display = serializers.CharField(source='get_tamaño_display', read_only=True)
    
    class Meta(BaseInventarioSerializer.Meta):
        model = VidrioTapaMDF
        fields = BaseInventarioSerializer.Meta.fields + [
            'tipo_material', 'tipo_material_display',
            'tipo_vidrio', 'tipo_vidrio_display',
            'grosor', 'grosor_display',
            'tamaño', 'tamaño_display'
        ]


class PaspartuSerializer(BaseInventarioSerializer):
    """Serializer para Paspartú"""
    tipo_material_display = serializers.CharField(source='get_tipo_material_display', read_only=True)
    tamaño_display = serializers.CharField(source='get_tamaño_display', read_only=True)
    grosor_display = serializers.CharField(source='get_grosor_display', read_only=True)
    color_display = serializers.CharField(source='get_color_display', read_only=True)
    
    class Meta(BaseInventarioSerializer.Meta):
        model = Paspartu
        fields = BaseInventarioSerializer.Meta.fields + [
            'tipo_material', 'tipo_material_display',
            'tamaño', 'tamaño_display',
            'grosor', 'grosor_display',
            'color', 'color_display'
        ]


# CATEGORÍA: MINILAB
class MinilabSerializer(BaseInventarioSerializer):
    """Serializer para Minilab"""
    tipo_insumo_display = serializers.CharField(source='get_tipo_insumo_display', read_only=True)
    nombre_tipo_display = serializers.CharField(source='get_nombre_tipo_display', read_only=True)
    tamaño_presentacion_display = serializers.CharField(source='get_tamaño_presentacion_display', read_only=True)
    
    class Meta(BaseInventarioSerializer.Meta):
        model = Minilab
        fields = BaseInventarioSerializer.Meta.fields + [
            'tipo_insumo', 'tipo_insumo_display',
            'nombre_tipo', 'nombre_tipo_display',
            'tamaño_presentacion', 'tamaño_presentacion_display',
            'fecha_compra'
        ]


# CATEGORÍA: GRADUACIONES
class CuadroSerializer(BaseInventarioSerializer):
    """Serializer para Cuadro"""
    formato_display = serializers.CharField(source='get_formato_display', read_only=True)
    dimensiones_display = serializers.CharField(source='get_dimensiones_display', read_only=True)
    material_display = serializers.CharField(source='get_material_display', read_only=True)
    
    class Meta(BaseInventarioSerializer.Meta):
        model = Cuadro
        fields = BaseInventarioSerializer.Meta.fields + [
            'formato', 'formato_display',
            'dimensiones', 'dimensiones_display',
            'material', 'material_display'
        ]


class AnuarioSerializer(BaseInventarioSerializer):
    """Serializer para Anuario"""
    formato_display = serializers.CharField(source='get_formato_display', read_only=True)
    paginas_display = serializers.CharField(source='get_paginas_display', read_only=True)
    tipo_tapa_display = serializers.CharField(source='get_tipo_tapa_display', read_only=True)
    
    class Meta(BaseInventarioSerializer.Meta):
        model = Anuario
        fields = BaseInventarioSerializer.Meta.fields + [
            'formato', 'formato_display',
            'paginas', 'paginas_display',
            'tipo_tapa', 'tipo_tapa_display'
        ]


# CATEGORÍA: CORTE LÁSER
class CorteLaserSerializer(BaseInventarioSerializer):
    """Serializer para Corte Láser"""
    producto_display = serializers.CharField(source='get_producto_display', read_only=True)
    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)
    tamaño_display = serializers.CharField(source='get_tamaño_display', read_only=True)
    color_display = serializers.CharField(source='get_color_display', read_only=True)
    unidad_display = serializers.CharField(source='get_unidad_display', read_only=True)
    
    class Meta(BaseInventarioSerializer.Meta):
        model = CorteLaser
        fields = BaseInventarioSerializer.Meta.fields + [
            'producto', 'producto_display',
            'tipo', 'tipo_display',
            'tamaño', 'tamaño_display',
            'color', 'color_display',
            'unidad', 'unidad_display'
        ]


# CATEGORÍA: ACCESORIOS
class MarcoAccesorioSerializer(BaseInventarioSerializer):
    """Serializer para Marco y Accesorio"""
    tipo_moldura_display = serializers.CharField(source='get_tipo_moldura_display', read_only=True)
    material_display = serializers.CharField(source='get_material_display', read_only=True)
    color_display = serializers.CharField(source='get_color_display', read_only=True)
    
    class Meta(BaseInventarioSerializer.Meta):
        model = MarcoAccesorio
        fields = BaseInventarioSerializer.Meta.fields + [
            'nombre_moldura', 'tipo_moldura', 'tipo_moldura_display',
            'material', 'material_display',
            'color', 'color_display',
            'dimensiones'
        ]


class HerramientaGeneralSerializer(BaseInventarioSerializer):
    """Serializer para Herramienta General"""
    marca_display = serializers.CharField(source='get_marca_display', read_only=True)
    tipo_material_display = serializers.CharField(source='get_tipo_material_display', read_only=True)
    
    class Meta(BaseInventarioSerializer.Meta):
        model = HerramientaGeneral
        fields = BaseInventarioSerializer.Meta.fields + [
            'nombre_herramienta',
            'marca', 'marca_display',
            'tipo_material', 'tipo_material_display'
        ]