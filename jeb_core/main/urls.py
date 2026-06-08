from django.urls import path
from . import views
from django.views.generic import TemplateView
app_name = 'main'

urlpatterns = [
     path('' , views.home , name='Home_Page'  ),
     path('terms/', 
         TemplateView.as_view(template_name='main/terms.html'), 
         name='terms'),
         
    path('privacy/', 
         TemplateView.as_view(template_name='main/privacy.html'), 
         name='privacy'),
         
    path('refund/', 
         TemplateView.as_view(template_name='main/refuned.html'), 
         name='refund'),
         
    path('agree-data/', 
         TemplateView.as_view(template_name='main/agree_data.html'), 
         name='agree_data'),
     

]
