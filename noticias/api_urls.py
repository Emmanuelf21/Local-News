from django.urls import path
from .api_views import *

urlpatterns = [
    #GET
    path('usuarios/me/', usuario_logado, name='usuario_logado'),
    path("noticias/", noticias_home_api),
    path('noticias/<int:noticia_id>/', noticia_detail_api, name='api_noticia_detail'),
    path('bairros/', listar_bairros, name='listar-bairros'),
    path('perfil/', listar_perfis, name='listar-perfis'),
    path('categorias/', listar_categorias, name='listar-categorias'),
    path('temas/', listar_temas, name='listar-temas'),
    path('visualizacoes', listar_visualizacoes, name='listar-visualizacoes'),
    path('curtidas/', listar_curtidas, name='listar_curtidas'),
    path('comentarios/', listar_comentarios, name='listar_comentarios'),
    
    #POST
    path('cadastrar_noticia/', cadastrar_noticia_api, name='cadastrar_noticia_api'),
    path('cadastro/', cadastro_api, name='api_cadastro'),
    path('login/', login_api, name='api_login'),
    path('visualizacoes/criar/', criar_visualizacao, name='criar_visualizacao'),
    path('curtidas/criar/', criar_curtida, name='criar_curtida'),
    path('comentarios/criar/', criar_comentario, name='criar_comentario'),
    
    
    #PUT
    path('noticias/<int:id>/editar/', editar_noticia_api, name='editar-noticia-api'),
    path('visualizacoes/<int:id>/', atualizar_visualizacao, name='atualizar_visualizacao'),
    path('usuarios/me/editar/', atualizar_usuario, name='atualizar_usuario'),
    path('comentarios/<int:id>/editar/', atualizar_comentario, name='atualizar_comentario'),

    #DELETE
    path('noticias/<int:id>/excluir/', excluir_noticia_api, name='noticia-excluir-api'),
    path('curtidas/<int:id>/deletar/', deletar_curtida, name='deletar_curtida'),
    path('comentarios/<int:id>/deletar/', deletar_comentario, name='deletar_comentario'),
    
]
