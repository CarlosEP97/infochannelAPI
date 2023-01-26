from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin , BaseUserManager
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator
from django.utils import timezone


class UserManager(BaseUserManager):

    def create_user(self,email,first_name,last_name,password=None,**kwargs):
        email = self.normalize_email(email)
        user = self.model(email = email, first_name = first_name,
                          last_name = last_name,**kwargs)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self,**kwargs):
        user = self.create_user(**kwargs)
        user.is_staff = True
        user.is_superuser = True
        user.save()
        return user


class User(AbstractBaseUser,PermissionsMixin):

    email = models.EmailField(
        unique=True,
        verbose_name=_('correo electrónico'),
        help_text=_('Correo electrónico'),
    )

    first_name = models.CharField(
        max_length=128,
        verbose_name=_('nombre'),
        help_text=_('Nombre'),
    )

    last_name = models.CharField(
        max_length=128,
        verbose_name=_('apellido'),
        help_text=_('Apellidos'),
    )

    mobile_number = models.CharField(
        max_length=13,
        verbose_name=_('número celular'),
        validators=[RegexValidator(r'^(\+|)\d{10,13}$')],
        help_text=_('Número de celular.'),
        blank=True,
        null=True
    )

    is_staff = models.BooleanField(
        default=False,
        verbose_name=_('operador'),
        help_text=_('Indica si puede entrar al panel de administrador'),
    )


    is_active = models.BooleanField(
        default=True,
        verbose_name=_('activo'),
        help_text=_('Indica si el usuario puede ingresar a la plataforma.'),
    )


    updated_at = models.DateTimeField(
        verbose_name=_('fecha de actualización'),
        auto_now=True,
        editable=False,
        help_text=_('Muestra la fecha de actualización'),
    )

    created_at = models.DateTimeField(
        default=timezone.now,
        verbose_name=_('fecha de registro'),
        editable=False,
        help_text=_('Muestra la fecha de creación.'),
    )

    objects = UserManager()

    USERNAME_FIELD = 'email'

    REQUIRED_FIELDS = ['first_name', 'last_name']


    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name}'

    class Meta:
        ordering = ['-id']
        verbose_name = _('usuario')
        verbose_name_plural = _('usuarios')
