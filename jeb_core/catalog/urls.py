from django.urls import path
from . import views

app_name = 'catalog'

urlpatterns = [
     path('' , views.CatalogView.as_view() , name='Catalog_Page'),
     path('computer/<slug:slug>', views.ComputerDetailView.as_view() , name='Detail_page')

]