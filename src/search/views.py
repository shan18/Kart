from django.views.generic import ListView

from products.models import Product


class SearchListView(ListView):
    template_name = 'search/list.html'

    # If we don['t use this function, then template gets 'q' by request.GET.q
    def get_context_data(self, *args, **kwargs):
        context = super(SearchListView, self).get_context_data(*args, **kwargs)
        context['query'] = self.request.GET.get('q')
        # SearchQuery.objects.create(query=query)
        return context

    def get_queryset(self, *args, **kwargs):   # Custom Model Manager
        request = self.request
        query = request.GET.get('q', None)  # request.GET['q'] will give an error if q does not exist
        if query is not None:
            return Product.objects.search(query)
        return Product.objects.featured()
