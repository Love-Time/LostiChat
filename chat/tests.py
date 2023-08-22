from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status

from chat.serializers import DialogSerializer

User = get_user_model()
# Create your tests here.
from rest_framework.test import APITestCase
from chat.models import Dialog
class LastMessagetests(APITestCase):
    def setUp(self):
        user_1 = User.objects.create_user(email='user1@mail.ru', password="123456")
        user_2 = User.objects.create_user(email='user2@mail.ru', password="123456")
        user_3 = User.objects.create_user(email='user3@mail.ru', password="123456")
        self.msgs = []
        for i in range(3):
            for j in range(3):
                msg = Dialog(sender_id=i+1, recipient_id=j+1, message = f'{i+1}_{j+1}')
                msg.save()
                self.msgs.append(msg)


    def test_last_message(self):
        responce = self.client.post('/api/v1/token/', {'email':'user1@mail.ru', 'password': '123456'}, type='json')
        self.assertEqual(responce.status_code, status.HTTP_200_OK)
        self.client.credentials(HTTP_AUTHORIZATION="JWT " + responce.data['access'] )
        responce2 = self.client.get("/api/v1/dialogs/")
        messages_answer = responce2.data
        messages_test = DialogSerializer([self.msgs[6], self.msgs[3], self.msgs[0]], many=True).data

        self.assertEqual(messages_answer, messages_test)


