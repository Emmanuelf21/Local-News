from django.contrib import admin
from .models import Noticia, Categoria, Bairro, Comentario

# Register your models here.
admin.site.register(Noticia)
admin.site.register(Categoria)
admin.site.register(Bairro)
admin.site.register(Comentario)