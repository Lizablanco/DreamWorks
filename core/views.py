from django.views.generic import TemplateView
from django.shortcuts import render
from django.views import View

def index(request):
    return render(request, 'core\Index.html')

###codigo de prueba
