from .views import HelloWorldView
from django.urls import path

urlpatterns = [
    path('', HelloWorldView.as_view(), name='hello_world'),
]