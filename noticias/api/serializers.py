from rest_framework import serializers
from ..models import Noticia, Tag, Comentario

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name']

class NoticiaSerializer(serializers.ModelSerializer):
    tema = TagSerializer()
    categoria = serializers.StringRelatedField()

    class Meta:
        model = Noticia
        fields = [
            'id', 'titulo', 'descricao', 'introducao',
            'desenvolvimento_inicial', 'desenvolvimento_final', 
            'conclusao', 'tema', 'categoria', 'created_at'
        ]

class ComentarioSerializer(serializers.ModelSerializer):
    usuario = serializers.StringRelatedField()
    
    class Meta:
        model = Comentario
        fields = ['id', 'usuario', 'conteudo', 'created_at']