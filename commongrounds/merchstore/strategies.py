"""Strategy pattern for handling Product purchase flow.

The Product Detail View selects the appropriate strategy based on the user's
authentication status and delegates the entire submission flow to it.
"""

from django.shortcuts import redirect
from django.urls import reverse


PENDING_TX_SESSION_KEY = 'pending_transaction'


class BaseTransactionStrategy:
    """Base class for transaction strategies."""

    def execute(self, request, product, form):
        raise NotImplementedError


class AuthenticatedPurchaseStrategy(BaseTransactionStrategy):
    """Saves the transaction and redirects to the cart.

    Stock deduction and status updates happen in the post_save signal
    (see merchstore/signals.py).
    """

    def execute(self, request, product, form):
        transaction = form.save(commit=False)
        transaction.product = product
        transaction.buyer = request.user.profile
        transaction.save()
        return redirect(reverse('merchstore:cart'))


class GuestPurchaseStrategy(BaseTransactionStrategy):
    """Stores pending transaction data in the session and redirects to login.

    On the next page load after login the cached data is replayed via the
    authenticated strategy (see merchstore.views.complete_pending_transaction).
    """

    def execute(self, request, product, form):
        request.session[PENDING_TX_SESSION_KEY] = {
            'product_id': product.pk,
            'amount': int(form.cleaned_data.get('amount') or 1),
        }
        return redirect('{}?next={}'.format(
            reverse('login'),
            product.get_absolute_url(),
        ))
