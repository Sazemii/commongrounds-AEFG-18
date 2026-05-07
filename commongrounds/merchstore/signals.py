"""Observer pattern: post_save signal on Transaction.

When a Transaction is created the handler deducts the bought amount from the
related Product's stock and flips the Product's status to "Out of stock" if
stock reaches zero.
"""

from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Product, Transaction


@receiver(post_save, sender=Transaction)
def deduct_product_stock(sender, instance, created, **kwargs):
    if not created:
        return
    product = instance.product
    new_stock = max(product.stock - instance.amount, 0)
    product.stock = new_stock
    if new_stock == 0:
        product.status = Product.STATUS_OUT_OF_STOCK
    elif product.status == Product.STATUS_OUT_OF_STOCK:
        product.status = Product.STATUS_AVAILABLE
    product.save()
