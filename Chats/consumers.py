import asyncio
import json
import redis
from asgiref.sync import async_to_sync, sync_to_async
from channels.consumer import SyncConsumer, AsyncConsumer
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer, JsonWebsocketConsumer, AsyncJsonWebsocketConsumer
from django.contrib.auth.models import User

from Users.models import Users
from .models import Thread, ChatMessage, ThreadMember
from django.core.asgi import get_asgi_application
import redis
from django.conf import settings

REDIS_HOST = 'localhost'
REDIS_PORT = 6379

redis_client = redis.StrictRedis(host=REDIS_HOST,
                                 port=REDIS_PORT, db=0)


class ChatConsumer(AsyncConsumer):
    group = 'AllMembers'
    count = 0
    KEY_ONLINE_USERS = 'OnlineList'

    async def websocket_connect(self, event):
        current_user = self.scope['user']

        self.makeOnline(current_user.username)

        thread_object = await self.getCurrentTread()

        self.chat_room = f'thread_{thread_object.id}'
        print('chat_room', self.chat_room)
        await self.channel_layer.group_add(self.chat_room, self.channel_name)

        onlineCount = self.getOnlinesCount()
        onlineList = self.getOnlineUsers()

        await self.channel_layer.group_send(self.chat_room, {
            'type': 'send_updates',
            'id': await self.getSenderId(),
            'username': await self.getSenderUsername(),
            'onlineList': onlineList,
            'onlineCount': onlineCount
        })

        await self.send({
            "type": "websocket.accept"
        })

    async def send_updates(self, event):
        await self.send({
            "text": json.dumps(event),
            "type": "websocket.send"
        })

    async def websocket_receive(self, event):


        # print('eveeeeent',event)
        jsonText = json.loads(event['text'])
        event_type = jsonText['type']

        if event_type == 'text':
            json_data = {
                "text": jsonText['text'],
                "username": await self.getSenderUsername(),
                "type": "chat_message"
            }
            senderId = await self.getSenderId()
            currentThread = await self.getCurrentTread()
            print('crr', self.chat_room, json_data)
            await self.channel_layer.group_add(self.chat_room, self.channel_name)
            await self.channel_layer.group_send(self.chat_room, json_data)
            await self.create_chat_message(senderId, jsonText['text'], currentThread)
            print('after')
        elif event_type == 'update_thread':
            thread_id = jsonText['thread_id']
            self.chat_room = f'thread_{thread_id}'


    async def websocket_disconnect(self, event):
        print("disconnected", event)
        self.makeOffline(await self.getSenderUsername())


    async def chat_message(self, event):
        print('message -> ', event)
        await self.send({
            "text": json.dumps({
                "message": event["text"],
                "username": event["username"],
                "type": "new_message"
            }),
            "type": "websocket.send"
        })

    def makeOnline(self, username):
        try:
            if not self.checkOnlineUser(username):
                redis_client.lpush(self.KEY_ONLINE_USERS, username)
        except Exception as ex:
            print(f'The Error in makeOnline function : {ex}')
        

    def makeOffline(self, username):
        redis_client.lrem(self.KEY_ONLINE_USERS, 1, username)

    def checkOnlineUser(self, username):
        userList = self.getOnlineUsers()
        return username in userList

    def getOnlineUsers(self):
        user_list = []
        while redis_client.llen(self.KEY_ONLINE_USERS) != 0:
            user_list.append(str(redis_client.lpop(self.KEY_ONLINE_USERS).decode()))

        for username in user_list:
            redis_client.lpush(self.KEY_ONLINE_USERS, username)

        return user_list

    def getOnlinesCount(self):
        return redis_client.llen(self.KEY_ONLINE_USERS)

    @sync_to_async
    def getSenderId(self):
        user = self.scope['user']
        if user.is_authenticated:
            userId = user.id
        else:
            userId = 1
        return userId

    @sync_to_async
    def getSenderUsername(self):
        user = self.scope['user']
        if user.is_authenticated:
            userId = user.username
        else:
            userId = "Nilufar"
        return userId

    @sync_to_async
    def getCurrentTread(self):
        try:
            thread_id = self.chat_room.replace("thread_", "")
            # print(self.scope['query_string'])
            # if 'thread_id' in self.scope['url_route']['kwargs']:
            #     thread_id = self.scope['url_route']['kwargs']['thread_id']
            #     print('getCurrentTread -> thread_id', thread_id)
            thread_nil = Thread.objects.get(id=int(thread_id))
            return thread_nil
        except Exception as ex:
            print(f'Error in getCurrentTread {str(ex)}')
        return Thread.objects.get(id=int(1))



    @database_sync_to_async
    def create_chat_message(self, sender, message, thread):
        try:
            chat = ChatMessage.objects.create(thread=thread, user=Users.objects.get(id=sender), message=message)
            chat.save()
            return True
        except Exception as e:
            print("Error saving chat!", e)
            return False

    async def connect(self):
        pass

# async def websocket_receive(self, event):
#     print("receive", event)
#     fronText = event.get('text', None)
#     if fronText is not None:
#         loaded_dict_data = json.loads(fronText)
#         msg = loaded_dict_data.get('message')
#         # print(msg)
#         # await self.send({
#         #     "type":"websocket.send",
#         #     "text":msg,
#         # })
#         user = self.scope['user']
#         # print('user ->', user)
#         # print('username ->', user.username)
#         # print('authentication ->', user.is_authenticated)
#         if user.is_authenticated:
#             username = user.username
#         else:
#             username = 'NilaUser'
#
#         myResponse = {
#             'message': msg,
#             'username': username
#         }
#
#
#
#         # new_event = {"type":"websocket.send",
#         #              "text":json.dumps((myResponse))}
#         #
#
#         await self.channel_layer.group_send(
#             self.chat_room,
#             {
#                 "type": "chat_message",
#                 "text": json.dumps(myResponse)
#             }
#         )
#         print('response->', myResponse)
#         # finalResponse = json.dumps(myResponse)
#         # print('finalResponse->', finalResponse)
#         # await self.send(finalResponse)
# chat_method is a custom method name that we made
# async def chat_message(self, event):
#     # sends the actual message
#     await self.send({
#         'type': 'websocket.send',
#         'text': event['text']
#     })

#
#     def fetch_chats(self, data):
#         chats = Chats.last_20_messages(self.room_name)
#         content = {
#             'command': 'Chats',
#             'messages': self.messages_to_json(messages)
#         }
#         self.send_message(content)
#
#     # Please send a new message for me
#     def new_message(self, data):
#         author = data['from']
#         author_user = Users.objects.filter(username=author)[0]
#         message = Chats.objects.create(
#             author=author_user,
#             content=data['message'],
#             room_name=self.room_name, )
#         content = {
#             'command': 'new_message',
#             'message': self.message_to_json(message)
#         }
#         return self.send_chat_message(content)
#
#     def chats_to_json(self, Chats):
#         Chats_json = []
#         for Chat in Chats:
#             Chats_json.append(self.message_to_json(Chat))
#         return Chats_json
#
#     def chat_to_json(self, Chat):
#         return {
#             'author': Chat.author.username,
#             'content': Chat.content,
#             'timestamp': Chat.created_at.isoformat(),
#         }
#
#     commands = {
#         'fetch_messages': fetch_chats,
#         'new_message': new_message
#     }
#
#     # Receive message from WebSocket
#
#     # def receive(self, *, text_data):
#     #     if text_data.startswith("/name"):
#     #         self.username = text_data[5:].strip()
#     #         self.send(text_data="[set your username to %s]" % self.username)
#     #     else:
#     #         self.send(text_data=self.username + ": " + text_data)
#
#     def send_chat_message(self, message):
#         # Send message to room group
#         async_to_sync(self.channel_layer.group_send)(
#             self.room_group_name,
#             {
#                 'type': 'chat_message',
#                 'message': message
#             }
#         )
#
#     def send_message(self, message):
#         self.send(text_data=json.dumps(message))
#
#     # Receive message from room group
#     def chat_message(self, event):
#         message = event['message']
#         self.send(text_data=json.dumps(message))
#
# #
# #
# # class ChatConsumer(WebsocketConsumer):
# #     # Load previous messages from database
# #     def fetch_messages(self, data):
# #         messages = Message.last_20_messages(self.room_name)
# #         content = {
# #             'command': 'messages',
# #             'messages': self.messages_to_json(messages)
# #         }
# #         self.send_message(content)
# #
# #     def new_message(self, data):
# #         author = data['from']
# #         author_user = User.objects.filter(username=author)[0]
# #         message = Message.objects.create(
# #             author=author_user,
# #             content=data['message'],
# #             room_name = self.room_name,)
# #         content = {
# #             'command': 'new_message',
# #             'message': self.message_to_json(message)
# #         }
# #         return self.send_chat_message(content)
# #
# #     def messages_to_json(self, messages):
# #         messages_json = []
# #         for message in messages:
# #             messages_json.append(self.message_to_json(message))
# #         return messages_json
# #
# #     def message_to_json(self, message):
# #         return {
# #             'author': message.author.username,
# #             'content': message.content,
# #             'timestamp': message.timestamp.isoformat(),
# #         }
# #
# #     # Choose the command
# #     commands = {
# #         'fetch_messages': fetch_messages,
# #         'new_message': new_message
# #     }
# #
# #     def connect(self):
# #         self.room_name = self.scope['url_route']['kwargs']['room_name']
# #         self.room_group_name = 'chat_%s' % self.room_name
# #
# #         # Join room group
# #         async_to_sync(self.channel_layer.group_add)(
# #             self.room_group_name,
# #             self.channel_name
# #         )
# #
# #         self.accept()
# #
# #     def disconnect(self, close_code):
# #         # Leave room group
# #         async_to_sync(self.channel_layer.group_discard)(
# #             self.room_group_name,
# #             self.channel_name
# #         )
# #
# #
# #     # Receive message from WebSocket
# #     def receive(self, text_data):
# #         data = json.loads(text_data)
# #         self.commands[data['command']](self, data)
# #
# #     def send_chat_message(self, message):
# #         # Send message to room group
# #         async_to_sync(self.channel_layer.group_send)(
# #             self.room_group_name,
# #             {
# #                 'type': 'chat_message',
# #                 'message': message
# #             }
# #         )
# #
# #     def send_message(self, message):
# #         self.send(text_data=json.dumps(message))
# #
# #     # Receive message from room group
# #     def chat_message(self, event):
# #         message = event['message']
# #         self.send(text_data=json.dumps(message))
# #
# #
