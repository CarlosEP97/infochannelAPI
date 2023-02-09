from django.urls import path,re_path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import *


app_name = 'user'

urlpatterns = [
    path('auth/token/', LoginView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('signup/',UserRegister.as_view(), name = 'signup_user'),
    path('logout/',LogoutView.as_view(), name = 'logout_user'),
    path('detail/',UserRetrieveAndUpdateData.as_view(),name = 'user_retrieve'),

]