# models.py
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings

# ----------------------------------------------------------------------------------
# Custom User Model
# ----------------------------------------------------------------------------------
class User(AbstractUser):
    email = models.EmailField(unique=True)  # Email único
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']
    
    class Meta:
        verbose_name = 'Usuario Personalizado'
        verbose_name_plural = 'Usuarios Personalizados' 
        
    def __str__(self):
        return self.username

# ----------------------------------------------------------------------------------
# Perfil   
# ----------------------------------------------------------------------------------
class Perfil(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,  
        on_delete=models.CASCADE,
        related_name='perfil'
    )
    
    fecha_registro = models.DateTimeField(auto_now_add=True)
    ultima_conexion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Perfil de Usuario'
        verbose_name_plural = 'Perfiles de Usuario'
        
    def __str__(self):
        return f"Perfil de {self.user.username}"

# ----------------------------------------------------------------------------------
# Genero de peliculas
# ----------------------------------------------------------------------------------
class Genero(models.Model):
    nombre = models.CharField(max_length=150)
    descripcion = models.TextField()
    
    class Meta:
        verbose_name = 'Género'
        verbose_name_plural = 'Géneros'
        
    def __str__(self):
        return self.nombre

# ----------------------------------------------------------------------------------
# Movie(Peliculas)
# ----------------------------------------------------------------------------------
class Movie(models.Model):
    titulo = models.CharField(max_length=150)
    descripcion = models.TextField()
    fecha_lanzamiento = models.DateField()
    duracion = models.IntegerField()
    archivo = models.FileField(upload_to='movies/')
    poster = models.ImageField(upload_to='posters/')
    autores = models.CharField(max_length=250)
    
    generos = models.ManyToManyField(Genero, related_name='peliculas')
    curiosidades = models.ManyToManyField('Curiosidad', through='MovieCuriosidad', related_name='peliculas')
    
    class Meta:
        verbose_name = 'Película'
        verbose_name_plural = 'Películas'
        
    def __str__(self):
        return self.titulo

# ----------------------------------------------------------------------------------
# Opinión
# ----------------------------------------------------------------------------------
class Opinion(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='opiniones'
    )
    
    movie = models.ForeignKey(
        Movie,
        on_delete=models.CASCADE,
        related_name='opiniones'
    )
    
    descripcion = models.TextField()
    fecha_registro = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Opinión de Usuario'
        verbose_name_plural = 'Opiniones de Usuario'
        unique_together = ['user', 'movie']
        
    def __str__(self):
        return f"Opinión de {self.user.username} sobre {self.movie.titulo}"

# ----------------------------------------------------------------------------------
# Curiosidades
# ----------------------------------------------------------------------------------
class Curiosidad(models.Model):
    titulo = models.CharField(max_length=150)
    descripcion = models.TextField()
    
    class Meta:
        verbose_name = 'Curiosidad'
        verbose_name_plural = 'Curiosidades'
        
    def __str__(self):
        return self.titulo

# ----------------------------------------------------------------------------------
# Para descargar películas (CORREGIDO)
# ----------------------------------------------------------------------------------
class DescargaUsuarioPelicula(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='descargas'
    )
    
    movie = models.ForeignKey(
        Movie,
        on_delete=models.CASCADE,
        related_name='descargas'
    )
    
    fecha_descarga = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Descarga de Usuario'
        verbose_name_plural = 'Descargas de Usuarios'
        unique_together = ['user', 'movie']
        
    def __str__(self):
        return f"{self.user.username} - {self.movie.titulo}"

# ----------------------------------------------------------------------------------
# Movie-curiosidades (tabla intermedia CORREGIDA)
# ----------------------------------------------------------------------------------
class MovieCuriosidad(models.Model):
    movie = models.ForeignKey(
        Movie,
        on_delete=models.CASCADE,
        related_name='curiosidades_intermedias'
    )
    
    curiosidad = models.ForeignKey(
        Curiosidad,
        on_delete=models.CASCADE,
        related_name='peliculas_intermedias'
    )
    
    #  Campo adicional para metadata
    fecha_asociacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'movie_curiosidades'
        verbose_name = 'Curiosidad de Película'
        verbose_name_plural = 'Curiosidades de Películas'
        unique_together = ['movie', 'curiosidad']
        
    def __str__(self):
        return f"{self.movie.titulo} - {self.curiosidad.titulo}"