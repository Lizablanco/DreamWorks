from django.utils.html import format_html # para previsualizar imágenes en el admin
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Curiosidad, Movie, Genero, MovieCuriosidad, DescargaUsuarioPelicula

# Register your models here.

# Registro del modelo User personalizado
admin.site.register(User, UserAdmin)

#
# 1. Género
#
@admin.register(Genero)
class GeneroAdmin(admin.ModelAdmin):
    list_display    = ('nombre',)
    search_fields   = ('nombre', 'descripcion')
    list_filter     = ('nombre',)


#
# 2. Curiosidad
#
@admin.register(Curiosidad)
class CuriosidadAdmin(admin.ModelAdmin):
    list_display    = ('titulo',)
    search_fields   = ('titulo', 'descripcion')
    list_filter     = ('titulo',)


#
# 3. Intermedio Película ↔ Curiosidad
#
class MovieCuriosidadInline(admin.TabularInline):
    model           = MovieCuriosidad
    extra           = 1
    raw_id_fields   = ('curiosidad',)
    verbose_name    = "Curiosidad de Película"
    verbose_name_plural = "Curiosidades de Película"


#
# 4. Película
#
@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display       = ('titulo', 'fecha_lanzamiento', 'duracion', 'autores')
    list_filter        = ('fecha_lanzamiento', 'generos')
    search_fields      = ('titulo', 'autores')
    filter_horizontal  = ('generos',)
    inlines            = [MovieCuriosidadInline]
    fieldsets = (
        (None, {
            'fields': (
                'titulo', 'descripcion', 'autores',
                ('fecha_lanzamiento', 'duracion'),
            )
        }),
        ('Archivos', {
            'fields': ('poster', 'archivo')
        }),
        ('Géneros', {
            'fields': ('generos',)
        }),
    )


#
# 5. Descargas de Usuario
#
@admin.register(DescargaUsuarioPelicula)
class DescargaUsuarioPeliculaAdmin(admin.ModelAdmin):
    list_display       = ('user', 'movie', 'fecha_descarga')
    search_fields      = ('user__username', 'movie__titulo')
    list_filter        = ('fecha_descarga', 'movie')
    date_hierarchy     = 'fecha_descarga'
    raw_id_fields      = ('user', 'movie')
    list_select_related = ('user', 'movie')