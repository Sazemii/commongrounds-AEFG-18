from django.views.generic.list import ListView
from django.views.generic.detail import DetailView

from .models import Commission, CommisionType


class CommissionListView(ListView):
    model = Commission
    template_name = 'commissions/commission_list.html'
    context_object_name = 'commissions'
    pass


class CommissionDetailView(DetailView):
    model = Commission
    template_name = 'commissions/commission_detail.html'
    context_object_name = 'commission'
    pass