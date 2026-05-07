from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.views.generic import DetailView, ListView, TemplateView
from django.views.generic.edit import CreateView, UpdateView

from accounts.mixins import RoleRequiredMixin
from accounts.models import Profile

from .forms import ProductCreateForm, ProductUpdateForm, TransactionForm
from .models import Product, Transaction
from .strategies import (
    PENDING_TX_SESSION_KEY,
    AuthenticatedPurchaseStrategy,
    GuestPurchaseStrategy,
)


class ProductListView(ListView):
    model = Product
    template_name = 'merchstore/items_list.html'
    context_object_name = 'all_products'

    def get_queryset(self):
        qs = Product.objects.all()
        user = self.request.user
        if user.is_authenticated and hasattr(user, 'profile'):
            qs = qs.exclude(owner=user.profile)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        user = self.request.user
        if user.is_authenticated and hasattr(user, 'profile'):
            ctx['user_products'] = Product.objects.filter(owner=user.profile)
        return ctx


class ProductDetailView(DetailView):
    model = Product
    template_name = 'merchstore/item_details.html'
    context_object_name = 'product'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        product = self.object
        user = self.request.user
        ctx['transaction_form'] = TransactionForm(max_stock=product.stock)
        ctx['is_owner'] = (
            user.is_authenticated
            and hasattr(user, 'profile')
            and product.owner_id == user.profile.pk
        )
        ctx['out_of_stock'] = product.stock == 0
        return ctx

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        product = self.object

        if (
            request.user.is_authenticated
            and hasattr(request.user, 'profile')
            and product.owner_id == request.user.profile.pk
        ):
            ctx = self.get_context_data()
            ctx['error'] = "You can't purchase your own product."
            return render(request, self.template_name, ctx)

        if product.stock == 0:
            ctx = self.get_context_data()
            ctx['error'] = 'This product is out of stock.'
            return render(request, self.template_name, ctx)

        form = TransactionForm(request.POST, max_stock=product.stock)
        if not form.is_valid():
            ctx = self.get_context_data()
            ctx['transaction_form'] = form
            return render(request, self.template_name, ctx)

        if request.user.is_authenticated:
            strategy = AuthenticatedPurchaseStrategy()
        else:
            strategy = GuestPurchaseStrategy()
        return strategy.execute(request, product, form)


class ProductCreateView(RoleRequiredMixin, CreateView):
    model = Product
    form_class = ProductCreateForm
    template_name = 'merchstore/item_form.html'
    required_role = Profile.ROLE_MARKET_SELLER

    def form_valid(self, form):
        product = form.save(commit=False)
        product.owner = self.request.user.profile
        if product.stock == 0:
            product.status = Product.STATUS_OUT_OF_STOCK
        product.save()
        self.object = product
        return redirect(product.get_absolute_url())


class ProductUpdateView(RoleRequiredMixin, UpdateView):
    model = Product
    form_class = ProductUpdateForm
    template_name = 'merchstore/item_form.html'
    required_role = Profile.ROLE_MARKET_SELLER

    def form_valid(self, form):
        product = form.save(commit=False)
        if product.stock == 0:
            product.status = Product.STATUS_OUT_OF_STOCK
        else:
            if product.status == Product.STATUS_OUT_OF_STOCK:
                product.status = Product.STATUS_AVAILABLE
        product.save()
        self.object = product
        return redirect(product.get_absolute_url())


class CartView(TemplateView):
    template_name = 'merchstore/cart.html'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        profile = self.request.user.profile
        transactions = (
            Transaction.objects
            .filter(buyer=profile)
            .select_related('product', 'product__owner')
            .order_by('product__owner__display_name', '-created_on')
        )
        groups = {}
        for tx in transactions:
            owner = tx.product.owner
            groups.setdefault(owner, []).append(tx)
        ctx['groups'] = groups
        ctx['has_transactions'] = bool(groups)
        return ctx


class TransactionListView(TemplateView):
    template_name = 'merchstore/transactions.html'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        profile = self.request.user.profile
        transactions = (
            Transaction.objects
            .filter(product__owner=profile)
            .select_related('product', 'buyer')
            .order_by('buyer__display_name', '-created_on')
        )
        groups = {}
        for tx in transactions:
            groups.setdefault(tx.buyer, []).append(tx)
        ctx['groups'] = groups
        ctx['has_transactions'] = bool(groups)
        return ctx


@login_required
def complete_pending_transaction(request):
    """Replays a session-stashed guest transaction once the user logs in."""
    pending = request.session.pop(PENDING_TX_SESSION_KEY, None)
    if not pending:
        return redirect('merchstore:items_list')
    try:
        product = Product.objects.get(pk=pending['product_id'])
    except Product.DoesNotExist:
        return redirect('merchstore:items_list')
    amount = min(int(pending.get('amount', 1)), product.stock)
    if amount < 1:
        return redirect(product.get_absolute_url())
    Transaction.objects.create(
        product=product,
        buyer=request.user.profile,
        amount=amount,
    )
    return redirect('merchstore:cart')
