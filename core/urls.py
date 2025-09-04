from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static  
from django.conf import settings
from . import views
from .views import ( IndexView, CuriosidadListView, CuriosidadCreateView, CuriosidadUpdateView, CuriosidadDeleteView, GeneroListView, GeneroCreateView, GeneroUpdateView, GeneroDeleteView, MovieListView, MovieCreateView, MovieUpdateView, MovieDeleteView, DescargaListView, DescargaCreateView, DescargaDeleteView, PeliculaInfoView, PeliculaDescargaView,
MovieUpdateView, archivo_no_disponible, guardar_opinion_general )

urlpatterns = [
    # Incluye las URLs de autenticación de Django
    path('', include('django.contrib.auth.urls')), 
    
    #url para el admin
    path('admin/', admin.site.urls),
    
    #url para la pagina principal
    path('', IndexView.as_view(), name='index'),
    
    #urls para register
    path('register/', views.RegisterView.as_view(), name='register'),
    
    #urls para login  
    path('login/', views.LoginView.as_view(), name='login'),
    
    #urls para comentarios
    path('comment/', views.CommentView.as_view(), name='comment'),

    #url para guardar opinion general
    path('opinion-general/', guardar_opinion_general, name='comment'),

    #urls para CRUD de Curiosidades
    path('curiosidades/',             CuriosidadListView.as_view(),   name='curiosidad_list'),
    path('curiosidades/nueva/',       CuriosidadCreateView.as_view(), name='curiosidad_nueva'),
    path('curiosidades/<int:pk>/editar/', CuriosidadUpdateView.as_view(), name='curiosidad_editar'),
    path('curiosidades/<int:pk>/borrar/',  CuriosidadDeleteView.as_view(), name='curiosidad_borrar'),
    
    #urls para CRUD de Generos
    path('generos/',                GeneroListView.as_view(),   name='genero_list'),
    path('generos/nuevo/',          GeneroCreateView.as_view(), name='genero_nuevo'),
    path('generos/<int:pk>/editar/', GeneroUpdateView.as_view(), name='genero_editar'),
    path('generos/<int:pk>/borrar/',  GeneroDeleteView.as_view(), name='genero_borrar'),
    
    # urls para CRUD de Peliculas
    path('peliculas/',              MovieListView.as_view(),   name='movie_list'),
    path('peliculas/nueva/',        MovieCreateView.as_view(), name='movie_nueva'),
    path('peliculas/<int:pk>/editar/', MovieUpdateView.as_view(), name='movie_editar'),
    path('peliculas/<int:pk>/borrar/',  MovieDeleteView.as_view(), name='movie_borrar'),
    
    # urls para manejar las descargas de peliculas por usuarios
    path('descargas/',               DescargaListView.as_view(),   name='descarga_list'),
    path('descargas/nueva/',         DescargaCreateView.as_view(), name='descarga_nueva'),
    path('descargas/<int:pk>/borrar/', DescargaDeleteView.as_view(), name='descarga_borrar'),
    
    # urls para manejar informacion y detalles de las peliculas
    path('pelicula/<slug:slug>/',      PeliculaInfoView.as_view(),  name='pelicula_info'),
    path('pelicula/<slug:slug>/descargar/', PeliculaDescargaView.as_view(), name='pelicula_descargar'),
    path('pelicula/<int:pk>/editar/',  MovieUpdateView.as_view(),   name='movie_edit'),
    
    # url para manejar cuando el archivo no esta disponible
    path('DreamWorks/pelicula/<slug:slug>/archivo-no-disponible/', archivo_no_disponible, name='archivo_no_disponible'),
    

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
# Configuración para servir archivos media durante el desarrollo



