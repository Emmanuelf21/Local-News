from django.contrib import admin
from .models import Noticia, Categoria, Bairro, Comentario, Usuario

# Register your models here.
admin.site.register(Noticia)
admin.site.register(Categoria)
admin.site.register(Bairro)
admin.site.register(Comentario)
admin.site.register(Usuario)