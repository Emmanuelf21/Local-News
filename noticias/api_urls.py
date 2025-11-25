from django.urls import path
# from .api_views import *
from . import api_views
urlpatterns = [
    #GET
    path('usuarios/me/', api_views.usuario_logado, name='usuario_logado'),
    path("noticias/", api_views.noticias_home_api, name='noticias_api'),
    path('noticias/<int:noticia_id>/', api_views.noticia_detail_api, name='api_noticia_detail'),
    path('bairros/', api_views.listar_bairros, name='listar-bairros'),
    path('perfil/', api_views.listar_perfis, name='listar-perfis'),
    path('categorias/', api_views.listar_categorias, name='listar-categorias'),
    path('temas/', api_views.listar_temas, name='listar-temas'),
    path('visualizacoes', api_views.listar_visualizacoes, name='listar-visualizacoes'),
    path('curtidas/', api_views.listar_curtidas, name='listar_curtidas'),
    path('comentarios/', api_views.listar_comentarios, name='listar_comentarios'),
    
    #POST
    path('cadastrar_noticia/', api_views.cadastrar_noticia_api, name='cadastrar_noticia_api'),
    path('cadastro/', api_views.cadastro_api, name='api_cadastro'),
    path('login/', api_views.login_api, name='api_login'),
    path('visualizacoes/criar/', api_views.criar_visualizacao, name='criar_visualizacao'),
    path('curtidas/criar/', api_views.criar_curtida, name='criar_curtida'),
    path('comentarios/criar/', api_views.criar_comentario, name='criar_comentario'),
    
    
    #PUT
    path('noticias/<int:id>/editar/', api_views.editar_noticia_api, name='editar-noticia-api'),
    path('visualizacoes/<int:id>/', api_views.atualizar_visualizacao, name='atualizar_visualizacao'),
    path('usuarios/me/editar/', api_views.atualizar_usuario, name='atualizar_usuario'),
    path('comentarios/<int:id>/editar/', api_views.atualizar_comentario, name='atualizar_comentario'),

    #DELETE
    path('noticias/<int:id>/excluir/', api_views.excluir_noticia_api, name='noticia-excluir-api'),
    path('curtidas/<int:id>/deletar/', api_views.deletar_curtida, name='deletar_curtida'),
    path('comentarios/<int:id>/deletar/', api_views.deletar_comentario, name='deletar_comentario_api'),
    
]
