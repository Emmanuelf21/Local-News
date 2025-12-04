from django.contrib import admin
from .models import Noticia, Categoria, Bairro, Comentario, Usuario
from django_summernote.admin import SummernoteModelAdmin

class SummerAdmin(SummernoteModelAdmin):
    summernote_fields = '__all__'

# Register your models here.
admin.site.register(Noticia, SummerAdmin)
admin.site.register(Categoria)
admin.site.register(Bairro)
admin.site.register(Comentario)
admin.site.register(Usuario)