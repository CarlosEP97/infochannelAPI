from django.urls import path, re_path
from . import views


app_name = 'campaign'

urlpatterns = [
    path('search/',views.SearchPlaylist.as_view(),name = 'search'),

    path('list/', views.Campaign.as_view(), name='Campaign'),
    path('<int:pk>/', views.CampaignRetrieve.as_view(), name='Campaign-detail'),
    path('<int:pk>/timelines/', views.CampaignTimelines.as_view(http_method_names=['get', 'post', 'put', 'delete']),
         name='Campaign-timelines'),
    path('timeline/<int:pk>/', views.TimelineDetail.as_view(), name='Campaign-detail'),
    path('timeline/<pk>/layout/', views.TimelinesLayouts.as_view(http_method_names=['get', 'post']),
         name='Timelines-layouts'),
    path('layout/<int:pk>/', views.Layouts.as_view(http_method_names=['get', 'put','delete']), name='layout-detail'),

    re_path(r'^playlist/(?P<playlist_id>[0-9]+)/add/$', views.PlaylistAddfile.as_view(
        http_method_names=['post', 'put', 'delete']), name='add-playlist'),

    re_path(r'^playlist/(?P<playlist_id>[0-9]+)/random/$', views.RandomOrder.as_view(
        http_method_names=['put']), name='random-playlist'),

]