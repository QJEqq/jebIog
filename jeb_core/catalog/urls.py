from django.urls import path
from . import views

app_name = 'catalog'

urlpatterns = [
     path('' , views.CatalogView.as_view() , name='catalog'),
     path('computer/<slug:slug>', views.ComputerDetailView.as_view() , name='detail'),
     path('component/<slug:slug>/', views.ComponentDetailView.as_view(), name='comdetail')

]