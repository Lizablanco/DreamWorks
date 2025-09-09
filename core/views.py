from django.conf import settings
from django.http import HttpResponse, FileResponse, Http404
import os
from django.http import FileResponse
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.views.generic import TemplateView
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import View
from core.models import *
from .forms  import CuriosidadForm, GeneroForm, MovieForm, DescargaForm, LoginForm, RegistroForm
from django.db.models import Q
from django.core.paginator import Paginator
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages

# Create your views here.


# vista para manejar cuando el archivo no esta disponible
def archivo_no_disponible(request, slug):
    pelicula = get_object_or_404(Movie, slug=slug)
    return render(request, 'partials/archivo_no_disponible.html', {'pelicula': pelicula})


# vista para guardar la opinion general
@login_required
def guardar_opinion_general(request):
    if request.method == 'POST':
        descripcion = request.POST.get('descripcion', '').strip()
        ya_existe = OpinionGeneral.objects.filter(user=request.user).exists()

        if descripcion and not ya_existe:
            OpinionGeneral.objects.create(
                user=request.user,
                descripcion=descripcion
            )
            messages.success(request, '¡Gracias por tu opinión! 📝')
        elif ya_existe:
            messages.warning(request, 'Ya has enviado una opinión anteriormente.')
        else:
            messages.error(request, 'La descripción no puede estar vacía.')

    return redirect('index')


###codigo de prueba
## Vista basada en clase para manejar el registro
class RegistroView(View):
    template_name = 'core/index.html'

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('index')
        opiniones_generales = OpinionGeneral.objects.order_by('-fecha_registro')[:5]
        return render(request, self.template_name, {
            'registro_form': RegistroForm(),
            'login_form': LoginForm(), 
            'opiniones_generales': opiniones_generales
        })

    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('index')
        form = RegistroForm(request.POST)
        opiniones_generales = OpinionGeneral.objects.order_by('-fecha_registro')[:5]
        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password1 = form.cleaned_data['password1']
            password2 = form.cleaned_data['password2']

            if password1 != password2:
                return render(request, self.template_name, {
                    'registro_form': form,
                    'login_form': LoginForm(),
                    'opiniones_generales': opiniones_generales,
                    'error_message': 'Las contraseñas no coinciden'
                })

            if User.objects.filter(username=username).exists():
                return render(request, self.template_name, {
                    'registro_form': form,
                    'login_form': LoginForm(),
                    'error_message': 'Ese nombre de usuario ya está en uso',
                    'opiniones_generales': opiniones_generales
                })

            User.objects.create_user(username=username, email=email, password=password1)
            messages.success(request, 'Registro exitoso. Ahora puedes iniciar sesión.')
            return redirect('login')

        return render(request, self.template_name, {
            'registro_form': form,
            'login_form': LoginForm(),
            'opiniones_generales': opiniones_generales,
        })

# vista de logout
class UserLogoutView(View):
    def get(self, request, *args, **kwargs):
        logout(request)
        return redirect('login')


## Vista para manejar el inicio de sesion
class LoginView(View):
    template_name = 'core/index.html'
    
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('index')

        opiniones_generales = OpinionGeneral.objects.order_by('-fecha_registro')[:5]

        return render(request, self.template_name, {
            'login_form': LoginForm(),
            'registro_form': RegistroForm(),
            'opiniones_generales': opiniones_generales,
        })
    
    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('index')

        form = LoginForm(request.POST)
        opiniones_generales = OpinionGeneral.objects.order_by('-fecha_registro')[:5]

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                return redirect('index')
            else:
                messages.error(request, 'Nombre de usuario o contraseña incorrectos')
        else:
            messages.error(request, 'Por favor corrige los errores del formulario')

        return render(request, self.template_name, {
            'login_form': form,
            'registro_form': RegistroForm(),
            'opiniones_generales': opiniones_generales
        })


## Vista para manejar los comentarios
class CommentView(LoginRequiredMixin, View):
    def post(self, request, slug):
        pelicula = get_object_or_404(Movie, slug=slug)
        descripcion = request.POST.get('descripcion', '').strip()

        ya_opino = Opinion.objects.filter(user=request.user, movie=pelicula).exists()

        if descripcion and not ya_opino:
            Opinion.objects.create(
                user=request.user,
                movie=pelicula,
                descripcion=descripcion
            )

            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'status': 'ok', 'message': 'Opinión guardada ✨'})
        
        return redirect('pelicula_info', slug=pelicula.slug)


# Vistas para CRUD de Curiosidades
class CuriosidadListView(View):
    template_name = 'core/curiosidad_list.html'

    def get(self, request):
        curiosidades = Curiosidad.objects.all().order_by('-id')
        return render(request, self.template_name, {'curiosidades': curiosidades})

# Vista para crear una nueva curiosidad
class CuriosidadCreateView(View):
    template_name = 'core/curiosidad_form.html'

    def get(self, request):
        form = CuriosidadForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = CuriosidadForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('curiosidad_list')
        return render(request, self.template_name, {'form': form})

# Vista para actualizar una curiosidad existente
class CuriosidadUpdateView(View):
    template_name = 'core/curiosidad_form.html'

    def get(self, request, pk):
        instancia = get_object_or_404(Curiosidad, pk=pk)
        form = CuriosidadForm(instance=instancia)
        return render(request, self.template_name, {'form': form, 'object': instancia})

    def post(self, request, pk):
        instancia = get_object_or_404(Curiosidad, pk=pk)
        form = CuriosidadForm(request.POST, instance=instancia)
        if form.is_valid():
            form.save()
            return redirect('curiosidad_list')
        return render(request, self.template_name, {'form': form, 'object': instancia})

# Vista para eliminar una curiosidad
class CuriosidadDeleteView(LoginRequiredMixin, View):
    template_name = 'core/curiosidad_confirm_delete.html'

    def get(self, request, pk):
        instancia = get_object_or_404(Curiosidad, pk=pk)
        return render(request, self.template_name, {'object': instancia})

    def post(self, request, pk):
        instancia = get_object_or_404(Curiosidad, pk=pk)
        instancia.delete()
        return redirect('curiosidad_list')


# Vistas para CRUD de Generos
class GeneroListView(LoginRequiredMixin, View):
    template_name = 'partials/genero_list.html'
    paginate_by=2

    def get(self, request):
        generos = Genero.objects.all().order_by('nombre')
        
        query = request.GET.get('q')
        
        if query:
            generos = generos.filter(
                Q(nombre__icontains=query) |
                Q(descripcion__icontains=query)
            ).distinct()
            
        paginator= Paginator(generos, self.paginate_by)
        page_number = request.GET.get('page')
        page_obj= paginator.get_page(page_number)
        
        context = {
            'page_obj': page_obj,
            'generos': page_obj.object_list,
            'query': query
        }
            
        return render(request, self.template_name, context)

# Vista para crear un nuevo genero
class GeneroCreateView(LoginRequiredMixin, View):
    template_name = 'partials/genero_form.html'

    def get(self, request):
        form = GeneroForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = GeneroForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('genero_list')
        return render(request, self.template_name, {'form': form})

# Vista para actualizar un genero existente
class GeneroUpdateView(LoginRequiredMixin, View):
    template_name = 'partials/genero_form.html'

    def get(self, request, pk):
        instancia = get_object_or_404(Genero, pk=pk)
        form = GeneroForm(instance=instancia)
        return render(request, self.template_name, {
            'form': form,
            'object': instancia
        })

    def post(self, request, pk):
        instancia = get_object_or_404(Genero, pk=pk)
        form = GeneroForm(request.POST, instance=instancia)
        if form.is_valid():
            form.save()
            return redirect('genero_list')
        return render(request, self.template_name, {
            'form': form,
            'object': instancia
        })

# Vista para eliminar un genero
class GeneroDeleteView(LoginRequiredMixin, View):
    template_name = 'partials/genero_confirm_delete.html'

    def get(self, request, pk):
        instancia = get_object_or_404(Genero, pk=pk)
        return render(request, self.template_name, {'object': instancia})

    def post(self, request, pk):
        instancia = get_object_or_404(Genero, pk=pk)
        instancia.delete()
        return redirect('genero_list')
    

# Vistas para CRUD de Peliculas
class MovieListView(LoginRequiredMixin, View):
    template_name = 'partials/movie_list.html'

    def get(self, request):
        peliculas = Movie.objects.all().order_by('-fecha_lanzamiento')
        return render(request, self.template_name, {'peliculas': peliculas})

# Vista para crear una nueva pelicula
class MovieCreateView(LoginRequiredMixin, View):
    template_name = 'partials/movie_form.html'

    def get(self, request):
        form = MovieForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = MovieForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('movie_list')
        return render(request, self.template_name, {'form': form})

# Vista para actualizar una pelicula existente
class MovieUpdateView(LoginRequiredMixin, View):
    template_name = 'partials/movie_form.html'

    def get(self, request, pk):
        instancia = get_object_or_404(Movie, pk=pk)
        form = MovieForm(instance=instancia)
        return render(request, self.template_name, {
            'form': form,
            'object': instancia
        })

    def post(self, request, pk):
        instancia = get_object_or_404(Movie, pk=pk)
        form = MovieForm(request.POST, request.FILES, instance=instancia)
        if form.is_valid():
            form.save()
            return redirect('movie_list')
        return render(request, self.template_name, {
            'form': form,
            'object': instancia
        })

# Vista para eliminar una pelicula
class MovieDeleteView(LoginRequiredMixin, View):
    template_name = 'partials\movie_confirm_delet.html'

    def get(self, request, pk):
        instancia = get_object_or_404(Movie, pk=pk)
        return render(request, self.template_name, {'object': instancia})

    def post(self, request, pk):
        instancia = get_object_or_404(Movie, pk=pk)
        instancia.delete()
        return redirect('movie_list')

# Vista para mostrar la informacion y detalles de una pelicula
class PeliculaInfoView(View):
    def get(self, request, slug):
        pelicula = get_object_or_404(Movie, slug=slug)
        opiniones = Opinion.objects.filter(movie=pelicula).order_by('-fecha_registro')
        ya_opino = False
        if request.user.is_authenticated:
            ya_opino = Opinion.objects.filter(user=request.user, movie=pelicula).exists()

        return render(request, 'core/peliculas_info.html', {
            'pelicula': pelicula,
            'opiniones': opiniones,
            'ya_opino': ya_opino
        })


# Vista para la pagina principal que muestra las peliculas mas recientes
class IndexView(View):
    template_name = 'core/index.html'

    def get(self, request):
        request.session.pop('abrir_login', None)  
        opiniones_generales = OpinionGeneral.objects.order_by('-fecha_registro')[:5]
        peliculas = Movie.objects.all().order_by('-fecha_lanzamiento')
        return render(request, self.template_name, {
            'peliculas': peliculas,
            'opiniones_generales': opiniones_generales,
            'registro_form': RegistroForm(),
            'login_form': LoginForm()
        })



# Vistas para manejar las descargas de peliculas por usuarios
@method_decorator(login_required(login_url='login'), name='dispatch')
class DescargaListView(LoginRequiredMixin, View):
    template_name = 'partials/descarga_list.html'

    def pelicula_descargar(request, slug):
        if not request.user.is_authenticated:
            messages.error(request, 'Debes iniciar sesión para descargar esta película 🪄')
            return redirect('login')

        pelicula = get_object_or_404(Movie, slug=slug)

        if not pelicula.archivo or not os.path.isfile(pelicula.archivo.path):
            return redirect(pelicula.get_absolute_url())

        return FileResponse(pelicula.archivo.open(), as_attachment=True, filename=os.path.basename(pelicula.archivo.name))

# Vista para manejar la descarga real del archivo
def descargar_pelicula (request, slug):
    if not request.user.is_authenticated:
        messages.error(request, 'Debes iniciar sesión para descargar esta película 🌟')
        request.session['abrir_login'] = True
        return redirect('index')

    pelicula = get_object_or_404(Movie, slug=slug)

    if not pelicula.archivo or not os.path.isfile(pelicula.archivo.path):
        messages.error(request, 'El archivo de esta película no está disponible 🛡️')
        return redirect(pelicula.get_absolute_url())

    return FileResponse(
        pelicula.archivo.open(),
        as_attachment=True,
        filename=os.path.basename(pelicula.archivo.name)
    )



# para registrar una nueva descarga
class DescargaCreateView(LoginRequiredMixin,View):
    template_name = 'partials/descarga_form.html'

    def get(self, request):
        # inyectamos el user para que el form filtre las películas ya descargadas
        form = DescargaForm(user=request.user)
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = DescargaForm(request.POST, user=request.user)
        if form.is_valid():
            descarga = form.save(commit=False)
            descarga.user = request.user
            descarga.save()
            return redirect('descarga_list')
        return render(request, self.template_name, {'form': form})

# para eliminar una descarga (solo el dueño o staff)
class DescargaDeleteView(LoginRequiredMixin, View):
    template_name = 'partials/descarga_confirm_delete.html'

    def get(self, request, pk):
        descarga = get_object_or_404(DescargaUsuarioPelicula, pk=pk)
        # Solo el dueño o staff puede verla
        if not (request.user.is_staff or descarga.user == request.user):
            return redirect('descarga_list')
        return render(request, self.template_name, {'object': descarga})

    def post(self, request, pk):
        descarga = get_object_or_404(DescargaUsuarioPelicula, pk=pk)
        if request.user.is_staff or descarga.user == request.user:
            descarga.delete()
        return redirect('descarga_list')

# vista para manejar la descarga real del archivo
@method_decorator(login_required, name='dispatch')
class PeliculaDescargaView(View):
    def get(self, request, slug):
        pelicula = get_object_or_404(Movie, slug=slug)

        # Verificar si el archivo existe físicamente
        if not pelicula.archivo or not os.path.isfile(pelicula.archivo.path):
            messages.warning(request, "Esta película no tiene archivo disponible para descarga.")
            return redirect('archivo_no_disponible', slug=pelicula.slug)

        # Registrar la descarga solo si no existe
        if not DescargaUsuarioPelicula.objects.filter(user=request.user, movie=pelicula).exists():
            DescargaUsuarioPelicula.objects.create(user=request.user, movie=pelicula)

        # Entregar el archivo como descarga directa
        return FileResponse(
            pelicula.archivo.open(),
            as_attachment=True,
            filename=os.path.basename(pelicula.archivo.name)
        )

