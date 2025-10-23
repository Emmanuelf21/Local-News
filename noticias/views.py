from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
from django.contrib import messages
from .forms import CadastroForm, LoginForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
# Create your views here.

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
    return render(request, 'noticias/home.html')


def logout_view(request):
    logout(request)
    messages.info(request, 'Você saiu da sua conta.')
    return redirect('login_cadastro')