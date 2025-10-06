from rest_framework import viewsets, permissions
from .models import Product
from .serializers import ProductSerializer
from users import permissions as user_permissions
from drf_spectacular.utils import extend_schema

@extend_schema(tags=["Products"])
class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def get_permissions(self):
            if self.action in ['list', 'retrieve']:
                # Público
                permission_classes = [permissions.AllowAny]
            else:
                # Solo admin autenticado
                permission_classes = [user_permissions.IsAdmin]
            return [permission() for permission in permission_classes]

