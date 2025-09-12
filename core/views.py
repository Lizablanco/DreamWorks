from django.conf import settings
from django.http import HttpResponse, FileResponse, Http404
import os
from django.contrib import messages
from django.core.exceptions import ValidationError, PermissionDenied
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
from django.db import IntegrityError, DatabaseError


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

#views de las opniones
class OpinionesDelReinoView(View):
    template_name = 'partials/opiniones_completas.html'

    def get(self, request):
        todas = OpinionGeneral.objects.order_by('-fecha_registro')
        paginador = Paginator(todas, 10)
        pagina = request.GET.get('page')
        opiniones = paginador.get_page(pagina)

        return render(request, self.template_name, {
            'opiniones_generales': opiniones
        })


###codigo de prueba
## Vista basada en clase para manejar el registro
GENERAL_OPINIONES_A_MOSTRAR = 3

class RegistroView(View):
    template_name = 'core/index.html'

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('index')

        qs = OpinionGeneral.objects.order_by('-fecha_registro')
        opiniones = qs[:GENERAL_OPINIONES_A_MOSTRAR]
        mostrar_boton = qs.count() > GENERAL_OPINIONES_A_MOSTRAR

        return render(request, self.template_name, {
            'registro_form': RegistroForm(),
            'login_form': LoginForm(),
            'opiniones_generales': opiniones,
            'mostrar_boton_ver_mas': mostrar_boton,
        })

    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('index')

        # Obtener datos directamente del request
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password1 = request.POST.get('password1', '')
        password2 = request.POST.get('password2', '')

        qs = OpinionGeneral.objects.order_by('-fecha_registro')
        opiniones = qs[:GENERAL_OPINIONES_A_MOSTRAR]
        mostrar_boton = qs.count() > GENERAL_OPINIONES_A_MOSTRAR

        # Validaciones manuales SIMPLES
        errors = []
        
        if not all([username, email, password1, password2]):
            messages.error(request, '❌ Todos los campos son obligatorios')
            return self.render_with_context(request, opiniones, mostrar_boton)
        
        if password1 != password2:
            messages.error(request, '🔒 Las contraseñas no coinciden')
            return self.render_with_context(request, opiniones, mostrar_boton)
        
        if User.objects.filter(username=username).exists():
            messages.error(request, '👤 Este nombre de usuario ya está en uso')
            return self.render_with_context(request, opiniones, mostrar_boton)
        
        if User.objects.filter(email=email).exists():
            messages.error(request, '📧 Este correo electrónico ya está registrado')
            return self.render_with_context(request, opiniones, mostrar_boton)

        # Crear usuario
        try:
            User.objects.create_user(username=username, email=email, password=password1)
            messages.success(request, '✨ ¡Registro exitoso! Ahora puedes iniciar sesión.')
            return redirect('login')
        except Exception as e:
            messages.error(request, '❌ Error al crear el usuario. Inténtalo de nuevo.')
            return self.render_with_context(request, opiniones, mostrar_boton)

    def render_with_context(self, request, opiniones, mostrar_boton):
        """Método helper para renderizar con el contexto"""
        return render(request, self.template_name, {
            'registro_form': RegistroForm(),
            'login_form': LoginForm(),
            'opiniones_generales': opiniones,
            'mostrar_boton_ver_mas': mostrar_boton,
        })

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

        qs = OpinionGeneral.objects.order_by('-fecha_registro')
        opiniones = qs[:GENERAL_OPINIONES_A_MOSTRAR]
        mostrar_boton = qs.count() > GENERAL_OPINIONES_A_MOSTRAR

        return render(request, self.template_name, {
            'login_form':   LoginForm(),
            'registro_form': RegistroForm(),
            'opiniones_generales':     opiniones,
            'mostrar_boton_ver_mas':   mostrar_boton,
        })

    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('index')

        form = LoginForm(request.POST)
        qs = OpinionGeneral.objects.order_by('-fecha_registro')
        opiniones = qs[:GENERAL_OPINIONES_A_MOSTRAR]
        mostrar_boton = qs.count() > GENERAL_OPINIONES_A_MOSTRAR

        if form.is_valid():
            u = form.cleaned_data['username']
            p = form.cleaned_data['password']
            user = authenticate(request, username=u, password=p)
            if user:
                login(request, user)
                messages.success(request, '🎉 ¡Bienvenido de nuevo!')
                return redirect('index')
            messages.error(request, '❌ Nombre de usuario o contraseña incorrectos')
        else:
            messages.error(request, '❌ Por favor corrige los errores del formulario')

        return render(request, self.template_name, {
            'login_form':   LoginForm(),  # Formulario limpio
            'registro_form': RegistroForm(),
            'opiniones_generales':     opiniones,
            'mostrar_boton_ver_mas':   mostrar_boton,
        })


## Vista para manejar los comentarios
class CommentView(LoginRequiredMixin, View):
    def post(self, request, slug):
        try:
            pelicula = get_object_or_404(Movie, slug=slug)
            descripcion = request.POST.get('descripcion', '').strip()

            if not descripcion:
                messages.error(request, '❌ La opinión no puede estar vacía.')
                return redirect('pelicula_info', slug=pelicula.slug)

            ya_opino = Opinion.objects.filter(user=request.user, movie=pelicula).exists()
            
            if ya_opino:
                messages.info(request, 'ℹ️ Ya has dejado tu opinión sobre esta película.')
                return redirect('pelicula_info', slug=pelicula.slug)

            try:
                Opinion.objects.create(user=request.user, movie=pelicula, descripcion=descripcion)
                messages.success(request, '✅ Opinión guardada correctamente ✨')
            except IntegrityError:
                messages.error(request, '❌ Error al guardar tu opinión')
            except DatabaseError:
                messages.error(request, '❌ Error de base de datos. Intenta más tarde.')
                
            return redirect('pelicula_info', slug=pelicula.slug)
            
        except Exception as e:
            messages.error(request, '❌ Error inesperado')
            return redirect('index')

# vistas de errores
class StaffRequiredMixin:
    error_messages = {
        'delete': '⚔️ Solo los archimagos del reino pueden eliminar este elemento.',
        'create': '🔮 Solo los escribas reales pueden crear nuevos elementos.',
        'edit': '📜 Solo los cronistas del reino pueden modificar este elemento.',
        'view': ' Solo los visionarios del staff pueden ver este elemento.',
        'default': '❌ Acceso restringido al personal del reino.'
    }
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_staff:
            action = self.get_action_type(request)
            message = self.error_messages.get(action, self.error_messages['default'])
            messages.error(request, message)
            return redirect('index') 
        return super().dispatch(request, *args, **kwargs)
    
    def get_action_type(self, request):
        path = request.path.lower()
        
        if 'borrar' in path or 'delete' in path:
            return 'delete'
        elif 'editar' in path or 'edit' in path:
            return 'edit'
        elif 'nuevo' in path or 'crear' in path or 'create' in path or 'add' in path:
            return 'create'
        elif 'ver' in path or 'view' in path or 'detalle' in path:
            return 'view'
        else:
            return 'default'

# Vistas para CRUD de Curiosidades
class CuriosidadListView(View):
    template_name = 'partials/curiosidad_list.html'

    def get(self, request):
        curiosidades = Curiosidad.objects.all().order_by('-id')
        return render(request, self.template_name, {'curiosidades': curiosidades})

# Vista para crear una nueva curiosidad
class CuriosidadCreateView(StaffRequiredMixin, LoginRequiredMixin, View):
    template_name = 'partials/curiosidad_form.html'

    def get(self, request):
        form = CuriosidadForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = CuriosidadForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, '✅ Curiosidad creada exitosamente')
            return redirect('curiosidad_list')
        messages.error(request, '❌ Error al crear la curiosidad')
        return render(request, self.template_name, {'form': CuriosidadForm()})

# Vista para actualizar una curiosidad existente
class CuriosidadUpdateView(StaffRequiredMixin, LoginRequiredMixin, View):
    template_name = 'partials/curiosidad_form.html'

    def get(self, request, pk):
        instancia = get_object_or_404(Curiosidad, pk=pk)
        form = CuriosidadForm(instance=instancia)
        return render(request, self.template_name, {'form': form, 'object': instancia})

    def post(self, request, pk):
        instancia = get_object_or_404(Curiosidad, pk=pk)
        form = CuriosidadForm(request.POST, instance=instancia)
        if form.is_valid():
            form.save()
            messages.success(request, '✅ Curiosidad actualizada exitosamente')
            return redirect('curiosidad_list')
        messages.error(request, '❌ Error al actualizar la curiosidad')
        return render(request, self.template_name, {'form': form, 'object': instancia})

# Vista para eliminar una curiosidad
class CuriosidadDeleteView(StaffRequiredMixin, LoginRequiredMixin, View):
    template_name = 'partials/curiosidad_confirm_delete.html'

    def get(self, request, pk):
        instancia = get_object_or_404(Curiosidad, pk=pk)
        return render(request, self.template_name, {'object': instancia})

    def post(self, request, pk):
        instancia = get_object_or_404(Curiosidad, pk=pk)
        instancia.delete()
        messages.success(request, '✅ Curiosidad eliminada exitosamente')
        return redirect('curiosidad_list')


# Vistas para CRUD de Generos
class GeneroListView(LoginRequiredMixin, View):
    template_name = 'partials/genero_list.html'
    paginate_by = 2

    def get(self, request):
        generos = Genero.objects.all().order_by('nombre')
        
        query = request.GET.get('q')
        
        if query:
            generos = generos.filter(
                Q(nombre__icontains=query) |
                Q(descripcion__icontains=query)
            ).distinct()
            
        paginator = Paginator(generos, self.paginate_by)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        context = {
            'page_obj': page_obj,
            'generos': page_obj.object_list,
            'query': query
        }
            
        return render(request, self.template_name, context)

# Vista para crear un nuevo genero
class GeneroCreateView(StaffRequiredMixin, LoginRequiredMixin, View):
    template_name = 'partials/genero_form.html'

    def get(self, request):
        form = GeneroForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = GeneroForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, '✅ Género creado exitosamente')
            return redirect('genero_list')
        messages.error(request, '❌ Error al crear el género')
        return render(request, self.template_name, {'form': GeneroForm()})

# Vista para actualizar un genero existente
class GeneroUpdateView(StaffRequiredMixin, LoginRequiredMixin, View):
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
            messages.success(request, '✅ Género actualizado exitosamente')
            return redirect('genero_list')
        messages.error(request, '❌ Error al actualizar el género')
        return render(request, self.template_name, {
            'form': form,
            'object': instancia
        })

# Vista para eliminar un genero
class GeneroDeleteView(StaffRequiredMixin, LoginRequiredMixin, View):
    template_name = 'partials/genero_confirm_delete.html'

    def get(self, request, pk):
        instancia = get_object_or_404(Genero, pk=pk)
        return render(request, self.template_name, {'object': instancia})

    def post(self, request, pk):
        instancia = get_object_or_404(Genero, pk=pk)
        instancia.delete()
        messages.success(request, '✅ Género eliminado exitosamente')
        return redirect('genero_list')
    

# Vistas para CRUD de Peliculas
class MovieListView(LoginRequiredMixin, View):
    template_name = 'partials/movie_list.html'

    def get(self, request):
        peliculas = Movie.objects.all().order_by('-fecha_lanzamiento')
        return render(request, self.template_name, {'peliculas': peliculas})



# vista para eliminar
class MovieDeleteView(StaffRequiredMixin, LoginRequiredMixin, View):
    template_name = 'partials/movie_confirm_delete.html'

    def get(self, request, pk):
        instancia = get_object_or_404(Movie, pk=pk)
        return render(request, self.template_name, {'object': instancia})

    def post(self, request, pk):
        instancia = get_object_or_404(Movie, pk=pk)
        instancia.delete()
        messages.success(request, '✨ La película ha sido enviada al olvido mágico.')
        return redirect('movie_list')

#vista para crear
class MovieCreateView(StaffRequiredMixin, LoginRequiredMixin, View):
    template_name = 'partials/movie_form.html'

    def get(self, request):
        form = MovieForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = MovieForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, '🎬 ¡Nueva película añadida al reino!')
            return redirect('movie_list')
        messages.error(request, '❌ Error al crear la película')
        return render(request, self.template_name, {'form': MovieForm()})

#vista para actualizar
class MovieUpdateView(StaffRequiredMixin, LoginRequiredMixin, View):
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
            messages.success(request, '📝 Película actualizada con éxito.')
            return redirect('movie_list')
        messages.error(request, '❌ Error al actualizar la película')
        return render(request, self.template_name, {
            'form': form,
            'object': instancia
        })

# Vista para mostrar la informacion y detalles de una pelicula
class PeliculaInfoView(View):
    def get(self, request, slug):
        pelicula = get_object_or_404(Movie, slug=slug)

        opiniones_qs = Opinion.objects.filter(movie=pelicula).order_by('-fecha_registro')
        paginador = Paginator(opiniones_qs, 5)
        pagina = request.GET.get('page')
        opiniones = paginador.get_page(pagina)

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

        todas_opiniones = OpinionGeneral.objects.order_by('-fecha_registro')
        opiniones_visibles = todas_opiniones[:3]
        mostrar_boton = todas_opiniones.count() > 3

        peliculas = Movie.objects.all().order_by('-fecha_lanzamiento')

        return render(request, self.template_name, {
            'peliculas': peliculas,
            'opiniones_generales': opiniones_visibles,
            'mostrar_boton_ver_mas': mostrar_boton,
            'registro_form': RegistroForm(),
            'login_form': LoginForm()
        })


# Vistas para manejar las descargas de peliculas por usuarios
class DescargaPeliculaView(LoginRequiredMixin, View):
    login_url = 'login'

    def get(self, request, slug):
        try:
            pelicula = get_object_or_404(Movie, slug=slug)

            if not pelicula.archivo or not os.path.isfile(pelicula.archivo.path):
                return redirect('archivo_no_disponible', slug=pelicula.slug)

            ya_descargo = DescargaUsuarioPelicula.objects.filter(user=request.user, movie=pelicula).exists()

            if ya_descargo:
                messages.info(request, '📦 Ya has descargado esta película anteriormente 🧙‍♀️')
                return redirect('pelicula_info', slug=pelicula.slug)

            DescargaUsuarioPelicula.objects.create(user=request.user, movie=pelicula)
            messages.success(request, '✅ Descarga completada ✨')

            try:
                response = FileResponse(
                    pelicula.archivo.open(),
                    as_attachment=True,
                    filename=os.path.basename(pelicula.archivo.name)
                )
                return response
            except IOError:
                messages.error(request, '❌ Error al acceder al archivo')
                return redirect('pelicula_info', slug=pelicula.slug)
                
        except Exception as e:
            messages.error(request, '❌ Error inesperado al procesar la descarga')
            return redirect('index')


# para registrar una nueva descarga
class DescargaCreateView(LoginRequiredMixin, View):
    template_name = 'partials/descarga_form.html'

    def get(self, request):
        form = DescargaForm(user=request.user)
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = DescargaForm(request.POST, user=request.user)
        if form.is_valid():
            descarga = form.save(commit=False)
            descarga.user = request.user
            descarga.save()
            messages.success(request, '✅ Descarga registrada exitosamente')
            return redirect('descarga_list')
        messages.error(request, '❌ Error al registrar la descarga')
        return render(request, self.template_name, {'form': DescargaForm(user=request.user)})


# para eliminar una descarga (solo el dueño o staff)
class DescargaDeleteView(LoginRequiredMixin, View):
    template_name = 'partials/descarga_confirm_delete.html'

    def get(self, request, pk):
        descarga = get_object_or_404(DescargaUsuarioPelicula, pk=pk)
        if not (request.user.is_staff or descarga.user == request.user):
            messages.error(request, '❌ Solo puedes eliminar tus propias descargas.')
            raise PermissionDenied
        return render(request, self.template_name, {'object': descarga})

    def post(self, request, pk):
        descarga = get_object_or_404(DescargaUsuarioPelicula, pk=pk)
        if not (request.user.is_staff or descarga.user == request.user):
            messages.error(request, '❌ Solo puedes eliminar tus propias descargas.')
            raise PermissionDenied
        descarga.delete()
        messages.success(request, '✅ Descarga eliminada correctamente.')
        return redirect('descarga_list')
    

# Para vistas que requieren ser superuser
class SuperUserRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            messages.error(request, '👑 Solo los superusuarios pueden acceder a esta función')
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

# Para vistas que solo el dueño puede modificar
class OwnerRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.user != request.user and not request.user.is_staff:
            messages.error(request, '🚫 No tienes permisos para realizar esta acción')
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

    def get_object(self):
        return get_object_or_404(DescargaUsuarioPelicula, pk=self.kwargs['pk'])