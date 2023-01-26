from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from django.urls import reverse
from rest_framework import status
from .models  import Player
from .serializers import PlayerSerializer , updatePlayerSerializer

TAGS_URL1 = reverse('player:list-players-create')
TAGS_URL3 = reverse('player:detail-update-delete-players', kwargs={'pk':1})


class Modeltest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth(self):
        res = self.client.get(TAGS_URL1)
        self.assertEqual(res.status_code,status.HTTP_401_UNAUTHORIZED)


class test_list_players(TestCase):

    def setUp(self):
        self.user = get_user_model().objects.create(
            username='dranza',
            password='password'
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_list(self):
        response = self.client.get(TAGS_URL1)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data['results'],list)



class test_create_player(TestCase):

    def setUp(self):
        self.user = get_user_model().objects.create(
            username='dranza34',
            password='password'
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

        self.player_data = {
            'user': self.user, 'name': 'playerdemo43',
            'long': -74.128540, 'lat': 4.712556
        }

    def test_create_auth_user(self):
        response = self.client.post(TAGS_URL1, self.player_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        player = Player.objects.get(pk=response.data['id'])
        serializer = PlayerSerializer(player)
        self.assertEqual(response.data, serializer.data)

    def tearDown(self):
        Player.objects.filter(**self.player_data).delete()


class test_retrieve_update_delete_players(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create(
            username='dranza34',
            password='password'
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

        self.player_data = {
            'user': self.user, 'name': 'playerdemo43',
            'long': -74.128540, 'lat': 4.712556
        }


    def test_Retrieve_player(self):
        response = self.client.post(TAGS_URL1, self.player_data)
        # self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        res=self.client.get(reverse('player:detail-update-delete-players', kwargs={'pk': response.data['id']}))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        retrieve = Player.objects.get(pk=res.data['id'])
        self.assertEqual(retrieve.name, res.data['name'])


    def test_update_player(self):
        response = self.client.post(TAGS_URL1, self.player_data)
        # self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        res = (reverse('player:detail-update-delete-players', kwargs={'pk': response.data['id']}))
        u = {'name': 'playerdemoUpdate997'}
        res1 = self.client.put(res,u)
        self.assertEqual(res1.status_code, status.HTTP_200_OK)
        update = Player.objects.get(pk=res1.data['id'])
        self.assertEqual(update.name, u['name'])

    def test_delete_player(self):
        response = self.client.post(TAGS_URL1, self.player_data)
        prev_db_count = Player.objects.all().count()
        self.assertGreater(prev_db_count,0)
        self.assertEqual(prev_db_count,1)
        response = self.client.delete((reverse('player:detail-update-delete-players', kwargs={'pk': response.data['id']})))
        self.assertEqual(response.status_code,status.HTTP_204_NO_CONTENT)

#
#
class ModeltestNoAuth(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth(self):
        res = self.client.get(TAGS_URL1)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_UNauth_user(self):
        p = {'user': self.client,'name': 'playerdemo43','long':-74.128540,'lat':4.712556}
        response = self.client.post(TAGS_URL1,p)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)