from django.views.generic import TemplateView, DetailView
from django.template.response import TemplateResponse
from django.db.models import Q
from .models import Computer , Category , Component ,CpuList , GpuList , RamList , ComponentType
from cart.cart import Cart

class CatalogView(TemplateView):
    template_name = 'catalog/catalog.html'

    # Исправил опечатку и привел к единому стилю
    FILTER_CONFIGS = {
        'computers': {
            'category': lambda qs, v: qs.filter(category__slug=v),
            'min_price': lambda qs, v: qs.filter(price__gte=v),
            'max_price': lambda qs, v: qs.filter(price__lte=v),
            'cpu': lambda qs, v: qs.filter(cpu__id=v) if v.isdigit() else qs,
            'gpu': lambda qs, v: qs.filter(gpu__id=v) if v.isdigit() else qs,
            'ram' : lambda qs, v: qs.filter(ram__id=v) if v.isdigit() else qs,
            'in_stock': lambda qs, v: qs.filter(quantity_in_stock__gt=0) if v == 'true' else qs,
        },
        'components': {
            'category': lambda qs, v: qs.filter(category__slug=v),
            'min_price': lambda qs, v: qs.filter(price__gte=v),
            'max_price': lambda qs, v: qs.filter(price__lte=v),
            'in_stock': lambda qs, v: qs.filter(quantity_in_stock__gt=0) if v == 'true' else qs,
            'typecom' : lambda qs , v: qs.filter(component_type__slug=v),
        }
    }

    def get_queryset(self, product_type):
        if product_type == 'components':
            queryset = Component.objects.filter(is_available=True)
            filters = self.FILTER_CONFIGS['components']
        else:
            queryset = Computer.objects.select_related('cpu', 'gpu', 'ram').filter(is_available=True)
            filters = self.FILTER_CONFIGS['computers']

        self.filter_params = {}
        for param, filter_func in filters.items():
            value = self.request.GET.get(param)
            if value:
                queryset = filter_func(queryset, value)
                self.filter_params[param] = value
        
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cart'] = Cart(self.request)
        product_type = self.request.GET.get('type', 'computers')

        items = self.get_queryset(product_type)

        search_query = self.request.GET.get('q', '')
        if search_query:
            if product_type == 'components':
                items = items.filter(Q(name__icontains=search_query))
            else:
                items = items.filter(
                    Q(name__icontains=search_query) |
                    Q(cpu__name__icontains=search_query) |
                    Q(gpu__name__icontains=search_query)
                )
            self.filter_params['q'] = search_query

        context.update({
            'items': items,
            'categories': Category.objects.all(),
            'product_type': product_type,
            'filter_params': self.filter_params,
            'search_query': search_query,
            'cpus' : CpuList.objects.filter(is_available=True),
            'gpus' : GpuList.objects.filter(is_available=True),
            'rams' : RamList.objects.filter(is_available=True),
            'componentType' : ComponentType.objects.all(),
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
        context['cart'] = Cart(self.request)
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

class ComponentDetailView(DetailView):
    model = Component
    template_name = 'catalog/component_detail.html'
    context_object_name = 'component'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_context_data(self, **kwargs):
        context =  super().get_context_data(**kwargs)
        context['cart'] = Cart(self.request)
        component = self.get_object()

        context['related_components'] = Component.objects.filter(
            category = component.category,
            is_available = True
        ) .exclude(id=component.id)[:4]
        context['categories'] = Category.objects.all()
        return context

    def get(self, request , *args, **kwargs):
        self.object = self.get_object()
        context = super().get_context_data(**kwargs)

        if request.headers.get('Hx-Request') :
            return TemplateResponse(request, 'catalog/component_detail.html', context)
        return TemplateResponse(request, self.template_name, context)   

