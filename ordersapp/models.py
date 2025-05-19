from django.db import models
from userapp.models import User
from productsapp.models import Product


# Create your models here.


class Order(models.Model):
    VALID_STATUS_CHOICES = [
        ("valid", "Valid"),
        ("invalid", "Invalid"),
    ]
    PAYMENT_STATUS_CHOICES = [
        ("paid", "Paid"),
        ("unpaid", "Unpaid"),
        ("refunded", "Refunded"),
    ]

    order_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    valid_status = models.CharField(max_length=10, choices=VALID_STATUS_CHOICES)
    payment_status = models.CharField(
        max_length=10, choices=PAYMENT_STATUS_CHOICES, db_index=True
    )
    payment_time = models.DateTimeField(null=True, blank=True, db_index=True)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    quantity = models.IntegerField()
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, db_index=True)
    logistics_id = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = "order"
        indexes = [
            models.Index(fields=["user", "product"]),
            models.Index(fields=["user", "valid_status"]),
        ]

    def __str__(self):
        return f"Order {self.order_id}"

class LogisticsStatus(models.Model):
    SHIPPING_STATUS_CHOICES = [
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('in_transit', 'In Transit'),
        ('delivered', 'Delivered'),
    ]
    
    logistics_id = models.AutoField(primary_key=True)
    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    origin = models.CharField(max_length=100)
    current_location = models.CharField(max_length=100, db_index=True)
    destination = models.CharField(max_length=100)
    shipping_status = models.CharField(max_length=20, choices=SHIPPING_STATUS_CHOICES)
    
    class Meta:
        db_table = 'logistics_status'
        
    def __str__(self):
        return f"Logistics {self.logistics_id}"