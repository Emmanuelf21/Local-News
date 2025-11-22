from django.urls import path
from .api_views import *

urlpatterns = [
    #GET
    path("noticias/", noticias_home_api),
    path('noticias/<int:noticia_id>/', noticia_detail_api, name='api_noticia_detail'),
    path('bairros/', listar_bairros, name='listar-bairros'),
    
    #POST
    path('cadastrar_noticia/', cadastrar_noticia_api, name='cadastrar_noticia_api'),
    path('cadastro/', cadastro_api, name='api_cadastro'),
    path('login/', login_api, name='api_login'),
    
    #PUT
    path('noticias/<int:id>/editar/', editar_noticia_api, name='editar-noticia-api'),
    
    #DELETE
    path('noticias/<int:id>/excluir/', excluir_noticia_api, name='noticia-excluir-api'),

]
