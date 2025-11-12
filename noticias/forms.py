from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate
from .models import Noticia

Usuario = get_user_model()

class CadastroForm(forms.ModelForm):
    senha = forms.CharField(
        label="Senha",
        widget=forms.PasswordInput(attrs={'class': 'border rounded-lg p-2 w-full'})
    )
    confirmar_senha = forms.CharField(
        label="Confirmar Senha",
        widget=forms.PasswordInput(attrs={'class': 'border rounded-lg p-2 w-full'})
    )

    class Meta:
        model = Usuario
        # 🔹 Removemos o campo 'perfil' daqui
        fields = ['email_usuario', 'nome_usuario']

        widgets = {
            'email_usuario': forms.EmailInput(attrs={'class': 'border rounded-lg p-2 w-full'}),
            'nome_usuario': forms.TextInput(attrs={'class': 'border rounded-lg p-2 w-full'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        senha = cleaned_data.get("senha")
        confirmar = cleaned_data.get("confirmar_senha")

        if senha != confirmar:
            raise forms.ValidationError("As senhas não conferem.")
        return cleaned_data

    def save(self, commit=True):
        usuario = super().save(commit=False)
        usuario.set_password(self.cleaned_data["senha"])

        # 🔹 Define o perfil padrão como "usuário comum"
        # Ajuste o valor conforme o campo do seu modelo (exemplo: 'perfil' pode ser um CharField ou ForeignKey)
        usuario.perfil = 'usuario'  # ou o valor correspondente ao perfil padrão no seu modelo

        if commit:
            usuario.save()
        return usuario

class LoginForm(forms.Form):
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={'class': 'border rounded-lg p-2 w-full'})
    )
    senha = forms.CharField(
        label="Senha",
        widget=forms.PasswordInput(attrs={'class': 'border rounded-lg p-2 w-full'})
    )

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get("email")
        senha = cleaned_data.get("senha")

        if email and senha:
            user = authenticate(email_usuario=email, password=senha)
            if not user:
                raise forms.ValidationError("Email ou senha incorretos.")
        return cleaned_data

class NoticiaForm(forms.ModelForm):
    class Meta:
        model = Noticia
        exclude = ['usuario', 'categoria']  # <--- Exclui o campo do formulário
        widgets = {
            'descricao': forms.TextInput(attrs={'class': 'form-control flex flex-col border rounded-md px-2 py-1 border-gray-500', 'placeholder': 'Breve descrição'}),
            'introducao': forms.Textarea(attrs={'class': 'form-control flex flex-col border rounded-md px-2 py-1 border-gray-500', 'rows': 3}),
            'desenvolvimento_inicial': forms.Textarea(attrs={'class': 'form-control flex flex-col px-2 py-1 border rounded-md border-gray-500', 'rows': 4}),
            'desenvolvimento_final': forms.Textarea(attrs={'class': 'form-control flex flex-col px-2 py-1 border rounded-md border-gray-500', 'rows': 4}),
            'conclusao': forms.Textarea(attrs={'class': 'form-control flex flex-col border px-2 py-1 rounded-md border-gray-500', 'rows': 3}),
            'video': forms.TextInput(attrs={'class': 'form-control flex flex-col border-b px-2 py-1', 'placeholder': 'Cole o link do YouTube'}),
        }