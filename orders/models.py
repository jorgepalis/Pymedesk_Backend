from django.db import models
from users.models import User
from products.models import Product
from decimal import Decimal



class Order(models.Model):
    """Modelo para órdenes de compra"""

    STATUS_CHOICES = [
        ('PENDING', 'En proceso'),
        ('COMPLETED', 'Completado'),
        ('CANCELLED', 'Cancelado'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'
        ordering = ['-created_at']

    def __str__(self):
        return f'Order {self.id} by {self.user.email}'
    

class OrderItem(models.Model):
    """Modelo para items dentro de una orden"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = 'Order Item'
        verbose_name_plural = 'Order Items'

    def __str__(self):
        return f'{self.quantity} x {self.product.name} in Order {self.order.id}'
    
    def save(self, *args, **kwargs):
        self.subtotal = Decimal(self.product.price * self.quantity)
        super().save(*args, **kwargs)
        # Recalcular el total de la orden con todos los items
        total = Decimal(sum(item.subtotal for item in self.order.items.all()))
        self.order.total_price = total
        self.order.save(update_fields=['total_price'])