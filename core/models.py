from django.db import models
from django.contrib.auth.models import AbstractUser

# ----------------------------------------------------------------------------------o
# Custom User Model, cambios del auth_user de django
# ----------------------------------------------------------------------------------
class User(AbstractUser):
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128) # Hashed password storage
    last_login = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    id_perfil = models.IntegerField(null=True, blank=True, help_text="ID del perfil asociado"
    )
    
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email'] # Email is required for user creation 
    
    class meta:
        verbose_name = 'Usuario Personalizado'
        verbose_name_plural = 'Usuarios Personalizados' 
        
    def __str__(self):
        return self.username 

# ----------------------------------------------------------------------------------
# Perfil   
# ----------------------------------------------------------------------------------
class Perfil(models.Model):
    id_user = models.CharField(max_length=150, unique=True, null=False)
    email= models.EmailField(unique=True, null=False)
    password = models.CharField(max_length=128, null=False) 
    fecha_registro= models.DateTimeField(auto_now_add=True, null=False)
    ultima_conexion= models.DateTimeField(auto_now=True, null=False)
    
    class meta:
        verbose_name = 'Perfil de Usuario'
        verbose_name_plural = 'Perfiles de Usuario'
    def __str__(self):
        return self.user

# ----------------------------------------------------------------------------------
# Genero de peliculas
# ----------------------------------------------------------------------------------
class genero(models.Model):
    nombre=models.CharField(max_length=150, null=False)
    descripcion=models.TextField(null=False)
    
    class meta:
        verbose_name = 'Genero'
        verbose_name_plural = 'Generos'
    def __str__(self):
        return self.nombre

# ----------------------------------------------------------------------------------
# Movie(Peliculas)
# ----------------------------------------------------------------------------------
class Movie(models.Model):
    titulo=models.CharField(max_length=150, null=False)
    descripcion=models.TextField(null=False)
    fecha_lanzamiento=models.DateField(null=False)
    duracion=models.IntegerField(null=False)
    archivo=models.FileField(upload_to='movies/', null=False)
    poster=models.ImageField(upload_to='posters/', null=False)
    autores=models.CharField(max_length=250, null=False)
    
    class meta:
        verbose_name = 'Pelicula'
        verbose_name_plural = 'Peliculas'
    def __str__(self):
        return self.titulo

# ----------------------------------------------------------------------------------
# Opinion
# ----------------------------------------------------------------------------------
class Opinion(models.Model):
    id_user = models.CharField(max_length=150, unique=True, null=False)
    email= models.EmailField(unique=True, null=False)
    descripcion= models.TextField(null=False)
    fecha_registro= models.DateTimeField(auto_now_add=True, null=False)
    id_movie= models.IntegerField(null=False)
    
    class meta:
        verbose_name = 'Opinion de Usuario'
        verbose_name_plural = 'Opiniones de Usuario'
    def __str__(self):
        return self.user

# ----------------------------------------------------------------------------------
# Curiosidades de las peliculas 
# ----------------------------------------------------------------------------------
class curiosidades(models.Model):
    titulo=models.CharField(max_length=150, null=False)
    descripcion=models.TextField(null=False)
    
    class meta:
        verbose_name = 'Curiosidad'
        verbose_name_plural = 'Curiosidades'
    def __str__(self):
        return self.titulo

# ----------------------------------------------------------------------------------
# Para descargar peliculas
# ----------------------------------------------------------------------------------
class Descargas_user_movie(models.Model):
    id_user=models.CharField(max_length=150, null=False)
    id_movie=models.CharField(max_length=150, null=False)
    fecha_descarga=models.DateTimeField(auto_now_add=True, null=False)
    
    class meta:
        verbose_name = 'Descarga de Usuario'
        verbose_name_plural = 'Descargas de Usuario'
    def __str__(self):
        return self.id_user + " - " + self.id_movie

# ----------------------------------------------------------------------------------
# Genero-Movie(tabla intermedia)
# ----------------------------------------------------------------------------------
class genero_movie(models.Model):
    id_movie=models.CharField(max_length=150, null=False)
    id_genero=models.CharField(max_length=150, null=False)
    
    class meta:
        verbose_name = 'Genero de Pelicula'
        verbose_name_plural = 'Generos de Pelicula'
    def __str__(self):
        return self.id_movie + " - " + self.id_genero



# ----------------------------------------------------------------------------------
# Movie-curiosiades(tabla intermedia)
# ----------------------------------------------------------------------------------
class Movie_curiosidades(models.Model):
    id_movie=models.CharField(max_length=150, null=False)
    id_curiosidades=models.CharField(max_length=150, null=False)
    
    
    class meta:
        verbose_name = 'Curiosidad de Pelicula'
        verbose_name_plural = 'Curiosidades de Pelicula'
    def __str__(self):
        return self.id_movie + " - " + self.id_curiosidades


    
