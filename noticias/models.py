from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from .managers import UsuarioManager
from geopy.geocoders import Nominatim
from taggit.models import Tag

# # Create your models here.
# class UsuarioManager(BaseUserManager):
#     def create_user(self, email_usuario, nome_usuario, password=None, perfil='usuario'):
#         if not email_usuario:
#             raise ValueError("O campo 'email' é obrigatório.")
#         email_usuario = self.normalize_email(email_usuario)

#         user = self.model(
#             email_usuario=email_usuario,
#             nome_usuario=nome_usuario,
#             perfil=perfil,
#         )
#         user.set_password(password)  # Importante: usa o set_password
#         user.save(using=self._db)
#         return user

#     def create_editor(self, email_usuario, nome_usuario, password):
#         return self.create_user(
#             email_usuario=email_usuario,
#             nome_usuario=nome_usuario,
#             password=password,
#             perfil='editor'
#         )

#     def create_superuser(self, email_usuario, nome_usuario, password):
#         user = self.create_user(
#             email_usuario=email_usuario,
#             nome_usuario=nome_usuario,
#             password=password,
#             perfil='editor',  # ou 'admin' se quiser outro perfil
#         )
#         user.is_staff = True
#         user.is_superuser = True
#         user.save(using=self._db)
#         return user
    
# class Usuario(AbstractBaseUser, PermissionsMixin):
#     PERFIS = (
#         ('usuario', 'Usuário Comum'),
#         ('editor', 'Editor'),
#     )

#     email_usuario = models.EmailField("Email", unique=True)
#     nome_usuario = models.CharField("Nome de Usuário", max_length=150)
#     senha_usuario = models.CharField("Senha", max_length=128)
#     perfil = models.CharField("Perfil", max_length=10, choices=PERFIS, default='usuario')

#     is_active = models.BooleanField(default=True)
#     is_staff = models.BooleanField(default=False)

#     # Adicionando related_name para evitar conflito
#     groups = models.ManyToManyField(
#         'auth.Group',
#         related_name='usuario_set',  # Aqui definimos um nome exclusivo para o relacionamento
#         blank=True
#     )
#     user_permissions = models.ManyToManyField(
#         'auth.Permission',
#         related_name='usuario_set',  # Aqui definimos um nome exclusivo para o relacionamento
#         blank=True
#     )

#     objects = UsuarioManager()

#     USERNAME_FIELD = 'email_usuario'
#     REQUIRED_FIELDS = ['nome_usuario']

#     def __str__(self):
#         return self.email_usuario
class Usuario(AbstractBaseUser, PermissionsMixin):
    PERFIS = [
        ('usuario', 'Usuário Comum'),
        ('editor', 'Editor'),
        ('admin', 'Administrador'),
    ]

    email_usuario = models.EmailField(unique=True)
    nome_usuario = models.CharField(max_length=150)
    perfil = models.CharField(max_length=20, choices=PERFIS, default='usuario')

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UsuarioManager()

    USERNAME_FIELD = 'email_usuario'
    REQUIRED_FIELDS = ['nome_usuario']

    def __str__(self):
        return self.nome_usuario

class Noticia(models.Model):
    image = models.ImageField("Imagem", upload_to='noticias/images/', blank=True, null=True)
    
    titulo=models.CharField("Título", max_length=200)
    categoria = models.ForeignKey('Categoria', on_delete=models.CASCADE, related_name="noticias", verbose_name="Categoria", default=1)
    tema = models.ForeignKey(Tag, on_delete=models.CASCADE, related_name='noticias')
    usuario = models.ForeignKey(
        get_user_model(),  # Isso já está correto
        on_delete=models.CASCADE,
        related_name='Noticias',
        verbose_name='Usuário',
        null=True,
    )

    bairro = models.ForeignKey('Bairro', on_delete=models.CASCADE, related_name='noticias', verbose_name='Bairro', default=1)
    descricao=models.CharField("Descrição", max_length=255)
    introducao=models.TextField("Introdução")
    desenvolvimento_inicial=models.TextField("Desenvolvimento")
    video = models.TextField("Vídeo", blank=True)
    desenvolvimento_final=models.TextField("Desenvolvimento")
    conclusao=models.TextField("Conclusão")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self): 
        return self.titulo
    
    def save(self, *args, **kwargs):
        if self.video:
            if 'watch?v=' in self.video:
                self.video = self.video.replace('watch?v=', 'embed/')
            elif 'youtu.be/' in self.video:
                video_id = self.video.split('youtu.be/')[1]
                self.video = f'https://www.youtube.com/embed/{video_id}'
        super().save(*args, **kwargs)
        
    class Meta:
        verbose_name = "Notícia"
        verbose_name_plural = "Notícias"
        ordering = ['-created_at'] #ordena as receitas pela data de criação (mais novas primeiro)


class Comentario(models.Model):
    usuario = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name='comentarios',
        verbose_name='Usuário',
    )
    
    noticia = models.ForeignKey(
        Noticia,
        on_delete=models.CASCADE,
        related_name='comentarios',
        verbose_name='Notícia',
    )
    
    comentario = models.TextField("Comentário")
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self): 
        return self.comentario  # Limita no print

    class Meta:
        verbose_name = "Comentario"
        verbose_name_plural = "Comentarios"
        ordering = ['-created_at']

class Categoria(models.Model):
    categoria = models.CharField("Categoria", max_length=50)
    
    def __str__(self): 
        return self.categoria

class Bairro(models.Model):
    bairro = models.CharField("Bairro", max_length=150)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    def save(self, *args, **kwargs):
        # Se não tiver coordenadas, tenta geocodificar automaticamente
        if not self.latitude or not self.longitude:
            geolocator = Nominatim(user_agent="localnews_bairros")
            location = geolocator.geocode(f"{self.bairro}, Acre, Brasil")
            if location:
                self.latitude = location.latitude
                self.longitude = location.longitude
        super().save(*args, **kwargs)

    def __str__(self): 
        return self.bairro
    
class Perfil(models.Model):
    perfil = models.CharField("Perfil", max_length=50)
    
    def __str__(self):
        return self.perfil
    
User = get_user_model()

class Curtida(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    noticia = models.ForeignKey(Noticia, on_delete=models.CASCADE, related_name='curtidas')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('usuario', 'noticia')


class Visualizacao(models.Model):
    noticia = models.ForeignKey(Noticia, on_delete=models.CASCADE, related_name='visualizacoes')
    data = models.DateTimeField(auto_now_add=True)
