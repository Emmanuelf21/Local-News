from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('cadastro/', views.login_cadastro, name='login_cadastro'),
    path('logout/', views.logout_view, name='logout'),
    path('noticia/<int:id>/', views.detalhar_noticia, name='detalhar_noticia'),
    path('cadastrar_noticia/', views.cadastrar_noticia, name='cadastrar_noticia'),
    path('editar/<int:id>/', views.editar_noticia, name='editar_noticia'),
    path('excluir/<int:id>/', views.excluir_noticia, name='excluir_noticia'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('perfil/',views.perfil, name='perfil'),
    path('noticia/<int:id>/', views.detalhar_noticia, name='detalhar_noticia'),
    path('noticia/<int:noticia_id>/curtir/', views.curtir_noticia, name='curtir_noticia'),
<<<<<<< HEAD
    path('noticia/<int:id>/comentar/', views.comentar, name='comentar'),
    path('comentario/<int:comentario_id>/editar/', views.editar_comentario, name='editar_comentario'),
    path('comentario/<int:comentario_id>/deletar/', views.apagar_comentario, name='deletar_comentario'),
=======
    path('comentario/adicionar/<int:noticia_id>/', views.comentar, name='comentar'),
    path('comentario/editar/<int:id>/', views.editar_comentario, name='editar_comentario'),
    path('comentario/deletar/<int:id>/', views.deletar_comentario, name='deletar_comentario'),
>>>>>>> 6b5dd5d7c0423fced9a750396086e49a8b15d2d2
]
