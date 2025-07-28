from django.urls import path
from . import views

urlpatterns = [
    # Dashboard
    path('', views.inventory_dashboard, name='inventory_dashboard'),

    # Product URLs
    path('products/', views.product_list, name='product_list'),
    path('products/new/', views.product_create, name='product_create'),
    path('products/<int:pk>/edit/', views.product_edit, name='product_edit'),
    path('products/<int:pk>/delete/', views.product_delete, name='product_delete'),

    # Transaction URLs
    path('transactions/', views.transaction_list, name='transaction_list'),
    path('transactions/new/', views.transaction_create, name='transaction_create'),

    # API Endpoints
    path('api/dashboard/', views.api_dashboard, name='api_dashboard'),
    path('api/products/', views.api_products, name='api_products'),
    path('api/transactions/', views.api_transactions, name='api_transactions'),
]
