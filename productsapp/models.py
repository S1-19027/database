from django.db import models
from userapp.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


# Create your models here.
class Category(models.Model):
    category_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50, db_index=True)
    description = models.TextField(blank=True)

    class Meta:
        db_table = "category"


class Product(models.Model):
    product_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, db_index=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True)
    sales = models.IntegerField(default=0)
    stock = models.IntegerField()
    listing_time = models.DateTimeField()
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)

    class Meta:
        db_table = "product"
        indexes = [
            models.Index(fields=["name", "price", "sales"]),
        ]


class ProductReview(models.Model):
    review_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, db_index=True)
    content = models.TextField()
    review_time = models.DateTimeField()
    rating = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(5)])

    class Meta:
        db_table = "product_review"
        indexes = [
            models.Index(fields=["review_time"]),
        ]
