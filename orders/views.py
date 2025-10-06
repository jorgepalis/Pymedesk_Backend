from rest_framework import viewsets, permissions
from .models import Order, OrderItem
from .serializers import OrderSerializer, OrderItemSerializer, OrderCreateSerializer
from users import permissions as user_permissions
from drf_spectacular.utils import extend_schema


@extend_schema(tags=["Orders"])
class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer

    def get_queryset(self):
        user = self.request.user
        # Si el usuario es admin, ve todas las órdenes
        if user.is_authenticated and user.role.name.lower() == 'admin':
            return Order.objects.all()
        # Si es cliente autenticado, ve solo las suyas
        elif user.is_authenticated and user.role.name.lower() == 'client':
            return Order.objects.filter(user=user)
        # Si no está autenticado, no puede ver nada
        return Order.objects.none()

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            # Solo autenticados (clientes o admins)
            permission_classes = [permissions.IsAuthenticated]
        elif self.action in ['create']:
            # Clientes y admins pueden crear
            permission_classes = [user_permissions.IsAdmin | user_permissions.IsClient]
        else:
            # Solo admin puede editar o eliminar
            permission_classes = [user_permissions.IsAdmin]
        return [permission() for permission in permission_classes]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return OrderCreateSerializer
        return OrderSerializer
    

