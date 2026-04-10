from .views import home, blog
from django.urls import path   

urlpatterns = [
    path('', home, name='home'),
    path('yangiliklar-saxifasi/', blog, name='blogs'),    
    ]