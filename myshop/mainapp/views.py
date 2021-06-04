from django.shortcuts import render
from django.views.generic import DetailView
from .models import Notebook, Smartphone, LatestProducts

def test_view(request):
    products = LatestProducts.objects.get_products_for_mainpage('notebook', 'smartphone')
    context = {
        'products': products
    }
    return render(request, 'base.html', context)


class ProductDetailView(DetailView):

    CT_MODEL_MODEL_CLASS = {
        'notebook': Notebook,
        'smartphone': Smartphone
    }

    def dispatch(self, request, *args, **kwargs):
        self.model = self.CT_MODEL_MODEL_CLASS[kwargs['ct_model']]
        self.queryset = self.model._base_manager.all()

        return super().dispatch(request, *args, **kwargs)

    context_object_name = 'product'
    template_name = 'product_detail.html'
    slug_url_kwarg = 'slug'
