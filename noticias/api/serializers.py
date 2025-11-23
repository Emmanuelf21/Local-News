from rest_framework import serializers
from ..models import Noticia, Tag, Comentario, Bairro, Perfil, Visualizacao, Categoria, Curtida, Usuario

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
            'conclusao', 'image','tema', 'categoria', 'created_at'
        ]

class NoticiaCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Noticia
        exclude = ['usuario', 'categoria', 'created_at', 'updated_at']

class BairroSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bairro
        fields = ['id', 'bairro', 'latitude', 'longitude']

class PerfilSerializer(serializers.ModelSerializer):
    class Meta:
        model = Perfil
        fields = ['id', 'perfil']
        
class UsuarioSimplesSerializer(serializers.ModelSerializer):
    perfil = PerfilSerializer(read_only=True)

    class Meta:
        model = Usuario
        fields = ['email_usuario', 'nome_usuario', 'perfil']

class AtualizarUsuarioSerializer(serializers.ModelSerializer):
    senha = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = Usuario
        fields = ['nome_usuario', 'senha']

    def update(self, instance, validated_data):
        # Atualiza nome
        instance.nome_usuario = validated_data.get('nome_usuario', instance.nome_usuario)
        
        # Atualiza senha
        senha = validated_data.get('senha', None)
        if senha:
            instance.set_password(senha)

        instance.save()
        return instance

class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = ["id", "categoria"]
        
class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ["id", "name", "slug"]

class VisualizacaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Visualizacao
        fields = ['id', 'noticia', 'quantidade']

class CurtidaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Curtida
        fields = ['id', 'usuario', 'noticia', 'created_at']
        read_only_fields = ['usuario', 'created_at']

class ComentarioSerializer(serializers.ModelSerializer):
    usuario = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Comentario
        fields = ['id', 'usuario', 'noticia', 'comentario', 'created_at']
        read_only_fields = ['id', 'usuario', 'created_at']