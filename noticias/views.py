from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
from django.contrib import messages

Usuario = get_user_model()
# Create your views here.
def home(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        nome = request.POST.get('nome')
        senha = request.POST.get('senha')
        perfil = request.POST.get('perfil')  # Captura o perfil selecionado

        # Verifica se o email já está cadastrado
        if Usuario.objects.filter(email_usuario=email).exists():
            messages.error(request, 'Email já cadastrado.')
            return redirect('home.html')

        # Cria o usuário com o perfil selecionado
        if perfil == 'editor':
            Usuario.objects.create_editor(
                email_usuario=email,
                nome_usuario=nome,
                senha_usuario=senha
            )
        else:
            Usuario.objects.create_user(
                email_usuario=email,
                nome_usuario=nome,
                senha_usuario=senha,
                perfil='usuario'
            )
        
        messages.success(request, 'Usuário cadastrado com sucesso.')
        return redirect('home.html')

    return render(request, "noticias/home.html")