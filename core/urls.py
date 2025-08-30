from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.RegisterView.as_view(), name='register'),  
    path('login/', views.LoginView.as_view(), name='login'),
    path('comment/', views.CommentView.as_view(), name='comment'),
]
