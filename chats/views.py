from django.contrib.auth import get_user_model
# from django.http.multipartparser import MultiPartParser
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import viewsets, permissions, generics # new
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import Http404
from .models import Chat, Message, ProfileData
from .permissions import IsUserOrReadOnly, IsOwnerOrReadOnly
from .serializers import ChatSerializer, MessageSerializer, UserSerializer, ProfileDataSerializer, \
    PrivateChatSerializer  # , ChatUserSerializer, PrivateChatSerializer
from rest_framework import status
import json

class ChatJoinViewSet(APIView):
    permissions_classes = (permissions.IsAuthenticated,)
    # serializer_class = ChatUserSerializer

    def get_object(self, pk):
        try:
            return Chat.objects.get(pk=pk)
        except Chat.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        chat = self.get_object(pk)
        messages = Message.objects.filter(chat__id=pk)
        if request.user in chat.chat_users.all():
            pass
        else:
            chat.chat_users.add(request.user)

        listOfMessage = []
        for item in messages:
            dictMessage = {'author': item.author.username, 'author_id':item.author.pk, 'date_posted': item.date_posted.strftime("%d-%m-%Y %H:%M:%S"), 'content': item.content}
            listOfMessage.append(dictMessage)

        listMembers = []
        for usr in chat.chat_users.all():
            listMembers.append({'id': usr.id, 'username': usr.username})

        dictResponse = {'chat': pk, 'title': chat.title, 'chat_users': listMembers, 'messages': listOfMessage}

        return Response(dictResponse)

class ChatViewSet(viewsets.ModelViewSet): # new
    permission_classes = (permissions.IsAuthenticated,)
    queryset = Chat.objects.all()
    serializer_class = ChatSerializer

    def perform_create(self, serializer):
        # here you will send `created_by` in the `validated_data`
        strData = json.dumps(self.request.data)
        data = json.loads(strData)
        if not data['private']:
            first_member_list = []
            first_member_list.append(self.request.user)
            serializer.save(owner=self.request.user, chat_users = first_member_list)
        else:
            first_member_list = []
            users = get_user_model()
            for userID in data['chat_users']:
                first_member_list.append(users.objects.get(pk=int(userID)))
            serializer.save(owner=self.request.user, chat_users = first_member_list)

class PrivateChatViewSet(viewsets.ModelViewSet): # new
    permission_classes = (IsOwnerOrReadOnly, permissions.IsAuthenticated,)
    queryset = Chat.objects.all()
    serializer_class = PrivateChatSerializer
    lookup_field = 'title'

    def perform_create(self, serializer):
        # here you will send `created_by` in the `validated_data`
        first_member_list = []
        first_member_list.append(self.request.user)
        serializer.save(owner=self.request.user, chat_users = first_member_list)

class MessageViewSet(viewsets.ModelViewSet): # new
    permission_classes = (permissions.IsAuthenticated,)
    queryset = Message.objects.all()
    serializer_class = MessageSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

class UserViewSet(viewsets.ModelViewSet): # new
    permission_classes = (IsUserOrReadOnly, permissions.IsAuthenticated,)
    queryset = get_user_model().objects.all()
    serializer_class = UserSerializer

class ProfileDataViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    queryset = ProfileData.objects.all()
    serializer_class = ProfileDataSerializer
    lookup_field = 'owner'

class UserAvatarUpload(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    parser_classes = [MultiPartParser, FormParser]
    serializer_class = ProfileDataSerializer

    def post(self, request, format=None):
        serializer = ProfileDataSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def perform_create(self, serializer):
        # here you will send `created_by` in the `validated_data`
        serializer.save(owner=self.request.user)
