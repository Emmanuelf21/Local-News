from django.urls import path
from . import views

urlpatterns=[
    path('', views.home, name='home'),
    path('mapa/', views.mapa_noticias, name='mapa_noticias'),
    path('cadastro/', views.login_cadastro, name='login_cadastro'),
    path('logout/', views.logout_view, name='logout'),
    path('cadastrar_noticia/', views.cadastrar_noticia, name='cadastrar_noticia'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('editar/<int:id>/', views.editar_noticia, name='editar_noticia'),
    path('excluir/<int:id>/', views.excluir_noticia, name='excluir_noticia'),
]