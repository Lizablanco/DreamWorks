from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from . import views
from .views import (
    IndexView,
    CuriosidadListView, CuriosidadCreateView, CuriosidadUpdateView, CuriosidadDeleteView,
    GeneroListView, GeneroCreateView, GeneroUpdateView, GeneroDeleteView,
    MovieListView, MovieCreateView, MovieUpdateView, MovieDeleteView,
    DescargaListView, DescargaCreateView, DescargaDeleteView,
    PeliculaInfoView, DescargaPeliculaView,
    archivo_no_disponible, guardar_opinion_general, CommentView, LoginView, RegistroView, UserLogoutView,OpinionesDelReinoView,
)

urlpatterns = [
    # Autenticación de Django (login, logout, password reset, etc.)
    path('accounts/', include('django.contrib.auth.urls')),

    # Panel de administración
    path('admin/', admin.site.urls),

    # Página principal
    path('', IndexView.as_view(), name='index'),

    # Registro y login personalizados
    path('registro/', RegistroView.as_view(), name='registro'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', UserLogoutView.as_view(), name='logout'),

    # Opiniones
    path('pelicula/<slug:slug>/opinar/', CommentView.as_view(), name='comment'),
    path('opinion-general/', guardar_opinion_general, name='comment_general'),
    path('opiniones/', OpinionesDelReinoView.as_view(), name='opiniones_del_reino'),

    # CRUD de Curiosidades
    path('curiosidades/', CuriosidadListView.as_view(), name='curiosidad_list'),
    path('curiosidades/nueva/', CuriosidadCreateView.as_view(), name='curiosidad_nueva'),
    path('curiosidades/<int:pk>/editar/', CuriosidadUpdateView.as_view(), name='curiosidad_editar'),
    path('curiosidades/<int:pk>/borrar/', CuriosidadDeleteView.as_view(), name='curiosidad_borrar'),

    # CRUD de Géneros
    path('generos/', GeneroListView.as_view(), name='genero_list'),
    path('generos/nuevo/', GeneroCreateView.as_view(), name='genero_nuevo'),
    path('generos/<int:pk>/editar/', GeneroUpdateView.as_view(), name='genero_editar'),
    path('generos/<int:pk>/borrar/', GeneroDeleteView.as_view(), name='genero_borrar'),

    # CRUD de Películas
    path('peliculas/', MovieListView.as_view(), name='movie_list'),
    path('peliculas/nueva/', MovieCreateView.as_view(), name='movie_nueva'),
    path('peliculas/<int:pk>/editar/', MovieUpdateView.as_view(), name='movie_editar'),
    path('peliculas/<int:pk>/borrar/', MovieDeleteView.as_view(), name='movie_borrar'),

    # Descargas de películas
    path('descargas/', DescargaListView.as_view(), name='descarga_list'),
    path('descargas/nueva/', DescargaCreateView.as_view(), name='descarga_nueva'),
    path('descargas/<int:pk>/borrar/', DescargaDeleteView.as_view(), name='descarga_borrar'),

    # Información y acciones sobre películas
    path('pelicula/<slug:slug>/', PeliculaInfoView.as_view(), name='pelicula_info'),
    path('descargar/<slug:slug>/', DescargaPeliculaView.as_view(), name='pelicula_descargar'),

    # Página de error si no hay archivo disponible
    path('DreamWorks/pelicula/<slug:slug>/archivo-no-disponible/', archivo_no_disponible, name='archivo_no_disponible'),
]

# Archivos multimedia en desarrollo
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)