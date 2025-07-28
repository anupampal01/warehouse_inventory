from django import forms
from .models import Product, StockTransaction, StockDetail

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'stock_quantity']

    def clean_stock_quantity(self):
        qty = self.cleaned_data.get('stock_quantity')
        if qty < 0:
            raise forms.ValidationError("Stock quantity cannot be negative.")
        return qty


class StockTransactionForm(forms.ModelForm):
    class Meta:
        model = StockTransaction
        fields = ['transaction_type', 'remarks']


class StockDetailForm(forms.ModelForm):
    class Meta:
        model = StockDetail
        fields = ['product', 'quantity']

    def clean_quantity(self):
        qty = self.cleaned_data.get('quantity')
        if qty <= 0:
            raise forms.ValidationError("Quantity must be greater than 0.")
        return qty
