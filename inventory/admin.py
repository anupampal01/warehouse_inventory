from django.contrib import admin
from .models import Product, StockTransaction, StockDetail

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'stock_quantity')
    search_fields = ('name',)

@admin.register(StockTransaction)
class StockTransactionAdmin(admin.ModelAdmin):
    list_display = ('transaction_type', 'date', 'remarks')

@admin.register(StockDetail)
class StockDetailAdmin(admin.ModelAdmin):
    list_display = ('transaction', 'product', 'quantity')
