from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from django.urls import reverse
from rest_framework import status
from django.core.files import File
from .models import Resource
from .serializers import ResourceSerializer


TAGS_URL = reverse('resource:list-create-resources')

class Modeltest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth(self):
        res = self.client.get(TAGS_URL)
        self.assertEqual(res.status_code,status.HTTP_401_UNAUTHORIZED)


class test_list_resouces(TestCase):

    def setUp(self):
        self.user = get_user_model().objects.create(
            username='dranza',
            password='password'
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)
#
    def test_create_auth_user(self):
        f = File(open('media/cared/gohan.jpg', 'rb'))
        r = {'user':self.user,'name': 'sdadsad', 'files':f}
        res = self.client.post(TAGS_URL,r)
        resour = Resource.objects.all()
        serializer = ResourceSerializer(resour, many=True)
        print(serializer.data)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        # self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assert_(res.data,serializer.data)

    def test_list(self):
        response = self.client.get(TAGS_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data['results'],list)



class ModeltestNoAuth(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth(self):
        res = self.client.get(TAGS_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_UNauth_user(self):
        f = File(open('media/cared/KqDKO.jpg', 'rb'))
        r = {'user': self.client, 'name': 'sdadsad', 'files': f}
        response = self.client.post(TAGS_URL,r)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
