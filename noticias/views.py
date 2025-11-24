from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.db.models import Count
from .forms import CadastroForm, LoginForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import NoticiaForm
from .models import Noticia, Curtida, Visualizacao, Comentario, Categoria
from taggit.models import Tag 
from .utils import analisar_texto_noticia 
from django.db.models import Q
from django.core.paginator import Paginator

from .utils import mapa_noticias
from .services.noticias_service import *

from django.http import JsonResponse
from .api_views import cadastro_api, login_api
from rest_framework.test import APIRequestFactory

def login_cadastro(request):
    cadastro_form = CadastroForm()
    login_form = LoginForm()

    if request.method == 'POST':
        if 'cadastro_submit' in request.POST:
            cadastro_form = CadastroForm(request.POST)
            if cadastro_form.is_valid():
                usuario = cadastro_form.save()
                messages.success(request, 'Usuário cadastrado com sucesso! Faça login.')
                return redirect('login_cadastro')  # redireciona para a própria página de cadastro/login
            else:
                messages.error(request, 'Erro no cadastro. Verifique os campos.')

        elif 'login_submit' in request.POST:
            login_form = LoginForm(request.POST)
            if login_form.is_valid():
                email = login_form.cleaned_data.get('email')
                senha = login_form.cleaned_data.get('senha')
                user = authenticate(email_usuario=email, password=senha)
                if user:
                    login(request, user)
                    messages.success(request, f'Bem-vindo, {user.nome_usuario}!')
                    return redirect('home')  # redireciona para a home após login
                else:
                    messages.error(request, 'Email ou senha incorretos.')

    context = {
        'cadastro_form': cadastro_form,
        'login_form': login_form,
    }
    return render(request, 'noticias/cadastro.html', context)

def home(request):
    data = get_home_data(
        tema_id=request.GET.get("tema"),
        query=request.GET.get("q")
    )

    context = {
        'noticias': data["noticias"],
        'ultimas_noticias': data["ultimas_noticias"],
        'mais_curtidas': data["mais_curtidas"],
        'tema_selecionada': data["tema_id"],
        'temas': data["temas"],
        'mapa': mapa_noticias(),
    }

    return render(request, 'noticias/home.html', context)



# 📰 NOVA VIEW — página individual da notícia
def detalhar_noticia(request, id):
    data = get_noticia_detail(id, usuario=request.user)
    
    context = {
        'noticia': data["noticia"],
        'comentarios': data["comentarios"],
        'visualizacoes': data["visualizacoes"],
        'total_curtidas': data["total_curtidas"],
        'usuario_curtiu': data["usuario_curtiu"],
        'mais_curtidas': data["mais_curtidas"],
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
    return redirect('login_cadastro')



@login_required
def cadastrar_noticia(request):
    if request.method == 'POST':
        form = NoticiaForm(request.POST, request.FILES)

        if form.is_valid():
            noticia = criar_noticia(
                validated_data=form.cleaned_data,
                usuario=request.user,
                analisar_func=analisar_texto_noticia
            )
            return redirect('home')

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

    if request.method == "POST":
        form = NoticiaForm(request.POST, request.FILES, instance=noticia)
        if form.is_valid():
            # Reutiliza a função atualizar_noticia
            noticia_editada = atualizar_noticia(
                noticia,
                form.cleaned_data,
                analisar_texto_noticia
            )
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

#secção de comentarios eu acho kkkkk

def detalhar_noticia(request, id):
    noticia = get_object_or_404(Noticia, id=id)

    # Registrar visualização automática
    Visualizacao.objects.get_or_create(usuario=request.user if request.user.is_authenticated else None,
                                       noticia=noticia)

    comentarios = Comentario.objects.filter(noticia=noticia).order_by('-criado_em')

    context = {
        'noticia': noticia,
        'comentarios': comentarios,
    }
    return render(request, 'noticias/detalhar_noticia.html', context)

@login_required
def comentar(request, id):
    noticia = get_object_or_404(Noticia, id=id)

    if request.method == "POST":
        texto = request.POST.get("texto")
        if texto.strip():
            Comentario.objects.create(
                usuario=request.user,
                noticia=noticia,
                texto=texto
            )
            messages.success(request, "Comentário enviado!")
        else:
            messages.error(request, "O comentário não pode estar vazio.")

    return redirect('detalhar_noticia', id=noticia.id)



