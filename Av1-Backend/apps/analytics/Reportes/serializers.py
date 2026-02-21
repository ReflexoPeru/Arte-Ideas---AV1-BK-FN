"""
Analytics Serializers - Arte Ideas
"""
from rest_framework import serializers


class MetricCardSerializer(serializers.Serializer):
    """Serializer para tarjetas de métricas"""
    label = serializers.CharField()
    value = serializers.CharField()
    icon = serializers.CharField(required=False, allow_blank=True)
    color = serializers.CharField(required=False, allow_blank=True)


class ReportMetricsSerializer(serializers.Serializer):
    """Serializer para métricas de reportes"""
    # Métricas genéricas que se mapean según la categoría
    pass


class ReportDetailSerializer(serializers.Serializer):
    """Serializer para tablas de detalle de reportes"""
    pass


class ReportSerializer(serializers.Serializer):
    """Serializer principal para reportes"""
    categoria = serializers.CharField()
    titulo = serializers.CharField()
    periodo_inicio = serializers.CharField()  # Se recibe como string ISO format
    periodo_fin = serializers.CharField()  # Se recibe como string ISO format
    metricas = serializers.DictField()
    detalle = serializers.ListField(child=serializers.DictField())
    fecha_generacion = serializers.CharField()  # Se recibe como string ISO format
