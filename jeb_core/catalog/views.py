from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView, DetailView
from django.http import HttpResponse
from django.template.response import TemplateResponse
from django.db.models import Q
from .models import Computer , Category , Component

class CatalogView(TemplateView):
    template_name = 'catalog/catalog.html'

    FILLTER_MAPPING = {
        'category' : lambda qs , v: qs.filter(category__slug=v),
        'min_price' : lambda qs, v: qs.filter(price__gte=v),
        'max_price' : lambda qs, v: qs.filter(price__lte=v),
        'cpu' : lambda qs, v: qs.filter(cpu__icontains=v),
        'gpu' : lambda qs, v: qs.filter(gpu__icontains=v),
        'in_stock' : lambda qs, v: qs.filter(quantity_in_stock__gt = 0) if v =='true' else qs,
    }

    def get_queryset(self):
        computers = Computer.objects.filter(is_available=True)
        self.filter_params = {}

        for param , filter_func in self.FILLTER_MAPPING.items():
            value = self.request.GET.get(param)
            if value:
                computers = filter_func(computers, value)
                self.filter_params[param] = value
            else:
                self.filter_params[param] = ''
        return computers
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        computers = self.get_queryset()
        search_query = self.request.GET.get('q', '')
        if search_query:
            computers = computers.filter(
                Q(name__icontains=search_query) |
                Q(cpu__icontains=search_query) |
                Q(gpu__icontains=search_query) |
                Q(description__icontains=search_query)
            )
            self.filter_params['q'] = search_query
        
        context.update({
            'computers': computers,                    
            'categories': Category.objects.all(),      
            'filter_params': self.filter_params,       
            'total_count': computers.count(),          
            'search_query': search_query,              
        })
        
        return context

    def get(self, request, *args, **kwargs):
            context = self.get_context_data(**kwargs)
            
            if request.headers.get('HX-Request'):
                return TemplateResponse(request, 'catalog/partials/computer_list.html', context)
            return TemplateResponse(request, self.template_name, context)
    
class ComputerDetailView(DetailView):
    model = Computer
    template_name = 'catalog/detail.html'
    context_object_name = 'computer'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        computer = self.get_object()

        context['related_computers'] = Computer.objects.filter(
            category = computer.category,
            is_available = True

        ).exclude(id=computer.id)[:4]

        context['categories'] = Category.objects.all()
        return context
    
    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = super().get_context_data(**kwargs)

        if request.headers.get('Hx-Request'):
            return TemplateResponse(request, 'catalog/partials/computer_detail_content.html', context)
        
        return TemplateResponse(request, self.template_name, context)

