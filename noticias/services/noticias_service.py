from django.db.models import Q, Count
from django.shortcuts import get_object_or_404
from ..models import Noticia, Tag, Visualizacao, Comentario, Curtida
from ..utils import mapa_noticias

def get_home_data(tema_id=None, query=None):
    temas = Tag.objects.all()

    if tema_id:
        tema = get_object_or_404(Tag, id=tema_id)
        noticias = Noticia.objects.filter(tema=tema)
    else:
        noticias = Noticia.objects.filter(categoria__id=1)

    noticias = noticias.order_by('-created_at')

    if query:
        noticias = noticias.filter(
            Q(titulo__icontains=query) |
            Q(descricao__icontains=query) |
            Q(introducao__icontains=query) |
            Q(desenvolvimento_inicial__icontains=query) |
            Q(desenvolvimento_final__icontains=query) |
            Q(conclusao__icontains=query)
        )

    mais_curtidas = Noticia.objects.annotate(
        num_curtidas=Count('curtidas')
    ).order_by('-num_curtidas')[:6]

    ultimas_noticias = Noticia.objects.order_by('-created_at')[:5]

    return {
        "temas": temas,
        "tema_id": tema_id,
        "noticias": noticias,
        "ultimas_noticias": ultimas_noticias,
        "mais_curtidas": mais_curtidas,
        "mapa_html": mapa_noticias(),
    }

def get_noticia_detail(noticia_id, usuario=None):
    """
    Retorna os dados completos de uma única notícia, incluindo:
    - Comentários ordenados por data decrescente
    - Total de curtidas
    - Se o usuário logado curtiu
    - Mais curtidas do site
    - Visualizações (incrementa)
    """
    noticia = get_object_or_404(Noticia, id=noticia_id)

    # Atualiza visualizações
    visualizacao, created = Visualizacao.objects.get_or_create(noticia=noticia)
    visualizacao.quantidade += 1
    visualizacao.save(update_fields=['quantidade'])

    # Comentários
    comentarios = Comentario.objects.filter(noticia=noticia).order_by('-created_at')

    # Mais curtidas
    mais_curtidas = Noticia.objects.annotate(num_curtidas=Count('curtidas')).order_by('-num_curtidas')[:6]

    # Total de curtidas
    total_curtidas = Curtida.objects.filter(noticia=noticia).count()

    # Se o usuário logado curtiu
    usuario_curtiu = False
    if usuario and usuario.is_authenticated:
        usuario_curtiu = Curtida.objects.filter(noticia=noticia, usuario=usuario).exists()

    return {
        "noticia": noticia,
        "comentarios": comentarios,
        "visualizacoes": visualizacao.quantidade,
        "total_curtidas": total_curtidas,
        "usuario_curtiu": usuario_curtiu,
        "mais_curtidas": mais_curtidas,
    }
    
def criar_noticia(validated_data, usuario, analisar_func):
    noticia = Noticia(**validated_data)
    noticia.usuario = usuario

    partes = [
        noticia.titulo,
        noticia.descricao,
        noticia.introducao,
        noticia.desenvolvimento_inicial,
        noticia.desenvolvimento_final,
        noticia.conclusao
    ]
    texto = ". ".join([p for p in partes if p])

    label = analisar_func(texto)

    noticia.categoria_id = 1 if label == 0 else 2
    noticia.save()

    return noticia