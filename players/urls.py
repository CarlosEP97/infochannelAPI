from django.urls import path
from . import views

app_name = 'player'

urlpatterns = [
    path('list/', views.Playerlist.as_view(http_method_names =['get','post']), name='list-players-create'),
    path('<int:pk>/detail/', views.PlayerRetrieveUpdateDestroy.as_view(http_method_names =['get','put','delete']),
         name='detail-update-delete-players'),
]
