from django.views.generic import TemplateView
from django.shortcuts import render
from django.views import View

def index(request):
    return render(request, 'core\Index.html')

###codigo de prueba
## Vista basada en clase para manejar el registro
class RegisterView(View):
    def get(self, request):
        return render(request, 'core/modals.html')
    def post(self, request):
        pass

## Vista para manejar el inicio de sesion
class LoginView(View):
    def get(self, request):
        return render(request, 'core/modals.html')
    def post(self, request):
        pass

## Vista para manejar los comentarios
class CommentView(View):
    def get(self, request):
        return render(request, 'core/modals.html')
    def post(self, request):
        pass
