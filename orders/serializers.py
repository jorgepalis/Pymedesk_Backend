from rest_framework import serializers
from products.models import Product
from .models import Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    # Campo para enviar el producto en la creación (write)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
        source='product',
        write_only=True
    )
    # Campo para mostrar el producto en la lectura (read)
    product = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_id', 'quantity', 'subtotal']
        read_only_fields = ['id', 'subtotal']

    def get_product(self, obj):
        return {
            "id": obj.product.id,
            "name": obj.product.name,
            "price": obj.product.price,
        }


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    user = serializers.SerializerMethodField(read_only=True)


    class Meta:
        model = Order
        fields = ['id', 'user', 'status', 'total_price', 'created_at', 'items']
        read_only_fields = ['id', 'total_price', 'created_at']

    def get_user(self, obj):
        return {
            "id": obj.user.id,
            "email": obj.user.email,
            "name": obj.user.name,
        }


class OrderCreateSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = ['id', 'user', 'status', 'total_price', 'items']
        read_only_fields = ['id', 'user', 'status', 'total_price']

    # Validar stock antes de crear
    def validate_items(self, items):
        for item in items:
            product = item['product']
            quantity = item['quantity']
            if product.stock < quantity:
                raise serializers.ValidationError(
                    f"No hay suficiente stock para el producto '{product.name}'. "
                    f"Disponible: {product.stock}, solicitado: {quantity}"
                )
        return items

    # Crear la orden y descontar stock
    def create(self, validated_data):
        items_data = validated_data.pop('items')
        user = self.context['request'].user


        order = Order.objects.create(user=user, **validated_data)


        for item_data in items_data:
            product = item_data['product']
            quantity = item_data['quantity']

            # Descontar stock del producto
            product.stock -= quantity
            product.save()

            # Crear el OrderItem
            OrderItem.objects.create(order=order, **item_data)

        return order
