"""
Views del Módulo de Clientes - Arte Ideas CRM
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db.models import Count, Q

from .models import Cliente, HistorialCliente, ContactoCliente
from .serializers import (
    ClienteSerializer, ClienteListSerializer, HistorialClienteSerializer,
    ContactoClienteSerializer, ClienteEstadisticasSerializer
)


class ClienteViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión completa de clientes
    """
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['tipo_cliente', 'activo', 'nivel_educativo']
    search_fields = ['nombres', 'apellidos', 'email', 'telefono', 'dni', 'razon_social']
    ordering_fields = ['nombres', 'apellidos', 'creado_en']
    ordering = ['apellidos', 'nombres']

    def get_serializer_class(self):
        if self.action == 'list':
            return ClienteListSerializer
        return ClienteSerializer

    def get_queryset(self):
        """Filtrar clientes por tenant del usuario"""
        if self.request.user.is_superuser:
            return Cliente.objects.all()
        return Cliente.objects.filter(tenant=self.request.user.tenant)

    def perform_create(self, serializer):
        """Asignar tenant automáticamente al crear"""
        serializer.save(tenant=self.request.user.tenant)

    @action(detail=False, methods=['get'])
    def estadisticas(self, request):
        """Obtener estadísticas de clientes"""
        queryset = self.get_queryset()
        
        total_clientes = queryset.count()
        clientes_activos = queryset.filter(activo=True).count()
        clientes_particulares = queryset.filter(tipo_cliente='particular').count()
        clientes_empresas = queryset.filter(tipo_cliente='empresa').count()
        clientes_colegios = queryset.filter(tipo_cliente='colegio').count()
        
        # Clientes por nivel educativo (solo colegios)
        colegios_inicial = queryset.filter(tipo_cliente='colegio', nivel_educativo='inicial').count()
        colegios_primaria = queryset.filter(tipo_cliente='colegio', nivel_educativo='primaria').count()
        colegios_secundaria = queryset.filter(tipo_cliente='colegio', nivel_educativo='secundaria').count()
        
        data = {
            'total_clientes': total_clientes,
            'clientes_activos': clientes_activos,
            'clientes_inactivos': total_clientes - clientes_activos,
            'por_tipo': {
                'particulares': clientes_particulares,
                'empresas': clientes_empresas,
                'colegios': clientes_colegios
            },
            'colegios_por_nivel': {
                'inicial': colegios_inicial,
                'primaria': colegios_primaria,
                'secundaria': colegios_secundaria
            }
        }
        
        serializer = ClienteEstadisticasSerializer(data)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def recientes(self, request):
        """Obtener clientes creados recientemente"""
        queryset = self.get_queryset().order_by('-creado_en')[:10]
        serializer = ClienteListSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def activar(self, request, pk=None):
        """Activar cliente"""
        cliente = self.get_object()
        cliente.activo = True
        cliente.save()
        return Response({'message': 'Cliente activado correctamente'})

    @action(detail=True, methods=['post'])
    def desactivar(self, request, pk=None):
        """Desactivar cliente"""
        cliente = self.get_object()
        cliente.activo = False
        cliente.save()
        return Response({'message': 'Cliente desactivado correctamente'})

    @action(detail=True, methods=['get'])
    def historial(self, request, pk=None):
        """Obtener historial de interacciones del cliente"""
        cliente = self.get_object()
        historial = HistorialCliente.objects.filter(cliente=cliente).order_by('-fecha')
        serializer = HistorialClienteSerializer(historial, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def agregar_interaccion(self, request, pk=None):
        """Agregar nueva interacción al historial del cliente"""
        cliente = self.get_object()
        data = request.data.copy()
        data['cliente'] = cliente.id
        data['registrado_por'] = request.user.id
        
        serializer = HistorialClienteSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def contactos(self, request, pk=None):
        """Obtener contactos adicionales del cliente"""
        cliente = self.get_object()
        contactos = ContactoCliente.objects.filter(cliente=cliente)
        serializer = ContactoClienteSerializer(contactos, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def agregar_contacto(self, request, pk=None):
        """Agregar nuevo contacto al cliente"""
        cliente = self.get_object()
        data = request.data.copy()
        data['cliente'] = cliente.id
        
        serializer = ContactoClienteSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class HistorialClienteViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión del historial de clientes
    """
    serializer_class = HistorialClienteSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['tipo_interaccion', 'cliente']
    search_fields = ['descripcion', 'resultado', 'cliente__nombres', 'cliente__apellidos']
    ordering = ['-fecha']

    def get_queryset(self):
        """Filtrar historial por tenant del usuario"""
        if self.request.user.is_superuser:
            return HistorialCliente.objects.all()
        return HistorialCliente.objects.filter(cliente__tenant=self.request.user.tenant)

    def perform_create(self, serializer):
        """Asignar usuario automáticamente al crear"""
        serializer.save(registrado_por=self.request.user)


class ContactoClienteViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión de contactos de clientes
    """
    serializer_class = ContactoClienteSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['cliente', 'es_principal']
    search_fields = ['nombre', 'cargo', 'email', 'telefono']
    ordering = ['-es_principal', 'nombre']

    def get_queryset(self):
        """Filtrar contactos por tenant del usuario"""
        if self.request.user.is_superuser:
            return ContactoCliente.objects.all()
        return ContactoCliente.objects.filter(cliente__tenant=self.request.user.tenant)