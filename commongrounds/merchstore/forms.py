from django import forms

from .models import Product, Transaction


class ProductCreateForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'name', 'product_type', 'product_image',
            'description', 'price', 'stock', 'status',
        ]


class ProductUpdateForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'name', 'product_type', 'product_image',
            'description', 'price', 'stock', 'status',
        ]


class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['amount']
        widgets = {
            'amount': forms.NumberInput(attrs={'min': 1}),
        }

    def __init__(self, *args, max_stock=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.max_stock = max_stock
        if max_stock is not None:
            self.fields['amount'].widget.attrs['max'] = max_stock

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount is None or amount < 1:
            raise forms.ValidationError('Amount must be at least 1.')
        if self.max_stock is not None and amount > self.max_stock:
            raise forms.ValidationError(
                'Only {} in stock.'.format(self.max_stock)
            )
        return amount
