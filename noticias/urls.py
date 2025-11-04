from django.urls import path
from . import views

urlpatterns=[
    path('', views.home, name='home'),
<<<<<<< HEAD
    path('cadastro/', views.cadastro, name='cadastro')
=======
    path('cadastro/', views.login_cadastro, name='login_cadastro'),
    path('logout/', views.logout_view, name='logout'),
    path('cadastrar_noticia/', views.cadastrar_noticia, name='cadastrar_noticia'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('editar/<int:id>/', views.editar_noticia, name='editar_noticia'),
    path('excluir/<int:id>/', views.excluir_noticia, name='excluir_noticia'),
>>>>>>> 8f491f7b23b9d85142f354bc0cbf4aaf279a88d8
]