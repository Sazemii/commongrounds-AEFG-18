from django.core.validators import MinValueValidator
from django.db import models
from django.urls import reverse
from decimal import Decimal
from accounts.models import Profile


class ProductType(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Product(models.Model):
    STATUS_CHOICES = [
        ('Available', 'Available'),
        ('On sale', 'On sale'),
        ('Out of stock', 'Out of stock'),
    ]

    name = models.CharField(max_length=255)
    product_type = models.ForeignKey(
        ProductType, on_delete=models.SET_NULL, null=True, editable=False)
    owner = models.ForeignKey(
        Profile, on_delete=models.CASCADE)
    product_image = models.ImageField(
        upload_to='merchstore/images/', null=True, blank=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=20,
                                decimal_places=2,
                                validators=[MinValueValidator(Decimal('0.01'))])
    stock = models.PositiveIntegerField()
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Available'
    )

    class Meta:
        ordering = ['name']

    def get_absolute_url(self):
        return reverse('merchstore:product-detail', kwargs={'pk': self.pk})

    def __str__(self):
        return self.name


class Transaction(models.Model):
    STATUS_CHOICES = [
        ('On cart', 'On cart'),
        ('To Pay', 'To Pay'),
        ('To Ship', 'To Ship'),
        ('To Receive', 'To Receive'),
        ('Delivered', 'Delivered'),
    ]

    buyer = models.ForeignKey(
        Profile, on_delete=models.SET_NULL, null=True)
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE)
    amount = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES
    )
    created_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Transaction for {self.product.name} by {self.buyer}"
