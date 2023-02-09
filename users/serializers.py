from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.utils.translation import gettext_lazy as _
from rest_framework_simplejwt.tokens import RefreshToken


from .models import User
from rest_framework.validators import UniqueValidator
from django.core.validators import RegexValidator
from django.contrib.auth.password_validation import validate_password


class UserDataSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('email','first_name', 'last_name', 'mobile_number', 'id',)
        read_only_fields = ('updated_at','created_at',)


class UserUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        exclude = ('updated_at','created_at','is_staff', 'is_active','password','is_superuser',
                   'last_login',)


class UserRegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(write_only=True,required=True,validators=[UniqueValidator(queryset=User.objects.all())])
    first_name = serializers.CharField(write_only=True,required=True)
    last_name = serializers.CharField(write_only=True,required=True)
    mobile_number = serializers.CharField(validators=[RegexValidator(r'^(\+|)\d{10,13}$')])
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password_confirmation = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = (
            'email',
            'first_name',
            'last_name',
            'mobile_number',
            'password',
            'password_confirmation',
        )

    def validate(self, data):
        """Verify passwords match."""
        passwd = data['password']
        passwd_conf = data['password_confirmation']
        if passwd != passwd_conf:
            raise serializers.ValidationError("Passwords don't match.")
        validate_password(passwd)
        return data

    def create(self, data):
        """Handle user and profile creation."""
        data.pop('password_confirmation')
        user = User.objects.create_user(**data)
        return user



class LoginSerializer(TokenObtainPairSerializer):
    default_error_messages = {
        "no_active_account": _("Usuario o contraseña incorrectos")
    }

    token_class = RefreshToken

    def validate(self, data):
        data_ = super().validate(data)
        data_['user'] = UserDataSerializer(self.user).data
        # token = self.get_token(self.user)
        # print(token)
        # data["token"] = str(token)
        return data_
