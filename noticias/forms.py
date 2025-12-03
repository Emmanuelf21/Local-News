from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate
from .models import Noticia, Perfil

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
        usuario.perfil = Perfil.objects.get(id=1)  # ou o valor correspondente ao perfil padrão no seu modelo

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
        exclude = ['usuario', 'categoria']

        base_input = (
            "w-full border border-gray-300 rounded-lg px-3 py-2 shadow-sm "
            "focus:ring-2 focus:ring-blue-500 focus:outline-none transition "
            "hover:border-blue-400"
        )

        # SVG do select
        select_arrow = (
            "background-image:url('data:image/svg+xml;utf8,"
            "<svg fill=\"%23666\" height=\"24\" viewBox=\"0 0 24 24\" width=\"24\" "
            "xmlns=\"http://www.w3.org/2000/svg\">"
            "<path d=\"M7 10l5 5 5-5z\"/></svg>'); "
            "background-repeat:no-repeat; background-position:right .7rem center; "
        )

        widgets = {

            # SELECT: Tema
            'tema': forms.Select(attrs={
                'class': base_input + " bg-white appearance-none pr-10 cursor-pointer",
                'style': select_arrow,
            }),

            # SELECT: Bairro
            'bairro': forms.Select(attrs={
                'class': base_input + " bg-white appearance-none pr-10 cursor-pointer",
                'style': select_arrow,
            }),
            'titulo': forms.TextInput(attrs={
                'class': base_input,
                'placeholder': 'Título da notícia...',
            }),
            # INPUTS E TEXTAREAS
            'descricao': forms.TextInput(attrs={
                'class': base_input,
                'placeholder': 'Breve descrição...',
            }),
            'introducao': forms.Textarea(attrs={
                'class': base_input,
                'rows': 3
            }),
            'desenvolvimento_inicial': forms.Textarea(attrs={
                'class': base_input,
                'rows': 4
            }),
            'desenvolvimento_final': forms.Textarea(attrs={
                'class': base_input,
                'rows': 4
            }),
            'conclusao': forms.Textarea(attrs={
                'class': base_input,
                'rows': 3
            }),
            'video': forms.TextInput(attrs={
                'class': base_input,
                'placeholder': 'Link do YouTube'
            }),

            # FILE INPUT - estilizado
            'image': forms.FileInput(attrs={
                'class': (
                    "mt-1 block w-full text-sm text-gray-700 cursor-pointer "
                    "file:mr-4 file:py-2 file:px-4 file:rounded-lg "
                    "file:border-0 file:text-sm file:font-semibold "
                    "file:bg-blue-600 file:text-white hover:file:bg-blue-700 "
                    "hover:border-blue-400"
                )
            }),
        }
