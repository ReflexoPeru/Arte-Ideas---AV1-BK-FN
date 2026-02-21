"""
Serializers del Commerce App - Arte Ideas
Serializers básicos para compatibilidad con código legacy
"""
from rest_framework import serializers
from .models import Product


class ProductSerializer(serializers.ModelSerializer):
    """
    Serializer básico para productos legacy
    NOTA: Para nuevos desarrollos, usar los serializers específicos del módulo inventario
    """
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'description', 'product_type', 
            'unit_price', 'cost_price', 'stock_quantity', 'min_stock',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate_unit_price(self, value):
        if value < 0:
            raise serializers.ValidationError("El precio unitario no puede ser negativo")
        return value
    
    def validate_cost_price(self, value):
        if value < 0:
            raise serializers.ValidationError("El precio de costo no puede ser negativo")
        return value
    
    def validate_stock_quantity(self, value):
        if value < 0:
            raise serializers.ValidationError("El stock no puede ser negativo")
        return value
    
    def validate_min_stock(self, value):
        if value < 0:
            raise serializers.ValidationError("El stock mínimo no puede ser negativo")
        return value