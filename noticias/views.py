from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model
from django.contrib import messages
from .forms import CadastroForm, LoginForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import NoticiaForm
from .models import Noticia, Curtida, Visualizacao, Comentario, Categoria
import folium
from taggit.models import Tag 
from .utils import analisar_texto_noticia

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
        noticias = Noticia.objects.all().order_by('-created_at')

    # 🔹 Últimas 5 notícias para o carrossel
    ultimas_noticias = Noticia.objects.all().order_by('-created_at')[:5]

    # 🔹 Mapa interativo
    mapa_html = mapa_noticias()

    context = {
        'noticias': noticias,
        'ultimas_noticias': ultimas_noticias,  # envia para o template
        'tema_selecionada': tema_id,
        'temas': temas,
        'mapa': mapa_html,
    }
    return render(request, 'noticias/home.html', context)


# 📰 NOVA VIEW — página individual da notícia
def detalhar_noticia(request, id):
    noticia = get_object_or_404(Noticia, id=id)

    visualizacao, created = Visualizacao.objects.get_or_create(noticia=noticia)
    visualizacao.quantidade += 1
    visualizacao.save(update_fields=['quantidade'])

    comentarios = Comentario.objects.filter(noticia=noticia).order_by('-created_at')

    context = {
        'noticia': noticia,
        'comentarios': comentarios,
        'visualizacoes': visualizacao.quantidade,
    }
    return render(request, 'noticias/detalhar_noticia.html', context)


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

    # Admin vê todas as notícias, editor vê apenas as suas
    if user.is_superuser:
        noticias = Noticia.objects.all()
    else:
        noticias = Noticia.objects.filter(usuario=user)

    # Totais do dashboard
    total_visualizacoes = sum(n.visualizacoes.count() for n in noticias)
    total_curtidas = sum(n.curtidas.count() for n in noticias)

    context = {
        'noticias': noticias,
        'total_visualizacoes': total_visualizacoes,
        'total_curtidas': total_curtidas,
    }
    return render(request, 'noticias/dashboard.html', context)

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

    # Mapa inicial do Brasil
    mapa = folium.Map(
        location=[-9.95, -67.75],
        zoom_start=13,
        zoom_control=False,
        scrollWheelZoom=False,
        doubleClickZoom=False,
        touchZoom=False,
    )
    
    for noticia in noticias:
        bairro = noticia.bairro
        if bairro.latitude and bairro.longitude:
            popup_text = f"""
                <b>{noticia.titulo}</b><br>
                <i>{bairro.bairro}</i><br>
                <small>{noticia.tema}</small><br>
                <a href='/noticia/{noticia.id}/' target='_blank'>Ver notícia</a>
            """
            folium.Marker(
                location=[bairro.latitude, bairro.longitude],
                popup=folium.Popup(popup_text, max_width=300),
                tooltip=noticia.titulo,
                icon=folium.Icon(color='blue', icon='info-sign')
            ).add_to(mapa)


    mapa.options['maxBounds'] = [
        [-10.02, -67.95],
        [-9.98, -67.75],
        [-10.02, -67.95],
        [-9.98, -67.75]
    ]

    mapa_html = mapa._repr_html_()
    return mapa_html
