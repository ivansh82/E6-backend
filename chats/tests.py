from django.test import TestCase
from django.contrib.auth.models import User
from .models import Chat, Message

class ChatsTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create a user
        testuser1 = User.objects.create_user(
        username='testuser1', password='abc123')
        testuser1.save()
        # Create a chat
        list_users = []
        list_users.append(testuser1)
        test_chat = Chat.objects.create(
        title='Chat title', owner=testuser1)
        test_chat.save()
        # Create a chat
        test_message = Message.objects.create(
        author=testuser1, chat=test_chat, content='test content')
        test_message.save()

    def test_chat_content(self):
        post = Chat.objects.get(id=1)
        owner = f'{post.owner}'
        title = f'{post.title}'
        message = Message.objects.get(id=1)
        author = f'{message.author}'
        chat = f'{message.chat}'
        body = f'{message.content}'

        self.assertEqual(owner, 'testuser1')
        self.assertEqual(title, 'Chat title')
        self.assertEqual(author, 'testuser1')
        self.assertEqual(chat, 'Chat title')
        self.assertEqual(body, 'test content')