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

@api_view(['GET','PUT'])
@permission_classes([IsAuthenticated])
def editar_noticia_api(request, id):
    """
        Modelo de PUT para atualizar a notícia
        {
        "id": 231,
        "titulo": "Nova praça inaugurada",
        "descricao": "Moradores comemoram",
        "introducao": "Evento reuniu dezenas de pessoas...",
        "desenvolvimento_inicial": "As obras começaram...",
        "desenvolvimento_final": "A praça inclui jardim...",
        "conclusao": "A comunidade aprovou...",
        "tema": 2
    }

    """
    noticia = get_object_or_404(Noticia, id=id)

    # Só o autor ou admin pode editar
    if not request.user.is_superuser and noticia.usuario != request.user:
        return Response({"detail": "Você não tem permissão para editar esta notícia."},
                        status=status.HTTP_403_FORBIDDEN)

    if request.method == 'GET':
        serializer = NoticiaSerializer(noticia)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = NoticiaCreateSerializer(data=request.data, partial=True)
        if serializer.is_valid():
            noticia_editada = atualizar_noticia(
                noticia, serializer.validated_data, analisar_texto_noticia
            )
            return Response(NoticiaSerializer(noticia_editada).data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def excluir_noticia_api(request, id):
    noticia = get_object_or_404(Noticia, id=id)

    # Só o autor ou admin pode excluir
    if not request.user.is_superuser and noticia.usuario != request.user:
        return Response(
            {"detail": "Você não tem permissão para excluir esta notícia."},
            status=status.HTTP_403_FORBIDDEN
        )

    noticia.delete()
    return Response({"detail": "Notícia excluída com sucesso."}, status=status.HTTP_200_OK)

# ----------------------------------------------------------------------  
# GET Bairros
@api_view(['GET'])
def listar_bairros(request):
    bairros = Bairro.objects.all().order_by('bairro')
    serializer = BairroSerializer(bairros, many=True)
    return Response(serializer.data)

# ----------------------------------------------------------------------  
# GET Perfil
@api_view(['GET'])
def listar_perfis(request):
    perfis = Perfil.objects.all().order_by('perfil')
    serializer = PerfilSerializer(perfis, many=True)
    return Response(serializer.data)

# ----------------------------------------------------------------------  
# GET Temas
@api_view(['GET'])
def listar_temas(request):
    temas = Tag.objects.all().order_by('name')
    serializer = TagSerializer(temas, many=True)
    return Response(serializer.data)

# ----------------------------------------------------------------------  
# GET Categorias (Real ou Fake)

@api_view(['GET'])
def listar_categorias(request):
    categorias = Categoria.objects.all().order_by('categoria')
    serializer = CategoriaSerializer(categorias, many=True)
    return Response(serializer.data)

# ----------------------------------------------------------------------  
# CRUD Visualizações
@api_view(['GET'])
def listar_visualizacoes(request):
    visualizacoes = Visualizacao.objects.all().order_by('id')
    serializer = VisualizacaoSerializer(visualizacoes, many=True)
    return Response(serializer.data)

@api_view(['POST'])
def criar_visualizacao(request):
    """
    Recebe: { "noticia": <id_da_noticia> }
    """
    data = request.data.copy()

    # quantidade padrão = 0 se não enviada
    if "quantidade" not in data:
        data["quantidade"] = 0

    serializer = VisualizacaoSerializer(data=data)

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# PUT — Atualiza visualização por ID
@api_view(['PUT'])
def atualizar_visualizacao(request, id):
    """
    Recebe o ID na tabela visualização para atualizar
    """
    try:
        visualizacao = Visualizacao.objects.get(id=id)
    except Visualizacao.DoesNotExist:
        return Response({"erro": "Visualização não encontrada"}, status=status.HTTP_404_NOT_FOUND)

    serializer = VisualizacaoSerializer(visualizacao, data=request.data, partial=True)

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# ----------------------------------------------------------------------  
# CRUD Curtidas

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def listar_curtidas(request):
    curtidas = Curtida.objects.all().order_by('-created_at')
    serializer = CurtidaSerializer(curtidas, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def criar_curtida(request):
    """
    Recebe o id da notícia e usuário precisa estar logado
    {
    "noticia": 12
    }
    """
    noticia_id = request.data.get('noticia')

    if not noticia_id:
        return Response({"erro": "Campo 'noticia' é obrigatório."}, status=status.HTTP_400_BAD_REQUEST)

    # Verifica se o usuário já curtiu a notícia
    if Curtida.objects.filter(usuario=request.user, noticia_id=noticia_id).exists():
        return Response({"erro": "Você já curtiu esta notícia."}, status=status.HTTP_400_BAD_REQUEST)

    # Cria a curtida
    curtida = Curtida(usuario=request.user, noticia_id=noticia_id)
    curtida.save()

    serializer = CurtidaSerializer(curtida)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def deletar_curtida(request, id):
    try:
        curtida = Curtida.objects.get(id=id, usuario=request.user)
    except Curtida.DoesNotExist:
        return Response({"erro": "Curtida não encontrada."}, status=status.HTTP_404_NOT_FOUND)

    curtida.delete()
    return Response({"mensagem": "Curtida removida com sucesso."}, status=status.HTTP_204_NO_CONTENT)

# ----------------------------------------------------------------------  
# CRUD Comentários
# GET — lista todos os comentários
@api_view(['GET'])
def listar_comentarios(request):
    comentarios = Comentario.objects.all().order_by('-created_at')
    serializer = ComentarioSerializer(comentarios, many=True)
    return Response(serializer.data)

# POST — cria comentário (usuário logado)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def criar_comentario(request):
    """
    Exemplo de POST
    {
    "noticia": 12,
    "comentario": "Ótima notícia!"
    }
    """
    serializer = ComentarioSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(usuario=request.user)  # passa o usuário logado diretamente
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# PUT — atualiza comentário (somente se for do usuário logado)
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def atualizar_comentario(request, id):
    try:
        comentario = Comentario.objects.get(id=id, usuario=request.user)
    except Comentario.DoesNotExist:
        return Response({"erro": "Comentário não encontrado ou você não tem permissão."}, status=status.HTTP_404_NOT_FOUND)

    serializer = ComentarioSerializer(comentario, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# DELETE — remove comentário (somente do usuário logado)
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def deletar_comentario(request, id):
    try:
        comentario = Comentario.objects.get(id=id, usuario=request.user)
    except Comentario.DoesNotExist:
        return Response({"erro": "Comentário não encontrado ou você não tem permissão."}, status=status.HTTP_404_NOT_FOUND)

    comentario.delete()
    return Response({"mensagem": "Comentário removido com sucesso."}, status=status.HTTP_204_NO_CONTENT)

# ----------------------------------------------------------------------  
# CRUD Login
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def usuario_logado(request):
    usuario = request.user  # pega o usuário autenticado
    serializer = UsuarioSimplesSerializer(usuario)
    return Response(serializer.data)

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

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def atualizar_usuario(request):
    usuario = request.user
    serializer = AtualizarUsuarioSerializer(usuario, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response({"mensagem": "Usuário atualizado com sucesso."})
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)