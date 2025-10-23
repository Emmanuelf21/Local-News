from django.urls import path
from . import views

urlpatterns=[
    path('', views.home, name='home'),
    path('cadastro/', views.login_cadastro, name='login_cadastro'),
    path('logout/', views.logout_view, name='logout'),
]