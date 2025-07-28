from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.db.models import Sum, Q
from django.contrib import messages
from .models import Product, StockTransaction, StockDetail
from .forms import ProductForm, StockTransactionForm, StockDetailForm

# ------------------------
# INVENTORY DASHBOARD (WEB + API)
# ------------------------
def inventory_dashboard(request):
    products = Product.objects.all()

    # Calculate stock: IN - OUT
    stock_movements = StockDetail.objects.values('product').annotate(
        in_qty=Sum('quantity', filter=Q(transaction__transaction_type='IN')),
        out_qty=Sum('quantity', filter=Q(transaction__transaction_type='OUT'))
    )

    stock_dict = {}
    for move in stock_movements:
        stock_dict[move['product']] = (move['in_qty'] or 0) - (move['out_qty'] or 0)

    for product in products:
        product.current_stock = stock_dict.get(product.id, 0)

    return render(request, 'inventory/inventory.html', {'products': products})


def api_dashboard(request):
    """API: Returns inventory stock summary"""
    products = Product.objects.all()
    data = []
    for product in products:
        total_in = StockDetail.objects.filter(
            product=product, transaction__transaction_type='IN'
        ).aggregate(Sum('quantity'))['quantity__sum'] or 0
        total_out = StockDetail.objects.filter(
            product=product, transaction__transaction_type='OUT'
        ).aggregate(Sum('quantity'))['quantity__sum'] or 0
        current_stock = total_in - total_out
        data.append({
            "name": product.name,
            "sku": product.sku,
            "current_stock": current_stock
        })
    return JsonResponse({"inventory": data})


# ------------------------
# PRODUCT CRUD
# ------------------------
def product_list(request):
    products = Product.objects.all()
    return render(request, 'inventory/product_list.html', {'products': products})


def api_products(request):
    """API: List all products with stock"""
    products = Product.objects.all().values("id", "name", "sku", "price")
    return JsonResponse({"products": list(products)})


def product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Product added successfully!")
            return redirect('product_list')
    else:
        form = ProductForm()
    return render(request, 'inventory/product_form.html', {'form': form})


def product_edit(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, "Product updated successfully!")
            return redirect('product_list')
    else:
        form = ProductForm(instance=product)
    return render(request, 'inventory/product_form.html', {'form': form})


def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    product.delete()
    messages.success(request, "Product deleted successfully!")
    return redirect('product_list')


# ------------------------
# STOCK TRANSACTIONS
# ------------------------
def transaction_list(request):
    transactions = StockTransaction.objects.all().order_by('-date')
    return render(request, 'inventory/transaction_list.html', {'transactions': transactions})


def api_transactions(request):
    """API: List all transactions"""
    transactions = StockTransaction.objects.all().values("transaction_type", "date", "remarks")
    return JsonResponse({"transactions": list(transactions)})


def transaction_create(request):
    if request.method == 'POST':
        t_form = StockTransactionForm(request.POST)
        d_form = StockDetailForm(request.POST)

        if t_form.is_valid() and d_form.is_valid():
            transaction = t_form.save()
            detail = d_form.save(commit=False)
            detail.transaction = transaction

            # Validate positive quantity
            if detail.quantity <= 0:
                d_form.add_error('quantity', 'Quantity must be greater than 0!')
                return render(request, 'inventory/transaction_form.html', {'t_form': t_form, 'd_form': d_form})

            # Validate stock for OUT
            if transaction.transaction_type == 'OUT':
                product = detail.product
                total_in = StockDetail.objects.filter(
                    product=product, transaction__transaction_type='IN'
                ).aggregate(Sum('quantity'))['quantity__sum'] or 0
                total_out = StockDetail.objects.filter(
                    product=product, transaction__transaction_type='OUT'
                ).aggregate(Sum('quantity'))['quantity__sum'] or 0
                current_stock = total_in - total_out

                if detail.quantity > current_stock:
                    d_form.add_error('quantity', 'Not enough stock available!')
                    return render(request, 'inventory/transaction_form.html', {'t_form': t_form, 'd_form': d_form})

            detail.save()
            messages.success(request, "Transaction recorded successfully!")
            return redirect('transaction_list')
    else:
        t_form = StockTransactionForm()
        d_form = StockDetailForm()

    return render(request, 'inventory/transaction_form.html', {'t_form': t_form, 'd_form': d_form})
