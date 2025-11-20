from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.db.models import Count
from .forms import CadastroForm, LoginForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import NoticiaForm
from .models import Noticia, Curtida, Visualizacao, Comentario, Categoria
import folium
from taggit.models import Tag 
from .utils import analisar_texto_noticia 
from django.db.models import Q
from django.core.paginator import Paginator

def login_cadastro(request):
    cadastro_form = CadastroForm()
    login_form = LoginForm()

    if request.method == 'POST':
        # 🔹 Verifica qual formulário foi enviado
        if 'cadastro_submit' in request.POST:
            cadastro_form = CadastroForm(request.POST)
            if cadastro_form.is_valid():
                cadastro_form.save()
                messages.success(request, 'Usuário cadastrado com sucesso! Faça login.')
                return redirect('login_cadastro')
            else:
                messages.error(request, 'Erro no cadastro. Verifique os campos.')
        
        elif 'login_submit' in request.POST:
            login_form = LoginForm(request.POST)
            if login_form.is_valid():
                email = login_form.cleaned_data.get('email')
                senha = login_form.cleaned_data.get('senha')
                user = authenticate(email_usuario=email, password=senha)
                if user is not None:
                    login(request, user)
                    messages.success(request, f'Bem-vindo, {user.nome_usuario}!')
                    return redirect('home')
                else:
                    messages.error(request, 'Email ou senha incorretos.')

    context = {
        'cadastro_form': cadastro_form,
        'login_form': login_form,
    }
    return render(request, 'noticias/cadastro.html', context)


def home(request):
    tema_id = request.GET.get('tema')
    temas = Tag.objects.all()
    
    
    if tema_id:
        tema = get_object_or_404(Tag, id=tema_id)
        noticias = Noticia.objects.filter(tema=tema).order_by('-created_at')
    else:
        noticias = Noticia.objects.filter(categoria__id=1)
        noticias = noticias.order_by('-created_at')
        
        
    #  Notícias mais curtidas (até 6)
    mais_curtidas = Noticia.objects.annotate(num_curtidas=Count('curtidas')).order_by('-num_curtidas')[:6]

    # 🔹 Últimas 5 notícias para o carrossel
    ultimas_noticias = Noticia.objects.all().order_by('-created_at')[:5]
    
    # 🔹 Mapa interativo
    mapa_html = mapa_noticias()

    # BARRA DE PESQUISA
    query = request.GET.get('q')
    if query:
        noticias = noticias.filter(
            Q(titulo__icontains=query) |
            Q(descricao__icontains=query) |
            Q(introducao__icontains=query) |
            Q(desenvolvimento_inicial__icontains=query) |
            Q(desenvolvimento_final__icontains=query) |
            Q(conclusao__icontains=query)
        )

    context = {
        'noticias': noticias,
        'ultimas_noticias': ultimas_noticias,  # envia para o template
        'mais_curtidas': mais_curtidas,   
        'tema_selecionada': tema_id,
        'temas': temas,
        'mapa': mapa_html,
    }
    return render(request, 'noticias/home.html', context)


# 📰 NOVA VIEW — página individual da notícia
def detalhar_noticia(request, id):
    noticia = get_object_or_404(Noticia, id=id)
    # 🔢 Atualiza as visualizações
    visualizacao, created = Visualizacao.objects.get_or_create(noticia=noticia)
    visualizacao.quantidade += 1
    visualizacao.save(update_fields=['quantidade'])

    # 💬 Busca comentários
    comentarios = Comentario.objects.filter(noticia=noticia).order_by('-created_at')
    
    #  Notícias mais curtidas (até 6)
    mais_curtidas = Noticia.objects.annotate(num_curtidas=Count('curtidas')).order_by('-num_curtidas')[:6]

    # ❤️ Lógica de curtidas
    total_curtidas = Curtida.objects.filter(noticia=noticia).count()

    # Verifica se o usuário atual já curtiu (se estiver logado)
    usuario_curtiu = False
    if request.user.is_authenticated:
        usuario_curtiu = Curtida.objects.filter(noticia=noticia, usuario=request.user).exists()

    context = {
        'noticia': noticia,
        'comentarios': comentarios,
        'visualizacoes': visualizacao.quantidade,
        'total_curtidas': total_curtidas,
        'mais_curtidas': mais_curtidas, 
        'usuario_curtiu': usuario_curtiu,
    }

    return render(request, 'noticias/detalhar_noticia.html', context)

@login_required
def curtir_noticia(request, noticia_id):
    noticia = get_object_or_404(Noticia, id=noticia_id)
    usuario = request.user

    curtida_existente = Curtida.objects.filter(noticia=noticia, usuario=usuario).first()
    if curtida_existente:
        curtida_existente.delete()
    else:
        Curtida.objects.create(noticia=noticia, usuario=usuario)

    return redirect('detalhar_noticia', id=noticia.id)


def logout_view(request):
    logout(request)
    messages.info(request, 'Você saiu da sua conta.')
    return redirect('login_cadastro')



@login_required
def cadastrar_noticia(request):
    if request.method == 'POST':
        form = NoticiaForm(request.POST, request.FILES)
        if form.is_valid():
            noticia = form.save(commit=False)
            noticia.usuario = request.user

            # Combina o texto principal da notícia
            partes = [
                noticia.titulo,
                noticia.introducao,
                noticia.desenvolvimento_inicial,
                noticia.desenvolvimento_final,
                noticia.conclusao
            ]
            texto = ". ".join([p for p in partes if p])

            # Chama o modelo da Hugging Face
            label = analisar_texto_noticia(texto)
            
            # Interpreta o resultado e define a categoria
            
            if label == 0:
                noticia.categoria_id = 1  # REAL
            else:
                noticia.categoria_id = 2 

            noticia.save()
            return redirect('home')
    else:
        form = NoticiaForm()
    return render(request, 'noticias/cadastrar_noticia.html', {'form': form})


@login_required
def dashboard(request):
    user = request.user

    # Separando publicadas e recusadas
    if user.is_superuser:
        noticias_publicadas = Noticia.objects.filter(categoria_id=1).order_by("-id")
        noticias_recusadas = Noticia.objects.exclude(categoria_id=1).order_by("-id")
    else:
        noticias_publicadas = Noticia.objects.filter(usuario=user, categoria_id=1).order_by("-id")
        noticias_recusadas = Noticia.objects.filter(usuario=user).exclude(categoria_id=1).order_by("-id")

    # --- Paginação ---
    # Publicadas
    paginator_pub = Paginator(noticias_publicadas, 5)
    page_pub_number = request.GET.get("page_pub")
    page_obj_pub = paginator_pub.get_page(page_pub_number)

    # Recusadas
    paginator_rec = Paginator(noticias_recusadas, 5)
    page_rec_number = request.GET.get("page_rec")
    page_obj_rec = paginator_rec.get_page(page_rec_number)

    # --- Visualizações ---
    visualizacoes = Visualizacao.objects.all()
    total_visualizacoes = 0

    # Corrigindo a verificação do perfil
    perfil_nome = user.perfil.perfil.lower()  # admin / editor

    if perfil_nome == "admin":
        total_visualizacoes = sum(v.quantidade for v in visualizacoes)
    elif perfil_nome == "editor":
        visualizacoes_user = Visualizacao.objects.filter(noticia__in=noticias_publicadas)
        total_visualizacoes = sum(v.quantidade for v in visualizacoes_user)

    # Curtidas
    total_curtidas = sum(n.curtidas.count() for n in noticias_publicadas)

    return render(request, "noticias/dashboard.html", {
        "page_obj_pub": page_obj_pub,
        "page_obj_rec": page_obj_rec,
        "visualizacoes": visualizacoes,
        "total_visualizacoes": total_visualizacoes,
        "total_curtidas": total_curtidas,
    })
    # user = request.user

    # # Admin vê todas as notícias, editor vê apenas as suas
    # if user.is_superuser:
    #     noticias = Noticia.objects.all()
    # else:
    #     noticias = Noticia.objects.filter(usuario=user)
    
    # # Todas as visualizações
    # visualizacoes = Visualizacao.objects.all()
    # total_visualizacoes=0
    
    # if (user.perfil.perfil == 'admin'):
    #     total_visualizacoes = sum(v.quantidade for v in visualizacoes)
        
    # elif (user.perfil.perfil == 'editor'):
    #     visualizacoes2 = Visualizacao.objects.filter(noticia__in=noticias)
    #     total_visualizacoes = sum(v.quantidade for v in visualizacoes2)
        
    # # Totais
    # total_curtidas = sum(n.curtidas.count() for n in noticias)

    # context = {
    #     'noticias': noticias,
    #     'visualizacoes': visualizacoes,  # ← ENVIA A TABELA COMPLETA
    #     'total_visualizacoes': total_visualizacoes,
    #     'total_curtidas': total_curtidas,
    # }
    
    # return render(request, 'noticias/dashboard.html', context)

@login_required
def perfil(request):
    user = request.user
    
    return render(request, 'noticias/perfil.html', {'user': user})

@login_required
def editar_noticia(request, id):
    noticia = get_object_or_404(Noticia, id=id)

    # Só o autor ou admin pode editar
    if not request.user.is_superuser and noticia.usuario != request.user:
        messages.error(request, "Você não tem permissão para editar esta notícia.")
        return redirect('dashboard')

    # Instancia o form com os dados da notícia existente
    if request.method == "POST":
        form = NoticiaForm(request.POST, request.FILES, instance=noticia)
        
        if form.is_valid():
            noticia_editada = form.save(commit=False)
            noticia_editada.usuario = noticia.usuario  # mantém o autor original
            
            # Combina o texto principal da notícia
            partes = [
                noticia_editada.titulo,
                noticia_editada.introducao,
                noticia_editada.desenvolvimento_inicial,
                noticia_editada.desenvolvimento_final,
                noticia_editada.conclusao
            ]
            
            texto = ". ".join([p for p in partes if p])

            # Chama o modelo da Hugging Face
            label = analisar_texto_noticia(texto)
            
            # Interpreta o resultado e define a categoria
            
            if label == 0:
                noticia_editada.categoria_id = 1  # REAL
            else:
                noticia_editada.categoria_id = 2
                
            noticia_editada.save()
            messages.success(request, "Notícia atualizada com sucesso!")
            return redirect('dashboard')
    else:
        form = NoticiaForm(instance=noticia)

    context = {'form': form, 'noticia': noticia}
    return render(request, 'noticias/editar_noticia.html', context)



@login_required
def excluir_noticia(request, id):
    noticia = get_object_or_404(Noticia, id=id)
    if not request.user.is_superuser and noticia.usuario != request.user:
        messages.error(request, "Você não tem permissão para excluir esta notícia.")
        return redirect('dashboard')

    noticia.delete()
    messages.success(request, "Notícia excluída com sucesso!")
    return redirect('dashboard')



def mapa_noticias():
    noticias = Noticia.objects.select_related('bairro', 'usuario', 'tema')

    # 🌎 Mapa centralizado em Rio Branco - AC, com mobile funcionando
    mapa = folium.Map(
        location=[-9.97499, -67.8243],  # Rio Branco - AC
        zoom_start=13,
        zoom_control=True,        # habilita controle de zoom para mobile
        scrollWheelZoom=True,     # permite zoom por gesto
        dragging=True,            # permite arrastar em mobile
        touchZoom=True,           # zoom por pinça no celular
    )

    # 🟦 Adiciona marcadores das notícias
    for noticia in noticias:
        bairro = noticia.bairro
        if bairro.latitude and bairro.longitude:

            popup_text = f"""
                    <div style="
                            width: 230px;
                            font-family: Arial, sans-serif;
                            border-radius: 10px;
                            overflow: hidden;
                            box-shadow: 0 2px 8px rgba(0,0,0,0.15);
                            background: #ffffff;
                        ">
                            <img src='{noticia.image.url if noticia.image else ""}'
                                style="width: 100%; height: 120px; object-fit: cover; display: block;" />

                            <div style="padding: 10px;">
                                <h4 style="margin: 0 0 5px 0; font-size: 15px; font-weight: bold; color: #333;">
                                    {noticia.titulo}
                                </h4>

                                <p style="margin: 0; font-size: 13px; color: #666;">
                                    <i>{bairro.bairro}</i>
                                </p>

                                <p style="margin: 4px 0 10px 0; font-size: 12px; color: #999;">
                                    {noticia.tema}
                                </p>

                                <a href='/noticia/{noticia.id}/'
                                target='_blank'
                                style="
                                        display: inline-block;
                                        background: #2563eb;
                                        color: white;
                                        padding: 6px 10px;
                                        border-radius: 6px;
                                        text-decoration: none;
                                        font-size: 12px;
                                        font-weight: bold;
                                ">
                                    Ver notícia →
                                </a>
                            </div>
                        </div>

            """

            folium.Marker(
                location=[bairro.latitude, bairro.longitude],
                popup=folium.Popup(popup_text, max_width=300),
                tooltip=noticia.titulo,
                icon=folium.Icon(color='blue', icon='info-sign')
            ).add_to(mapa)

    # 🔒 Define limites aproximados de Rio Branco (opcional)
    mapa.options['maxBounds'] = [
        [-10.20, -68.00],  # sudoeste
        [-9.90, -67.60]    # nordeste
    ]

    mapa_html = mapa._repr_html_()
    return mapa_html

