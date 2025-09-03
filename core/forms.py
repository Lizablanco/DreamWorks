from django import forms
from .models import Curiosidad, Genero, Movie, DescargaUsuarioPelicula

#formulario para agregar una curiosidad
class CuriosidadForm(forms.ModelForm):
    class Meta:
        model  = Curiosidad
        fields = ['titulo', 'descripcion']
        widgets = {
            'titulo': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Ej. Shrek (2001) – Premio histórico'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 4,
                'placeholder': 'Detalle de la curiosidad'
            }),
        }
        error_messages = {
            'titulo': {
                'required': 'Debes proporcionar un título.',
                'max_length': 'Máximo 200 caracteres.',
            },
            'descripcion': {
                'required': 'La descripción no puede quedar vacía.',
            },
        }


#formulario para agregar un genero
class GeneroForm(forms.ModelForm):
    class Meta:
        model  = Genero
        fields = ['nombre', 'descripcion']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej. Animación, Aventura'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Breve descripción del género (opcional)'
            }),
        }
        error_messages = {
            'nombre': {
                'required': 'El nombre del género es obligatorio.',
                'unique': 'Este género ya existe.',
                'max_length': 'Máximo 100 caracteres.',
            },
        }

#formulario para agregar una pelicula
class MovieForm(forms.ModelForm):
    class Meta:
        model  = Movie
        fields = [
            'titulo', 'descripcion', 'fecha_lanzamiento',
            'duracion', 'archivo', 'poster', 'autores'
        ]
        widgets = {
            'titulo': forms.TextInput(attrs={'class':'form-control'}),
            'descripcion': forms.Textarea(attrs={'class':'form-control','rows':4}),
            'fecha_lanzamiento': forms.DateInput(
                attrs={'class':'form-control','type':'date'}
            ),
            'duracion': forms.NumberInput(attrs={'class':'form-control'}),
            'autores': forms.TextInput(attrs={'class':'form-control'}),
        }
        error_messages = {
            'titulo': {
                'required': 'El título es obligatorio.',
                'max_length': 'Máximo 150 caracteres.',
            },
            'descripcion': {
                'required': 'La descripción no puede quedar vacía.',
            },
            'fecha_lanzamiento': {
                'required': 'La fecha de lanzamiento es obligatoria.',
                'invalid': 'Formato de fecha inválido. Usa AAAA-MM-DD.',
            },
            'duracion': {
                'required': 'La duración es obligatoria.',
                'invalid': 'Introduce un número válido para la duración.',
            },
            'archivo': {
                'required': 'Debes subir el archivo de la película.',
                'invalid': 'Archivo inválido. Asegúrate de que sea un archivo correcto.',
            },
            'poster': {
                'required': 'Debes subir una imagen para el póster.',
                'invalid': 'Imagen inválida. Asegúrate de que sea un archivo de imagen correcto.',
            },
            'autores': {
                'required': 'El campo autores es obligatorio.',
                'max_length': 'Máximo 250 caracteres.',
            },
        }
    def clean_titulo(self):
        titulo = self.cleaned_data['titulo']
        if Movie.objects.filter(titulo=titulo).exists():
            raise forms.ValidationError("Ya existe una película con ese título.")
        return titulo

# Formulario para que un usuario registre la descarga de una película
class DescargaForm(forms.ModelForm):
    class Meta:
        model  = DescargaUsuarioPelicula
        fields = ['movie']
        widgets = {
            'movie': forms.Select(attrs={'class': 'form-control'})
        }
        error_messages = {
            'movie': {
                'required': 'Debes seleccionar una película.',
                'unique': 'Ya descargaste esa película.'
            }
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            # Solo mostrar películas que no hayas descargado aún
            pendientes = DescargaUsuarioPelicula.objects.filter(user=user).values_list('movie_id', flat=True)
            self.fields['movie'].queryset = Movie.objects.exclude(pk__in=pendientes)
