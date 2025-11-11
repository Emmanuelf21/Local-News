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

# def cadastro(request):
#     if request.method == 'POST':
#         form = CadastroForm(request.POST)
#         if form.is_valid():
#             form.save()
#             messages.success(request, 'Usuário cadastrado com sucesso!')
#             return redirect('cadastro')
#         else:
#             messages.error(request, 'Por favor, corrija os erros abaixo.')
#     else:
#         form = CadastroForm()

#     return render(request, 'noticias/cadastro.html', {'form': form})

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
    categoria_id = request.GET.get('categoria')
    categorias = Tag.objects.all()

    if categoria_id:
        categoria = get_object_or_404(Tag, id=categoria_id)
        noticias = Noticia.objects.filter(categoria=categoria).order_by('-created_at')
    else:
        noticias = Noticia.objects.all().order_by('-created_at')

    # 🔹 Últimas 5 notícias para o carrossel
    ultimas_noticias = Noticia.objects.all().order_by('-created_at')[:5]

    # 🔹 Mapa interativo
    mapa_html = mapa_noticias()

    context = {
        'noticias': noticias,
        'ultimas_noticias': ultimas_noticias,  # envia para o template
        'categoria_selecionada': categoria_id,
        'categorias': categorias,
        'mapa': mapa_html,
    }
    return render(request, 'noticias/home.html', context)


def logout_view(request):
    logout(request)
    messages.info(request, 'Você saiu da sua conta.')
    return redirect('login_cadastro')

@login_required
def cadastrar_noticia(request):
    if request.method == 'POST':
        form = NoticiaForm(request.POST, request.FILES)
        if form.is_valid():
            noticia = form.save(commit=False)  # não salva ainda
            noticia.usuario = request.user      # define o usuário logado
            noticia.save()
            return redirect('home')
            # return redirect('lista_noticias')   # troque pelo nome da sua view de listagem
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
    noticias = Noticia.objects.select_related('bairro', 'usuario', 'categoria')

    # Mapa inicial do Brasil
    mapa = folium.Map(
    location=[-9.95, -67.75],  # ajustar conforme necessidade
    zoom_start=13,
    zoom_control=False,
    scrollWheelZoom=False,
    doubleClickZoom=False,
    touchZoom=False
    )
    
    for noticia in noticias:
        bairro = noticia.bairro
        if bairro.latitude and bairro.longitude:
            popup_text = f"""
                <b>{noticia.titulo}</b><br>
                <i>{bairro.bairro}</i><br>
                <small>{noticia.categoria}</small><br>
                <a href='/noticia/{noticia.id}/' target='_blank'>Ver notícia</a>
            """
            

            folium.Marker(
                location=[bairro.latitude, bairro.longitude],
                popup=folium.Popup(popup_text, max_width=300),
                tooltip=noticia.titulo,
                icon=folium.Icon(color='blue', icon='info-sign')
            ).add_to(mapa)
    mapa.options['maxBounds'] = [
    [-10.02, -67.95],  # sudoeste (y-mín, x-mín)
    [-9.98, -67.75]   # nordeste (y-máx, x-máx)
    ]

    mapa_html = mapa._repr_html_()
    return mapa_html
