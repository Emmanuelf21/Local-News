from django.urls import path
from .api_views import *

urlpatterns = [
    path("noticias/", noticias_home_api),
    path('noticias/<int:noticia_id>/', noticia_detail_api, name='api_noticia_detail'),
    path('cadastro/', cadastro_api, name='api_cadastro'),
    path('login/', login_api, name='api_login'),
]
