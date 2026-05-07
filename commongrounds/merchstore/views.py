from django.shortcuts import redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Product, Transaction
from .forms import ProductForm, TransactionForm
from accounts.mixins import RoleRequiredMixin


class ProductListView(ListView):
    model = Product
    template_name = 'merchstore/product_list.html'
    context_object_name = 'products'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            user_profile = self.request.user.profile
            context['user_products'] = Product.objects.filter(
                owner=user_profile).order_by('name')
            context['all_products'] = Product.objects.exclude(
                owner=user_profile).order_by('name')
        else:
            context['all_products'] = Product.objects.all()
        return context


class ProductDetailView(DetailView):
    model = Product
    template_name = 'merchstore/product_detail.html'
    context_object_name = 'product'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = TransactionForm()
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if not request.user.is_authenticated:
            return redirect('login')

        if self.object.owner == request.user.profile:
            return redirect('merchstore:product-detail', pk=self.object.pk)

        form = TransactionForm(request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.product = self.object
            transaction.buyer = request.user.profile
            transaction.status = 'On cart'

            product = transaction.product
            if product.stock >= transaction.amount:
                product.stock -= transaction.amount
                if product.stock == 0:
                    product.status = 'Out of stock'
                product.save()
                transaction.save()
                return redirect('merchstore:cart')
            return redirect('merchstore:product-detail', pk=product.pk)
        return self.render_to_response(self.get_context_data(form=form))


class ProductCreateView(RoleRequiredMixin, LoginRequiredMixin, CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'merchstore/product_form.html'
    required_role = 'Market Seller'

    def form_valid(self, form):
        form.instance.owner = self.request.user.profile
        return super().form_valid(form)


class ProductUpdateView(RoleRequiredMixin, LoginRequiredMixin, UpdateView):
    model = Product
    form_class = ProductForm
    template_name = 'merchstore/product_form.html'
    required_role = 'Market Seller'

    def form_valid(self, form):
        if form.instance.stock == 0:
            form.instance.status = 'Out of stock'
        else:
            form.instance.status = 'Available'
        return super().form_valid(form)


class CartView(LoginRequiredMixin, ListView):
    model = Transaction
    template_name = 'merchstore/cart.html'
    context_object_name = 'transactions'

    def get_queryset(self):
        return Transaction.objects.filter(
            buyer=self.request.user.profile, 
            status='On cart'
        ).order_by('product__owner')

    def post(self, request, *args, **kwargs):
        transactions = Transaction.objects.filter(
            buyer=self.request.user.profile, status='On cart')
        for transaction in transactions:
            transaction.status = 'To Pay'
            transaction.save()
        return redirect('merchstore:transactions_list')


from django.db.models import Q


class TransactionListView(LoginRequiredMixin, ListView):
    model = Transaction
    template_name = 'merchstore/transactions_list.html'
    context_object_name = 'transactions'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_profile = self.request.user.profile
        
        context['purchases'] = Transaction.objects.filter(
            buyer=user_profile
        ).exclude(status='On cart').order_by('product__owner', '-created_on')
        
        context['sales'] = Transaction.objects.filter(
            product__owner=user_profile
        ).order_by('buyer', '-created_on')
        
        return context

    def get_queryset(self):
        return Transaction.objects.filter(
            Q(product__owner=self.request.user.profile) |
            Q(buyer=self.request.user.profile)
        ).exclude(buyer=self.request.user.profile, status='On cart').order_by('-created_on')
