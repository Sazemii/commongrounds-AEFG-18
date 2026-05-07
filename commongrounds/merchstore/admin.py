from django.contrib import admin

from .models import Product, ProductType, Transaction


class ProductInLine(admin.TabularInline):
    model = Product
    fields = ('name', 'price', 'stock', 'status')
    extra = 0


class ProductTypeAdmin(admin.ModelAdmin):
    search_fields = ('name', 'description')
    list_display = ('name', 'description')
    inlines = [ProductInLine]


class ProductAdmin(admin.ModelAdmin):
    search_fields = ('name', 'description')
    list_display = ('name', 'owner', 'product_type', 'price', 'stock', 'status')
    list_filter = ('product_type', 'status')


class TransactionAdmin(admin.ModelAdmin):
    list_display = ('product', 'buyer', 'amount', 'status', 'created_on')
    list_filter = ('status',)


admin.site.register(ProductType, ProductTypeAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Transaction, TransactionAdmin)
