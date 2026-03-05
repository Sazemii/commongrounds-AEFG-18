from django.contrib import admin
from .models import ProductType, Product


class ProductInLine(admin.TabularInline):
    model = Product


class ProductTypeAdmin(admin.ModelAdmin):
    model = ProductType
    search_fields = ('name', 'description')
    list_display = ('name', 'description')
    inlines = [ProductInLine,]


class ProductAdmin(admin.ModelAdmin):
    model = Product
    search_fields = ('name', 'description', 'price')
    list_display = ('name', 'description', 'price')
    list_filter = ('product_type',)


admin.site.register(ProductType, ProductTypeAdmin)
admin.site.register(Product, ProductAdmin)
