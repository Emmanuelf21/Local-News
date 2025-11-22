from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from .utils import analisar_texto_noticia
from .api.serializers import *
from .services.noticias_service import *

# imports de cadastro/login
from .forms import CadastroForm, LoginForm
from django.contrib.auth import authenticate, login
from rest_framework import status

# CRUD para Notícias
@api_view(['GET'])
def noticias_home_api(request):
    data = get_home_data(
        tema_id=request.GET.get("tema"),
        query=request.GET.get("q")
    )

    return Response({
        "noticias": NoticiaSerializer(data["noticias"], many=True).data,
        "ultimas_noticias": NoticiaSerializer(data["ultimas_noticias"], many=True).data,
        "mais_curtidas": NoticiaSerializer(data["mais_curtidas"], many=True).data,
        "temas": TagSerializer(data["temas"], many=True).data,
        "tema_selecionada": data["tema_id"],
        "mapa": data["mapa_html"],
    })

@api_view(['GET'])
def noticia_detail_api(request, noticia_id):
    """
    API que retorna os detalhes de uma notícia específica:
    - /api/noticias/<id>/
    - Retorna JSON com:
        - noticia
        - comentarios
        - total de visualizações
        - total de curtidas
        - usuario_curtiu
        - mais_curtidas
    """
    data = get_noticia_detail(noticia_id, usuario=request.user)

    return Response({
        "noticia": NoticiaSerializer(data["noticia"]).data,
        "comentarios": ComentarioSerializer(data["comentarios"], many=True).data,
        "visualizacoes": data["visualizacoes"],
        "total_curtidas": data["total_curtidas"],
        "usuario_curtiu": data["usuario_curtiu"],
        "mais_curtidas": NoticiaSerializer(data["mais_curtidas"], many=True).data,
    })
  
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def cadastrar_noticia_api(request):

    serializer = NoticiaCreateSerializer(data=request.data)

    if serializer.is_valid():
        noticia = criar_noticia(
            validated_data=serializer.validated_data,
            usuario=request.user,
            analisar_func=analisar_texto_noticia
        )
        return Response({"id": noticia.id}, status=201)

    return Response(serializer.errors, status=400)

# ----------------------------------------------------------------------  
# GET Bairros
@api_view(['GET'])
def listar_bairros(request):
    bairros = Bairro.objects.all().order_by('bairro')
    serializer = BairroSerializer(bairros, many=True)
    return Response(serializer.data)

# ----------------------------------------------------------------------  
# CRUD Login
@api_view(['POST'])
def cadastro_api(request):
    """
    API para cadastro de usuários.
    - Endpoint: POST /api/cadastro/
    - Body (JSON):
        {
            "nome_usuario": "João",
            "email_usuario": "joao@email.com",
            "senha": "123456",
            "confirmar_senha": "123456"
        }
    - Retorno 201 Created ou 400 Bad Request com erros de validação.
    """
    form = CadastroForm(request.data)
    if form.is_valid():
        usuario = form.save()
        return Response({
            "mensagem": "Usuário cadastrado com sucesso!",
            "usuario_id": usuario.id,
            "nome_usuario": usuario.nome_usuario
        }, status=status.HTTP_201_CREATED)
    else:
        return Response({
            "mensagem": "Erro no cadastro.",
            "erros": form.errors
        }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def login_api(request):
    """
    API para login de usuários.
    - Endpoint: POST /api/login/
    - Body (JSON):
        {
            "email": "joao@email.com",
            "senha": "123456"
        }
    - Retorna 200 OK com dados do usuário ou 400 Bad Request se login falhar.
    """
    form = LoginForm(request.data)
    if form.is_valid():
        email = form.cleaned_data.get('email')
        senha = form.cleaned_data.get('senha')
        user = authenticate(email_usuario=email, password=senha)
        if user is not None:
            login(request, user)
            return Response({
                "mensagem": f"Bem-vindo, {user.nome_usuario}!",
                "usuario_id": user.id,
                "nome_usuario": user.nome_usuario
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                "mensagem": "Email ou senha incorretos."
            }, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({
            "mensagem": "Erro no login.",
            "erros": form.errors
        }, status=status.HTTP_400_BAD_REQUEST)