from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from django.core.files import File
from django.urls import reverse
from rest_framework import status
from .models import *
from resources.models import Resource
from .serializers import *

# Create your tests here.

add_files = reverse('campaign:add-playlist', kwargs={'playlist_id':2})
Campaign_create = reverse('campaign:Campaign')

class Layouts(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create(
            username='dranza',
            password='password'
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

        self.campaign_data = {'user': self.user, 'campaign_name' : 'Prueba1', 'screen_orientation': 10,
                              'width': 1920 , 'height': 1080}

        self.timelines_data = {'campaign': self.campaign_data , 'timeline_name': 'attachToPrueba1',
                               'play_options': 10}

        self.layouts_data = {'timelines': self.timelines_data , 'name': 'attachToPrueba1'}

    def  test_PlaylistAddfile_view(self):
        response = self.client.post(Campaign_create, self.campaign_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        #test signal
        self.assertEqual(Timelines.objects.count(), 1)
        self.assertEqual(Playlist.objects.count(), 1)

    def test_signal(self):
        # Create a Campaigns instance to use as the sender
        campaign = Campaigns.objects.create(user = self.user,campaign_name='Test Campaign', width=640, height=480, screen_orientation= 10)
        # # Call the signal's send method directly
        # campaign_timelines_playlist_set.send(sender=campaign, created=True)


        # Get the created Timelines and Playlist instances
        timeline = Timelines.objects.get(campaign=campaign)
        playlist = Playlist.objects.get(timelines=timeline)

        # Test that the width and height of the Playlist instance match the campaign's width and height
        self.assertEqual(playlist.width, campaign.width)
        self.assertEqual(playlist.height, campaign.height)

    def test_resource_position(self):
        campaign = Campaigns.objects.create(user=self.user, campaign_name='Test Campaign', width=640, height=480,
                                            screen_orientation=10)
        timeline = Timelines.objects.get(campaign=campaign)
        playlist = Playlist.objects.get(timelines=timeline)

        #Create a resource
        f = File(open('media/cared/gohan.jpg', 'rb'))
        r = [{'user': self.user, 'name': 'sdadsad1', 'files': f},
             {'user': self.user, 'name': 'sdadsad2', 'files': f},
             {'user': self.user, 'name': 'sdadsad3', 'files': f}]

        for i in r:
            Resource.objects.create(**i)

        # add resource to a playlist
        ids = {'pk_ids': [1, 2, 3]}
        while ids:
            if not ids['pk_ids']:
                break
            pk_ids = ids['pk_ids'].pop(0)
            post_response = self.client.post(add_files, {'pk_ids':pk_ids})
        print(post_response.data)
        r_position = AddFiles.objects.filter(playlist=playlist, resource__pk__in=[1, 2, 3])
        # print(r_position.values_list('pk'))

        #update position
        update_response = self.client.put(add_files,{'resource_id': ['2'], 'position': ['1']})
        # print(update_response.data)

        #delete a element

        delete_response = self.client.delete(add_files,{'resource_id': ['3']})
        print(delete_response.data)

        self.assertEqual(playlist.resources.count(), 3)
        self.assertEqual( AddFiles.objects.filter(playlist = playlist).values_list('position','resource')  , 0)
