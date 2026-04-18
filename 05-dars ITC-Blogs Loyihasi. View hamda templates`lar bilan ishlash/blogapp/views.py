from django.shortcuts import render

# Create your views here.
from .models import Blogs

def home(request):
    blogs = Blogs.objects.all()
    context = {
        'blogs': blogs
    }
    return render(request, 'home.html', context)