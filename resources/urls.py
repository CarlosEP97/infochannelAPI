from django.urls import path,re_path
from . import views

app_name = 'resource'

urlpatterns = [
    path('list/', views.ResourcesList.as_view(), name='list-create-resources'),
    path('delete/', views.ResourcesDestroy.as_view(), name='delete-resources'),
    path('<int:pk>/edit/', views.ResourcesRetrieve.as_view(), name='detail-update-resources'),
    path('<int:pk>/download/', views.FilesDownload.as_view(), name='download-resources'),

]