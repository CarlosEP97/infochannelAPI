from django.core.exceptions import ObjectDoesNotExist
from rest_framework.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from rest_framework.response import Response
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenViewBase

from .serializers import UserDataSerializer, UserRegisterSerializer,LoginSerializer,UserUpdateSerializer

from rest_framework import generics, mixins
from rest_framework.permissions import AllowAny, IsAuthenticated

from rest_framework import status

from .models import User


class UserRegister(generics.GenericAPIView):
    permission_classes = (AllowAny,)
    serializer_class = UserRegisterSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data = request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        data = UserDataSerializer(user).data
        return Response(data,status.HTTP_201_CREATED)


class LoginView(TokenViewBase):

    permission_classes = (AllowAny,)
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            raise ValidationError(_("Nombre de usuario o contraseña incorrecta."))



class LogoutView(generics.GenericAPIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            user = self.request.user
            if user is None:
                raise ValidationError(_('No se ha ingresado ningun usuario'))

            refresh_token = request.data.get("refresh_token", '')
            if refresh_token == '':
                raise ValidationError('no se envió refresh_token')
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({}, status=status.HTTP_200_OK)
        except ValidationError as e:
            return Response({"error": e.detail}, status=status.HTTP_400_BAD_REQUEST)

class LogoutAllView(generics.GenericAPIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        tokens = OutstandingToken.objects.filter(user_id=request.user.id)
        for token in tokens:
            t, _ = BlacklistedToken.objects.get_or_create(token=token)

        return Response(status=status.HTTP_205_RESET_CONTENT)



class UserRetrieveAndUpdateData(generics.RetrieveUpdateAPIView):

    permission_classes = (IsAuthenticated,)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return UserDataSerializer
        else:
            return UserUpdateSerializer

    def get_object(self):
        user = self.request.user
        if user:
            get_user = User.objects.get(pk=user.pk)
            return get_user

    def put(self, request, *args, **kwargs):
        user = self.get_object()
        if user:
            serializer = self.get_serializer(user,data = request.data, partial = True)
            serializer.is_valid(raise_exception = True)
            serializer.save()
            print(serializer.data)
            data = self.get_serializer(user).data
        return Response(data, status = status.HTTP_200_OK)




