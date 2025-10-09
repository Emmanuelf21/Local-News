from django.db import models
from django.contrib.auth import get_user_model

# Create your models here.
class Noticia(models.Model):
    image = models.ImageField("Imagem", upload_to='noticias/images/', blank=True, null=True)
    
    titulo=models.CharField("Título", max_length=200)
    categoria = models.ForeignKey('Categoria', on_delete=models.CASCADE, related_name="noticias", verbose_name="Categoria")
    # categoria = models.CharField("Categoria", max_length=50, choices=CATEGORIAS, default='Outros')
    usuario = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name='Noticias',
        verbose_name='Usuário',
        null=True,
    ) 
    bairro = models.ForeignKey('Bairro', on_delete=models.CASCADE, related_name='noticias', verbose_name='Bairro', default=1)
    descricao=models.CharField("Descrição", max_length=255)
    introducao=models.TextField("Introdução")
    desenvolvimento_inicial=models.TextField("Desenvolvimento")
    video = models.TextField("Vídeo", help_text='link do youtube', blank=True)
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
    
    def __str__(self): 
        return self.bairro
    
class Perfil(models.Model):
    perfil = models.CharField("Perfil", max_length=50)
    
    def __str__(self):
        return self.perfil
    
