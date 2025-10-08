from django.db import models

# Create your models here.
class Noticia(models.Model):
    CATEGORIAS = [
        ('política', 'Política'),
        ('esportes','Esportes'),
        ('entretenimento','Entretenimento'),
        ('tecnologia','Tecnologia'),
        ('saúde', 'Saúde'),
        ('economia','Economia'),
        ('outros','Outros')
    ]
    image = models.ImageField("Imagem", upload_to='receitas/images/', blank=True, null=True)
    
    titulo=models.CharField("Título", max_length=200)
    categoria = models.CharField("Categoria", max_length=50, choices=CATEGORIAS, default='Outros')
    
    descricao=models.CharField("Descrição", max_length=255)
    introducao=models.TextField("Introdução")
    desenvolvimento_inicial=models.TextField("Desenvolvimento")
    video = models.TextField("Vídeo", help_text='link do youtube')
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
