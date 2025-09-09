from .forms import RegistroForm, LoginForm

def modals_forms(request):
    print(">>> Context processor ejecutado")
    return {
        'registro_form': RegistroForm(),
        'login_form': LoginForm()
    }
