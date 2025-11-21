from django.contrib.auth.base_user import BaseUserManager

class UsuarioManager(BaseUserManager):
    def create_user(self, email_usuario, nome_usuario, senha_usuario=None, perfil=1, **extra_fields):
        if not email_usuario:
            raise ValueError('O email é obrigatório.')

        email_usuario = self.normalize_email(email_usuario)
        usuario = self.model(
            email_usuario=email_usuario,
            nome_usuario=nome_usuario,
            perfil=perfil,
            **extra_fields
        )
        usuario.set_password(senha_usuario)
        usuario.save(using=self._db)
        return usuario

    def create_editor(self, email_usuario, nome_usuario, senha_usuario=None, **extra_fields):
        extra_fields.setdefault('perfil', 2)
        return self.create_user(email_usuario, nome_usuario, senha_usuario, **extra_fields)

    def create_superuser(self, email_usuario, nome_usuario, senha_usuario=None, **extra_fields):
        extra_fields.setdefault('perfil', 3)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(email_usuario, nome_usuario, senha_usuario, **extra_fields)
