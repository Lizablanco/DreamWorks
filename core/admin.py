from django.utils.html import format_html # para previsualizar imágenes en el admin
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Curiosidad, Movie, Genero, MovieCuriosidad, DescargaUsuarioPelicula, OpinionGeneral, Opinion


# Register your models here.

# Registro del modelo User personalizado
admin.site.register(User, UserAdmin)

# Registro del modelo OpinionGeneral
admin.site.register(OpinionGeneral)

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
    list_display = ('titulo', 'fecha_lanzamiento', 'slug')
    list_per_page=4
    prepopulated_fields = {'slug': ('titulo',)}
    search_fields = ('titulo',)
    filter_horizontal = ('generos',)
    inlines = [MovieCuriosidadInline]
    
    def vista_poster(self, obj):
        if obj.poster:
            return format_html('<img src="{}" width="80" />', obj.poster.url)
        return "Sin imagen"
    vista_poster.short_description = "Póster"
    readonly_fields = ('vista_poster',)
    fieldsets = (
    (None, {
        'fields': (
            'titulo', 'descripcion', 'fecha_lanzamiento', 'duracion',
            'archivo', 'enlace_externo', 'poster', 'vista_poster',
            'autores', 'generos', 'slug'
        )
    }),
)


#
# 5. Descargas de Usuario
#
@admin.register(DescargaUsuarioPelicula)
class DescargaUsuarioPeliculaAdmin(admin.ModelAdmin):
    list_display       = ('user', 'movie', 'fecha_descarga')
    list_per_page=4
    search_fields      = ('user__username', 'movie__titulo')
    list_filter        = ('fecha_descarga', 'movie')
    date_hierarchy     = 'fecha_descarga'
    raw_id_fields      = ('user', 'movie')
    list_select_related = ('user', 'movie')

#
#6. opiniones de usuarios
#

@admin.register(Opinion)
class OpinionAdmin(admin.ModelAdmin):
    list_display = ('user', 'movie', 'descripcion', 'fecha_registro')
    list_per_page=4
    list_filter = ('movie', 'fecha_registro')
    search_fields = ('user__username', 'movie__titulo', 'descripcion')
    ordering = ('-fecha_registro',)
    raw_id_fields = ('user', 'movie')
    
#exclude = ('descripcion'), excluye un campo de la vista del admin